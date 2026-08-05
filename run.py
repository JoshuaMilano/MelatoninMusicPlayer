from PySide6.QtWidgets import QApplication, QWidget
from frontend.Components import MainWindow
from frontend.Styles import STYLESHEET

if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    app.exec()