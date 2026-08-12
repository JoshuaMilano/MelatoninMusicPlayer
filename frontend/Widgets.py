from PySide6.QtGui import Qt, QMouseEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QSlider
)

class FolderPicker(QWidget):
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

class MediaSlider(QSlider):
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # Grab pixel user clicked on
            click_position = event.position().x()
            # Grab width of slider
            total_width = self.width()
            # Assuming a position of 100px and a width of 400px
            # Grab percentage (100th pixel / 400px width = 0.25)
            percentage = click_position / total_width

            # New value is minimum (0) + ((maximum (400px) - minimum (0px)) * percentage (0.25))
            new_value = self.minimum() + ((self.maximum() - self.minimum()) * percentage)

            # Value is new value converted from a float to an int
            self.setValue(int(new_value))

            # Hey Engine, the Slider moved!
            self.sliderMoved.emit(int(new_value))

            event.accept()
        super().mousePressEvent(event)