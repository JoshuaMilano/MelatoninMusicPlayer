from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QMouseEvent
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget
)

from backend.AudioEngine import AudioEngine, EngineState
from database.Database import Database

class MainWindow(QMainWindow):
    def __init__(self, title: str):
        super().__init__()

        # Create the AudioEngine
        self.audio_engine = AudioEngine()

        # Create the Database
        self.database = Database()
        self.check_db()

        # Window Config
        self.setWindowTitle(title)
        self.setMinimumSize(QSize(200, 300))
        self.resize(QSize(800, 600))

        # Layout Creation
        layout = QVBoxLayout()

        # Create the control bar
        self.control_bar = ControlBar(self.audio_engine)

        layout.addWidget(self.control_bar)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.menu_bar = MenuBar(self.audio_engine, self.database)
        self.setMenuBar(self.menu_bar)

    def closeEvent(self, event):
        self.audio_engine.stop_playback()
        return super().closeEvent(event)

    def check_db(self):
        if not self.database.db:
            dialog = BuildDatabaseDialog(self)
            dialog.exec()
            new_database_folder = dialog.folder_picker.path_display.text()
            self.database.set_new_location(new_database_folder)


# class MainContent():

class BuildDatabaseDialog(QDialog):
    """Shows a popup to pick a database location"""
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle('Pick a database location')
        layout = QVBoxLayout()

        message = QLabel('Melatonin requires a database to organise and display music.\nPick a database location?')

        self.folder_picker = FolderPicker()
        self.submit_button = QPushButton('Confirm')
        self.submit_button.clicked.connect(self.accept)

        layout.addWidget(message)
        layout.addWidget(self.folder_picker)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)


class MenuBar(QMenuBar):
    def __init__(self, audio_engine: AudioEngine, database: Database):
        super().__init__()

        # Pass the audio engine through
        self.audio_engine = audio_engine
        self.database = database

        # File Menu
        file_menu = QMenu('&File', self)
        self.addMenu(file_menu)
        load_song_action = QAction('Load Song', self)
        stop_song_action = QAction('Unload Song', self)
        rebuild_database_action = QAction('Rebuild Database', self)
        load_song_action.setShortcut('CTRL+L')
        # stop_song_action.setShortcut('CTRL+K')
        load_song_action.triggered.connect(self.load_song)
        stop_song_action.triggered.connect(self.stop_song)
        rebuild_database_action.triggered.connect(self.rebuild_database)
        file_menu.addAction(load_song_action)
        file_menu.addAction(stop_song_action)
        file_menu.addAction(rebuild_database_action)

        # Preferences Menu
        pref_menu = QMenu('&Settings', self)
        self.addMenu(pref_menu)

        # View Menu
        view_menu = QMenu('&View', self)
        self.addMenu(view_menu)
        # Create toggle_fullscreen action
        fullscreen_action = QAction('Toggle Fullscreen', self)
        fullscreen_action.setShortcut('CTRL+F')
        view_menu.addAction(fullscreen_action)
        # Create toggle_mini_player action
        mini_player_action = QAction('Toggle Mini Player', self)
        mini_player_action.setShortcut('CTRL+T')
        view_menu.addAction(mini_player_action)

    def load_song(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select and audio file',
            '',
            'Audio Files (*.mp3 *.wav *.flac)'
        )

        if file_path:
            self.audio_engine.start_playback(file_path)

    def stop_song(self):
        self.audio_engine.stop_playback()   

    def rebuild_database(self):
        self.database.rebuild()

class ControlBar(QWidget):
    def __init__(self, audio_engine: AudioEngine):
        super().__init__()
        # Grab the Audio Engine
        self.audio_engine = audio_engine

        # Create the Progress bar, and set it's range to 0 - 100
        self.duration_bar = MediaSlider(Qt.Orientation.Horizontal)
        self.duration_bar.setEnabled(False)

        # Create the layout to hold the buttons
        button_layout = QHBoxLayout()

        # Create the play and pause buttons
        self.play_pause_button = QPushButton('Play')
        self.play_pause_button.setEnabled(False)
        self.play_pause_button.clicked.connect(self.play_pause_music)

        # Add the play/pause button to layout
        button_layout.addWidget(self.play_pause_button)

        # Create the layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.duration_bar)
        layout.addLayout(button_layout)

        self.audio_engine.total_playback_time.connect(self.duration_bar.setMaximum)
        self.audio_engine.current_playback_time.connect(self.update_slider_position)
        self.duration_bar.sliderMoved.connect(self.audio_engine.change_playback_millisecond_position)
        self.audio_engine.engine_state_changed.connect(self.sync_ui_to_engine)

    def update_slider_position(self, current_ms):
        if not self.duration_bar.isSliderDown():
            self.duration_bar.setValue(current_ms)

    def play_music(self):
        self.audio_engine.resume_playback()

    def pause_music(self):
        self.audio_engine.pause_playback()

    def play_pause_music(self):
        if self.audio_engine.device.running:
            self.audio_engine.pause_playback()
        else:
            self.audio_engine.resume_playback()

    def sync_ui_to_engine(self, state: EngineState):
        if state == EngineState.PLAYING:
            self.duration_bar.setEnabled(True)
            self.play_pause_button.setEnabled(True)
            self.play_pause_button.setText('Pause')
        elif state == EngineState.PAUSED:
            self.duration_bar.setEnabled(True)
            self.play_pause_button.setEnabled(True)
            self.play_pause_button.setText('Play')
        elif state == EngineState.STOPPED:
            self.duration_bar.setEnabled(False)
            self.play_pause_button.setEnabled(False)
            self.play_pause_button.setText('Play')
            self.duration_bar.setValue(0)

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