from PySide6.QtWidgets import QVBoxLayout, QMainWindow, QWidget, QPushButton
from PySide6.QtCore import QSize

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window Config
        self.setWindowTitle('Melatonin Music Player')
        self.setMinimumSize(QSize(200, 300))

        # Layout Creation
        layout = QVBoxLayout()

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)