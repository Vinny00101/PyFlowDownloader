import csv
from datetime import datetime
from typing import Protocol

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
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


class LogEntryProtocol(Protocol):
    event_type: str
    status: str
    message: str
    download_id: int | None
    error_message: str
    created_at: datetime


_COLUMNS = ["Data", "Evento", "Status", "Mensagem", "Download"]
_COL = {name: idx for idx, name in enumerate(_COLUMNS)}


class LogsPanel(QWidget):
    clear_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._logs: list[LogEntryProtocol] = []
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        action_bar = QHBoxLayout()
        action_bar.setContentsMargins(0, 0, 0, 0)
        action_bar.setSpacing(8)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Filtrar por evento, status ou mensagem...")
        self._search_input.setClearButtonEnabled(True)
        action_bar.addWidget(self._search_input, stretch=1)

        self._export_btn = QPushButton("Exportar CSV")
        self._export_btn.setObjectName("secondaryBtn")
        action_bar.addWidget(self._export_btn)

        self._clear_btn = QPushButton("Limpar logs")
        self._clear_btn.setObjectName("dangerBtn")
        action_bar.addWidget(self._clear_btn)
        layout.addLayout(action_bar)

        self._count_label = QLabel("Nenhum log registrado")
        self._count_label.setObjectName("subtitleLabel")
        layout.addWidget(self._count_label)

        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_frame_layout = QVBoxLayout(table_frame)
        table_frame_layout.setContentsMargins(1, 1, 1, 1)
        table_frame_layout.setSpacing(0)

        self._table = QTableWidget()
        self._table.setObjectName("historyTable")
        self._table.setColumnCount(len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.setSortingEnabled(True)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(_COL["Mensagem"], QHeaderView.Stretch)

        table_frame_layout.addWidget(self._table)
        layout.addWidget(table_frame, stretch=1)

    def _connect_signals(self) -> None:
        self._search_input.textChanged.connect(self._apply_filter)
        self._export_btn.clicked.connect(self._on_export_clicked)
        self._clear_btn.clicked.connect(self._on_clear_clicked)

    @Slot()
    def refresh(self, logs: list[LogEntryProtocol]) -> None:
        self._logs = logs
        self._apply_filter(self._search_input.text())

    def _apply_filter(self, text: str) -> None:
        query = text.strip().lower()
        visible = [
            log for log in self._logs
            if not query
            or query in log.event_type.lower()
            or query in log.status.lower()
            or query in log.message.lower()
            or query in log.error_message.lower()
        ]
        self._populate_table(visible)

    def _populate_table(self, logs: list[LogEntryProtocol]) -> None:
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)

        for log in logs:
            row = self._table.rowCount()
            self._table.insertRow(row)
            download = f"#{log.download_id}" if log.download_id is not None else "—"
            cells = [
                log.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                log.event_type,
                log.status or "—",
                log.message or "—",
                download,
            ]
            for col, value in enumerate(cells):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if log.error_message:
                    item.setToolTip(log.error_message)
                self._table.setItem(row, col, item)

        self._table.setSortingEnabled(True)
        self._update_count_label(len(logs))

    def _update_count_label(self, visible: int) -> None:
        total = len(self._logs)
        if total == 0:
            self._count_label.setText("Nenhum log registrado")
        elif visible == total:
            self._count_label.setText(f"{total} {'log' if total == 1 else 'logs'} registrados")
        else:
            self._count_label.setText(f"{visible} de {total} logs exibidos")

    @Slot()
    def _on_export_clicked(self) -> None:
        if not self._logs:
            QMessageBox.information(self, "Exportar CSV", "Nenhum log para exportar.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar logs",
            f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)",
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["Data", "Evento", "Status", "Mensagem", "Download", "Erro"],
            )
            writer.writeheader()
            for log in self._logs:
                writer.writerow({
                    "Data": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "Evento": log.event_type,
                    "Status": log.status,
                    "Mensagem": log.message,
                    "Download": log.download_id if log.download_id is not None else "",
                    "Erro": log.error_message,
                })

        QMessageBox.information(self, "Exportar CSV", f"Logs exportados com sucesso:\n{path}")

    @Slot()
    def _on_clear_clicked(self) -> None:
        if not self._logs:
            QMessageBox.information(self, "Limpar logs", "Os logs já estão vazios.")
            return

        reply = QMessageBox.question(
            self,
            "Limpar logs",
            f"Remover {len(self._logs)} {'log' if len(self._logs) == 1 else 'logs'}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.clear_requested.emit()
