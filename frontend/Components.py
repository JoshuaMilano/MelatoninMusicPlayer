from PySide6.QtWidgets import QVBoxLayout, QMainWindow, QWidget, QMenuBar, QMenu, QFileDialog, QProgressBar
from PySide6.QtGui import QAction
from PySide6.QtCore import QSize

from backend.AudioEngine import AudioEngine

class MainWindow(QMainWindow):
    def __init__(self, title: str):
        super().__init__()

        self.audioEngine = AudioEngine()

        # Window Config
        self.setWindowTitle(title)
        self.setMinimumSize(QSize(200, 300))
        self.resize(QSize(800, 600))

        # Layout Creation
        layout = QVBoxLayout()

        # Create the control bar
        self.control_bar = ControlBar()

        layout.addWidget(self.control_bar)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.menu_bar = MenuBar(self.audioEngine)
        self.setMenuBar(self.menu_bar)

        self.audioEngine.total_playback_time.connect(self.control_bar.progress_bar.setMaximum)
        self.audioEngine.current_playback_time.connect(self.control_bar.progress_bar.setValue)

    def closeEvent(self, event):
        self.audioEngine.stop_playback()
        return super().closeEvent(event)

class MenuBar(QMenuBar):
    def __init__(self, audio_engine: AudioEngine):
        super().__init__()

        # Pass the audio engine through
        self.audio_engine = audio_engine

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

        # DEBUG MENU!!!
        debug_menu = QMenu('DEBUG', self)
        self.addMenu(debug_menu)
        load_song_action = QAction('Load Song', self)
        stop_song_action = QAction('Stop Song', self)
        load_song_action.setShortcut('CTRL+L')
        stop_song_action.setShortcut('CTRL+K')
        load_song_action.triggered.connect(self.load_song)
        stop_song_action.triggered.connect(self.stop_song)
        debug_menu.addAction(load_song_action)
        debug_menu.addAction(stop_song_action)

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
    def __init__(self):
        super().__init__()
        # Create the Progress bar, and set it's range to 0 - 100
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)

        # Create the layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.progress_bar)

