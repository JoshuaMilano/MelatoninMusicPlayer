from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import Qt, QAction, QMouseEvent
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QMenuBar,
    QMenu,
    QFileDialog,
    QSlider,
    QPushButton
)

from backend.AudioEngine import AudioEngine


class MainWindow(QMainWindow):
    def __init__(self, title: str):
        super().__init__()

        self.audio_engine = AudioEngine()

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

        self.menu_bar = MenuBar(self.audio_engine)
        self.setMenuBar(self.menu_bar)


    def closeEvent(self, event):
        self.audio_engine.stop_playback()
        return super().closeEvent(event)

class MenuBar(QMenuBar):
    def __init__(self, audio_engine: AudioEngine):
        super().__init__()

        # Pass the audio engine through
        self.audio_engine = audio_engine

        # File Menu
        file_menu = QMenu('&File', self)
        self.addMenu(file_menu)
        load_song_action = QAction('Load Song', self)
        stop_song_action = QAction('Unload Song', self)
        load_song_action.setShortcut('CTRL+L')
        stop_song_action.setShortcut('CTRL+K')
        load_song_action.triggered.connect(self.load_song)
        stop_song_action.triggered.connect(self.stop_song)
        file_menu.addAction(load_song_action)
        file_menu.addAction(stop_song_action)

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


class ControlBar(QWidget):
    def __init__(self, audio_engine: AudioEngine):
        super().__init__()
        # Grab the Audio Engine
        self.audio_engine = audio_engine

        # Create the Progress bar, and set it's range to 0 - 100
        self.duration_bar = MediaSlider(Qt.Horizontal)
        self.duration_bar.setEnabled(False)

        # Create the layout to hold the buttons
        button_layout = QHBoxLayout()

        # Create the play and pause buttons
        self.play_button = QPushButton('Play')
        self.play_button.clicked.connect(self.play_music)
        self.pause_button = QPushButton('Stop')
        self.pause_button.clicked.connect(self.pause_music)

        # Add play and pause buttons to layout
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.pause_button)

        # Create the layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.duration_bar)
        layout.addLayout(button_layout)

        self.audio_engine.total_playback_time.connect(self.duration_bar.setMaximum)
        self.audio_engine.current_playback_time.connect(self.update_slider_position)
        self.audio_engine.file_currently_loaded.connect(self.duration_bar.setEnabled)
        self.audio_engine.file_currently_loaded.connect(self.play_button.setEnabled)
        self.audio_engine.file_currently_loaded.connect(self.pause_button.setEnabled)
        self.duration_bar.sliderMoved.connect(self.audio_engine.change_playback_millisecond_position)

    def update_slider_position(self, current_ms):
        if not self.duration_bar.isSliderDown():
            self.duration_bar.setValue(current_ms)

    def play_music(self):
        self.audio_engine.resume_playback()

    def pause_music(self):
        self.audio_engine.pause_playback()

class MediaSlider(QSlider):
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
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