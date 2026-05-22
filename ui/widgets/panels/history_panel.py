import csv
from datetime import datetime

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.protocols.tasks import HistoryTaskProtocol as HistoryTask


# Colunas da tabela (índice → nome)
_COLUMNS = ["Título", "Status", "Tamanho", "Velocidade média", "Data", "Arquivo"]
_COL = {name: idx for idx, name in enumerate(_COLUMNS)}

# Status visíveis no painel (apenas terminais)
_TERMINAL_STATUSES = {"completed", "cancelled", "error"}

# Rótulos localizados de status
_STATUS_LABELS: dict[str, str] = {
    "completed": "Concluído",
    "cancelled":  "Cancelado",
    "error":      "Erro",
}


class HistoryPanel(QWidget):
    """Aba de histórico de downloads.

    Emite sinais para ações que exijam acesso ao ThreadManager

    Signals:
        clear_requested: Emitido quando o usuário confirma limpar o histórico.
            O receptor (MainWindow) deve chamar `refresh()` após a limpeza.
    """

    clear_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tasks: list[HistoryTask] = []
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        """Constrói o layout completo do painel."""
        layout = QVBoxLayout(self)

        # Barra de ações + filtro
        action_bar = QHBoxLayout()

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Filtrar por título ou URL…")
        self._search_input.setClearButtonEnabled(True)
        action_bar.addWidget(self._search_input, stretch=1)

        self._export_btn = QPushButton("Exportar CSV")
        self._export_btn.setObjectName("secondaryBtn")
        action_bar.addWidget(self._export_btn)

        self._clear_btn = QPushButton("Limpar histórico")
        self._clear_btn.setObjectName("dangerBtn")
        action_bar.addWidget(self._clear_btn)

        layout.addLayout(action_bar)

        # Contador de itens
        self._count_label = QLabel("Nenhum item no histórico")
        self._count_label.setObjectName("subtitleLabel")
        layout.addWidget(self._count_label)

        # Tabela
        self._table = QTableWidget()
        self._table.setColumnCount(len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setSortingEnabled(True)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(_COL["Título"], QHeaderView.Stretch)
        header.setSectionResizeMode(_COL["Arquivo"], QHeaderView.Stretch)

        layout.addWidget(self._table, stretch=1)

    def _connect_signals(self) -> None:
        """Conecta sinais internos do painel."""
        self._export_btn.clicked.connect(self._on_export_clicked)
        self._clear_btn.clicked.connect(self._on_clear_clicked)
        self._search_input.textChanged.connect(self._apply_filter)

    @Slot()
    def refresh(self, tasks: list[HistoryTask]) -> None:
        """Atualiza o painel com a lista mais recente de tarefas terminais.

        Deve ser chamado pelo MainWindow sempre que o estado mudar.
        O painel filtra internamente por status terminal e reaaplica
        o filtro de texto ativo.

        Args:
            tasks: Lista completa de tarefas. O painel filtra
                   internamente os status relevantes.
        """
        self._tasks = [t for t in tasks if t.status in _TERMINAL_STATUSES]
        self._apply_filter(self._search_input.text())

    def _apply_filter(self, text: str) -> None:
        """Filtra as linhas pelo texto digitado (título ou URL).

        Args:
            text: Texto de busca; vazio exibe todos os itens.
        """
        query = text.strip().lower()
        visible = [
            t for t in self._tasks
            if not query
            or query in (t.title or "").lower()
            or query in t.url.lower()
        ]
        self._populate_table(visible)

    def _populate_table(self, tasks: list[HistoryTask]) -> None:
        """Preenche a tabela com a lista filtrada de tarefas.

        Args:
            tasks: Tarefas a exibir.
        """
        # Desabilita sorting durante inserção para evitar reordenação contínua
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)

        for task in tasks:
            row = self._table.rowCount()
            self._table.insertRow(row)

            title = task.title or _short_url(task.url)
            status_label = _STATUS_LABELS.get(task.status, task.status)
            size_str = _format_bytes(task.total_bytes)
            speed_str = (
                f"{task.avg_speed_kbps:.0f} KB/s"
                if task.avg_speed_kbps > 0
                else "—"
            )
            date_str = (
                task.finished_at.strftime("%d/%m/%Y %H:%M")
                if task.finished_at
                else "—"
            )
            file_str = str(task.file_path) if task.file_path else "—"

            cells = [title, status_label, size_str, speed_str, date_str, file_str]
            for col, value in enumerate(cells):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

                # Tooltip de erro na coluna Status
                if col == _COL["Status"] and task.status == "error" and task.error_msg:
                    item.setToolTip(task.error_msg)

                self._table.setItem(row, col, item)

        self._table.setSortingEnabled(True)
        self._update_count_label(len(tasks))

    def _update_count_label(self, visible: int) -> None:
        """Atualiza o rótulo de contagem com total e itens visíveis.

        Args:
            visible: Quantidade de itens atualmente visíveis na tabela.
        """
        total = len(self._tasks)
        if total == 0:
            self._count_label.setText("Nenhum item no histórico")
        elif visible == total:
            self._count_label.setText(
                f"{total} {'item' if total == 1 else 'itens'} no histórico"
            )
        else:
            self._count_label.setText(
                f"{visible} de {total} {'item' if total == 1 else 'itens'} exibidos"
            )

    @Slot()
    def _on_export_clicked(self) -> None:
        """Abre diálogo de salvamento e exporta os itens visíveis para CSV."""
        completed = [t for t in self._tasks if t.status == "completed"]
        if not completed:
            QMessageBox.information(
                self,
                "Exportar CSV",
                "Nenhum download concluído para exportar.",
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar histórico",
            f"historico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)",
        )
        if not path:
            return

        self._write_csv(path, completed)
        QMessageBox.information(
            self,
            "Exportar CSV",
            f"Histórico exportado com sucesso:\n{path}",
        )

    @Slot()
    def _on_clear_clicked(self) -> None:
        """Pede confirmação e emite `clear_requested` se confirmado."""
        total = len(self._tasks)
        if total == 0:
            QMessageBox.information(self, "Limpar histórico", "O histórico já está vazio.")
            return

        reply = QMessageBox.question(
            self,
            "Limpar histórico",
            f"Remover {total} {'item' if total == 1 else 'itens'} do histórico?\n"
            "Os arquivos baixados não serão deletados.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.clear_requested.emit()

    @staticmethod
    def _write_csv(path: str, tasks: list[HistoryTask]) -> None:
        """Grava o arquivo CSV com os downloads concluídos.

        Usa encoding utf-8-sig para compatibilidade com Excel no Windows.

        Args:
            path: Caminho completo do arquivo de destino.
            tasks: Tarefas concluídas a incluir no relatório.
        """
        fieldnames = [
            "Data de Inicio",
            "Titulo",
            "URL de Origem",
            "Tamanho (MB)",
            "Velocidade Media (KB/s)",
            "Caminho de Destino",
        ]
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for task in tasks:
                writer.writerow({
                    "Data de Inicio": (
                        task.finished_at.strftime("%Y-%m-%d %H:%M:%S")
                        if task.finished_at
                        else ""
                    ),
                    "Titulo": task.title or _short_url(task.url),
                    "URL de Origem": task.url,
                    "Tamanho (MB)": (
                        round(task.total_bytes / 1_048_576, 2)
                        if task.total_bytes > 0
                        else ""
                    ),
                    "Velocidade Media (KB/s)": (
                        round(task.avg_speed_kbps, 1)
                        if task.avg_speed_kbps > 0
                        else ""
                    ),
                    "Caminho de Destino": str(task.file_path or ""),
                })


def _format_bytes(total: int) -> str:
    """Formata um valor em bytes para string legível (KB, MB, GB).

    Args:
        total: Tamanho em bytes.

    Returns:
        String formatada, ou '—' se total for 0.
    """
    if total <= 0:
        return "—"
    if total < 1_024:
        return f"{total} B"
    if total < 1_048_576:
        return f"{total / 1_024:.1f} KB"
    if total < 1_073_741_824:
        return f"{total / 1_048_576:.2f} MB"
    return f"{total / 1_073_741_824:.2f} GB"


def _short_url(url: str, max_len: int = 60) -> str:
    """Retorna versão truncada da URL para exibição em tabela.

    Args:
        url: URL completa.
        max_len: Comprimento máximo antes do truncamento.

    Returns:
        URL original se curta, ou truncada com '…' ao final.
    """
    return url if len(url) <= max_len else url[:max_len] + "…"
