from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget
)

class BuildDataFolderDialog(QDialog):
    """Shows a popup to pick a folder location"""
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle('Pick a data folder location')
        layout = QVBoxLayout()

        message = QLabel('Melatonin requires a folder to store a music database and user preferences.\nPick a folder location?')

        self.folder_picker = FolderPicker()
        self.submit_button = QPushButton('Confirm')
        self.submit_button.clicked.connect(self.accept)

        layout.addWidget(message)
        layout.addWidget(self.folder_picker)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)

class PickLibraryDialog(QDialog):
    """Shows a popup asking the user to pick their library folder"""
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle('Pick')

class FolderPicker(QWidget):
    """UI Component to let the user pick a folder"""
    def __init__(self, *, label_text: str = 'Select a folder', placeholder: str = 'Select a folder...'):
        super().__init__()
        widget_layout = QVBoxLayout()

        self.label = QLabel(label_text)
        widget_layout.addWidget(self.label)
        widget_layout.setSpacing(5)

        folder_select_layout = QHBoxLayout()

        self.path_display = QLineEdit()
        self.path_display.setPlaceholderText(placeholder)

        self.browse_button = QPushButton('Browse...')
        self.browse_button.clicked.connect(self.open_folder_dialog)

        folder_select_layout.addWidget(self.path_display)
        folder_select_layout.addWidget(self.browse_button)

        widget_layout.addLayout(folder_select_layout)

        self.setLayout(widget_layout)

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select a Folder')

        if folder_path:
            self.path_display.setText(folder_path)
