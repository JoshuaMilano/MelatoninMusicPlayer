from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QVBoxLayout,
    QWidget
)

from frontend.Widgets import MediaSlider
from frontend.Dialogs import BuildDataFolderDialog
from frontend.Controls import MediaControls
from backend.AudioEngine import AudioEngine, EngineState
from backend.Backend import Backend

class MainWindow(QMainWindow):
    def __init__(self, title: str):
        super().__init__()

        # Attach the backend
        self.backend = Backend()

        # Access Datafolder directly
        self.data_folder = self.backend.data_folder

        # Access AudioEngine directly
        self.audio_engine = self.backend.audio_engine

        # Access FileManager directly
        self.file_manager = self.backend.file_manager

        # Check Datafolder Exists
        self.check_datafolder_exists()

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

    #   self.menu_bar = MenuBar(self.audio_engine, self.database)
        self.menu_bar = MenuBar(self.backend,)
        self.setMenuBar(self.menu_bar)

    def closeEvent(self, event):
        self.audio_engine.stop_playback()
        return super().closeEvent(event)

    def check_datafolder_exists(self):
        if not self.data_folder.datafolder_location:
            dialog = BuildDataFolderDialog(self)
            dialog.exec()
            new_datafolder_location = dialog.data()
            self.data_folder.setup_folder(new_datafolder_location)

# class MainContent():

class MenuBar(QMenuBar):
    # def __init__(self, audio_engine: AudioEngine, database: Database):
    def __init__(self, backend: Backend):
        super().__init__()

        # Access Datafolder directly
        self.data_folder = backend.data_folder

        # Access AudioEngine directly
        self.audio_engine = backend.audio_engine

        # Access FileManager directly
        self.file_manager = backend.file_manager

        # Pass the audio engine through
        self.audio_engine = self.audio_engine

        # File Menu
        file_menu = QMenu('&File', self)
        self.addMenu(file_menu)
        load_song_action = QAction('Load Song', self)
        stop_song_action = QAction('Unload Song', self)
        queue_song_action = QAction('Queue Song', self)
        # DEBUG DEBUG DEBUG === DO NOT COMMIT
        sort_folder_action = QAction('Sort Folder', self)
        rebuild_database_action = QAction('Rebuild Database', self)
        load_song_action.setShortcut('CTRL+L')
        # stop_song_action.setShortcut('CTRL+K')
        load_song_action.triggered.connect(self.load_song)
        stop_song_action.triggered.connect(self.stop_song)
        queue_song_action.triggered.connect(self.queue_song)
        # DEBUG DEBUG DEBUG === DO NOT COMMIT
        sort_folder_action.triggered.connect(self.sort_folder)
        # rebuild_database_action.triggered.connect(self.rebuild_database)
        file_menu.addAction(load_song_action)
        file_menu.addAction(stop_song_action)
        file_menu.addAction(queue_song_action)
        # DEBUG DEBUG DEBUG === DO NOT COMMIT
        file_menu.addAction(sort_folder_action)
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
            self.audio_engine.play(file_path)

    def queue_song(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select and audio file',
            '',
            'Audio Files (*.mp3 *.wav *.flac)'
        )

        if file_path:
            self.audio_engine.queue.append(file_path)

    def stop_song(self):
        self.audio_engine.stop_playback()
        
    # DEBUG DEBUG DEBUG === DO NOT COMMIT
    def sort_folder(self):
        musicfolder = QFileDialog.getExistingDirectory(
            self,
            'Select Music Folder'
        )
        self.file_manager.sort_music_folder(Path(musicfolder))

    def rebuild_database_action(self):
        # self.database.rebuild()
        pass

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

        self.media_controls = MediaControls(audio_engine)

        # Create the layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addStretch()
        layout.addWidget(self.duration_bar)
        layout.addWidget(self.media_controls)

        self.audio_engine.total_playback_time.connect(self.duration_bar.setMaximum)
        self.audio_engine.current_playback_time.connect(self.update_slider_position)
        self.duration_bar.sliderMoved.connect(self.audio_engine.change_playback_millisecond_position)
        self.audio_engine.engine_state_changed.connect(self.sync_ui_to_engine)

    def update_slider_position(self, current_ms):
        if not self.duration_bar.isSliderDown():
            self.duration_bar.setValue(current_ms)

    def play_pause_music(self):
        if self.audio_engine.engine_state == EngineState.PLAYING:
            self.audio_engine.pause_playback()
        elif self.audio_engine.engine_state == EngineState.FINISHED:
            self.audio_engine.resume_playback()
        else:
            self.audio_engine.resume_playback()

    def sync_ui_to_engine(self, state: EngineState):
        match state:
            case EngineState.PLAYING:
                self.duration_bar.setEnabled(True)
                self.play_pause_button.setEnabled(True)
                self.play_pause_button.setText('Pause')
            case EngineState.PAUSED:
                self.duration_bar.setEnabled(True)
                self.play_pause_button.setEnabled(True)
                self.play_pause_button.setText('Play')
            case EngineState.STOPPED:
                self.duration_bar.setEnabled(False)
                self.play_pause_button.setEnabled(False)
                self.play_pause_button.setText('Play')
                self.duration_bar.setValue(0)