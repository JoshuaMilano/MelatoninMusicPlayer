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
from backend.AudioEngine import AudioEngine, EngineState

class MediaControls(QWidget):
    def __init__(self, audio_engine: AudioEngine):
        super().__init__()

        # Grab the Audio Engine
        self.audio_engine = audio_engine

        # Grab the Queue
        self.queue = audio_engine.queue

        # Create the previous button
        self.prev_button = QPushButton('|<')
        self.prev_button.setEnabled(False)
        self.prev_button.clicked.connect(self.prev_button_method)

        # Create the play/pause button
        self.play_pause_button = QPushButton('Play')
        self.play_pause_button.setEnabled(False)
        self.play_pause_button.clicked.connect(self.play_pause_method)

        # Create the next button
        self.next_button = QPushButton('>|')
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.next_button_method)

        # Create the widget layout
        layout = QHBoxLayout()

        # Assign buttons to the layout
        layout.addWidget(self.prev_button)
        layout.addWidget(self.play_pause_button)
        layout.addWidget(self.next_button)

        # Assign the layout to the widget
        self.setLayout(layout)

        self.audio_engine.engine_state_changed.connect(self.sync_ui_to_engine)

    def prev_button_method(self):
        if not self.queue.current_song.prev:
            self.audio_engine.reset_playback(start_paused=False)


    def play_pause_method(self):
            if self.audio_engine.engine_state == EngineState.PLAYING:
                self.audio_engine.pause_playback()
            elif self.audio_engine.engine_state == EngineState.FINISHED:
                self.audio_engine.resume_playback()
            else:
                self.audio_engine.resume_playback()

    def next_button_method(self):
        if not self.queue.current_song.next:
            self.audio_engine.reset_playback()


    def sync_ui_to_engine(self, state: EngineState):
        match state:
            case EngineState.PLAYING:
                self.prev_button.setEnabled(True)
                self.next_button.setEnabled(True)
                self.play_pause_button.setEnabled(True)
                self.play_pause_button.setText('Pause')
            case EngineState.PAUSED:
                self.prev_button.setEnabled(True)
                self.next_button.setEnabled(True)
                self.play_pause_button.setEnabled(True)
                self.play_pause_button.setText('Play')
            case EngineState.STOPPED:
                self.prev_button.setEnabled(False)
                self.next_button.setEnabled(False)
                self.play_pause_button.setEnabled(False)
                self.play_pause_button.setText('Play')