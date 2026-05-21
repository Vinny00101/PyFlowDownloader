
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton 


class MainWindow(QMainWindow): 
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyFlowDownloader")

        self.setMinimumSize(QSize(800, 500))

        self.resize(1024, 600)
        
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)



        theme_button = QPushButton()
        theme_button
        
        layout = QVBoxLayout(self.central_widget)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def keyPressEvent(self, event_input: Qt):
        # verificar se a tecla que foi presionada é o f11 no teclado.
        if event_input.key() == Qt.Key_F11:
            self.toggle_fullscreen()
            event_input.accept()
        else:
            # passa as demais tecla em diantes
            super().keyPressEvent(self.event)


    