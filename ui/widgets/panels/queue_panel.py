from typing import Protocol, runtime_checkable
 
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
 
from ui.widgets.download_card import DownloadCard
from ui.protocols.tasks import QueueTaskProtocol as QueueTask

_ACTIVE_STATUSES = {"pending", "running", "paused", "error"}
_REMOVE_STATUSES = {"completed", "cancelled"}
_REMOVE_DELAY_MS = 3_000

class QueuePanel(QWidget):
    """Aba da fila de dawnload

    Essa parte faz o gerenciamento DownloadCards: 

        Essa parte gerencia a criação de novas tarefas,
        atualizando a cada tick de polling e remoção com
        animação após conclusão ou cancelamento.

    Signals:
        cancel_requested(int): Emitido quando o usuário clica em cancelar
            em algum card. O receptor deve confirmar e, se confirmado,
            chamar `manager.cancel(task_id)`.
        status_changed(int, int, int): Emitido após cada refresh com
            (total, active, queued) para atualizar a status bar externa.
    """

    cancel_requested = Signal(int)
    status_changed = Signal(int, int, int)
    error_reported = Signal(int, str)

    POLL_INTERVAL_MS: int = 300

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cards: dict[int, DownloadCard] = {}
        self._pending_removal: set[int] = set()
        self._removed_terminal: set[int] = set()
        self._reported_errors: set[int] = set()
        self._build_ui()
        self._setup_timer()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0,0,0,0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QScrollArea.NoFrame)

        self._container = QWidget()
        self._container.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )

        self._cards_layout = QVBoxLayout(self._container)
        self._cards_layout.setSpacing(8)
        self._cards_layout.setContentsMargins(0, 4, 0, 4)
        self._cards_layout.setAlignment(Qt.AlignTop)

        self._empty_label = QLabel("Nenhum download na fila.\nCole uma URL acima para começar.")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setObjectName("subtitleLabel")
        self._empty_label.setVisible(True)
        self._cards_layout.addWidget(self._empty_label)
 
        self._scroll.setWidget(self._container)
        root.addWidget(self._scroll)

    def _setup_timer(self) -> None:
        self._time = QTimer(self)
        self._time.setInterval(self.POLL_INTERVAL_MS)
        self._time.timeout.connect(self.tick)
        self._poll_source: "ManagerProtocol | None" = None

    def start_polling(self, manager: "ManagerProtocol") -> None:
        self._poll_source = manager
        self._time.start()
        self.tick()

    def stop(self) -> None:
        self._time.stop()

    @Slot()
    def refresh(self, tasks: list[QueueTask]) -> None:
        # Alerta de não uso
        """Atualiza todos os cards com a lista de tarefas fornecida.
 
        Pode ser chamado diretamente pelo MainWindow além do polling
        interno, por exemplo após adicionar um novo download.
 
        Args:
            tasks: Lista completa de tarefas do manager.
        """
        self._update_cards(tasks)
        self._emit_status(tasks)
    
    @Slot()
    def tick(self) -> None:
        """Slot do timer: busca tarefas do manager e atualiza os cards."""
        if self._poll_source is None:
            return
        tasks = self._poll_source.list_tasks()
        self._update_cards(tasks)
        self._emit_status(tasks)

    def _update_cards(self, tasks: list[QueueTask]) -> None:
        """Cria, atualiza ou agenda remoção de cards conforme o estado.
 
        Args:
            tasks: Lista atual de tarefas do manager.
        """
        
        seen_ids: set[int] = set()
 
        for task in tasks:
            seen_ids.add(task.task_id)
            if task.status not in _REMOVE_STATUSES:
                self._removed_terminal.discard(task.task_id)
            if task.task_id in self._removed_terminal:
                continue
            if task.task_id in self._pending_removal:
                continue
            card = self._cards.get(task.task_id)
 
            if card is None:
                card = self._create_card(task)
  
            self._update_card(card, task)
            if (
                task.status == "error"
                and task.error_msg
                and task.task_id not in self._reported_errors
            ):
                self._reported_errors.add(task.task_id)
                self.error_reported.emit(task.task_id, task.error_msg)
            if task.status in _REMOVE_STATUSES:
                self._schedule_removal(task.task_id)

        self._removed_terminal.intersection_update(seen_ids)
 
        # Remove cards de tarefas que desapareceram completamente do manager
        ghost_ids = set(self._cards.keys()) - seen_ids - self._pending_removal
        for tid in ghost_ids:
            self._remove_card_now(tid)
 
        self._toggle_empty_label()

    def _create_card(self, task: QueueTask) -> DownloadCard:
        """Instancia um DownloadCard, conecta seus sinais e insere no layout.
 
        Args:
            task: Tarefa para a qual o card será criado.
 
        Returns:
            Card recém-criado já inserido no layout.
        """
        card = DownloadCard(task.task_id, task.url)
 
        card.cancel_btn.clicked.connect(
            lambda _checked=False, tid=task.task_id: self.cancel_requested.emit(tid)
        )
 
        # Insere antes do stretch (se houver) ou no final
        insert_pos = max(0, self._cards_layout.count() - 1)
        self._cards_layout.insertWidget(insert_pos, card)
        card.show()
 
        self._cards[task.task_id] = card
        return card

    @staticmethod
    def _update_card(card: DownloadCard, task: QueueTask) -> None:
        """Repassa os dados atuais da tarefa para o card.
 
        Args:
            card: Card a atualizar.
            task: Estado atual da tarefa.
        """
        card.update_progress(
            value=task.progress,
            status=task.status,
            speed=task.speed,
            eta=task.eta,
        )
 
        if task.status == "error" and task.error_msg:
            card.setToolTip(task.error_msg)
        else:
            card.setToolTip("")

    def _schedule_removal(self, task_id: int) -> None:
        """Agenda remoção do card após `_REMOVE_DELAY_MS` ms.
 
        O delay permite que o usuário veja o estado final antes
        do card desaparecer da fila.
 
        Args:
            task_id: ID da tarefa cujo card será removido.
        """
        if task_id in self._pending_removal:
            return
        self._pending_removal.add(task_id)
        QTimer.singleShot(
            _REMOVE_DELAY_MS,
            lambda: self._remove_card_now(task_id, mark_terminal=True),
        )

    def _remove_card_now(self, task_id: int, mark_terminal: bool = False) -> None:
        """Remove imediatamente o card do layout e libera sua memória.
 
        Args:
            task_id: ID da tarefa cujo card será destruído.
        """
        if mark_terminal:
            self._removed_terminal.add(task_id)

        card = self._cards.pop(task_id, None)
        self._pending_removal.discard(task_id)
 
        if card is None:
            return
 
        self._cards_layout.removeWidget(card)
        card.hide()
        card.deleteLater()
 
        self._toggle_empty_label()

    def _toggle_empty_label(self) -> None:
        """Exibe ou oculta o label de fila vazia conforme o número de cards."""
        has_cards = bool(self._cards)
        self._empty_label.setVisible(not has_cards)

    def _emit_status(self, tasks: list[QueueTask]) -> None:
        """Calcula os contadores e emite status_changed"""
        total = len(tasks)
        active = sum(1 for t in tasks if t.status == "running")
        queued  = sum(1 for t in tasks if t.status == "pending")
        self.status_changed.emit(total, active, queued)



@runtime_checkable
class ManagerProtocol(Protocol):
    """Interface mínima do ThreadManager que o QueuePanel usa no polling."""
 
    def list_tasks(self) -> list[QueueTask]: ...
