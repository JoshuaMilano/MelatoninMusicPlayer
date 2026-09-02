import miniaudio
from PySide6.QtCore import QObject, Signal
from enum import Enum, auto
import gc

from backend.SongHelpers import SongMetadata, get_song_metadata


# TODO: Upgrade engine to support up to 32bit audio

class EngineState(Enum):
    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()
    FINISHED = auto()

# This controls the framerate of the UI audio slider.
slider_framerate = 60

# The Purpose of the StreamProxy is to hijack the connection between the AudioEngine and the miniaudio C library
class StreamProxy:
    def __init__(self, sound_file, engine):
        # We grab the decoded sound file
        self.decoded_sound_file = sound_file

        # We grab the amount of audio channels (Mono, Stereo, Etc)
        self.decoded_sound_file_channels = self.decoded_sound_file.nchannels

        # We grab the AudioEngine
        self.engine = engine


    def send(self, framecount):
        if framecount == 0:
            return b''

        # Files with multiple audio channels alternate in memory, so we calculate the index for every SET of channels
        memory_start_index = (self.engine.frames_played * self.decoded_sound_file_channels)

        # We multiply the amount of frames by the amount of channels to get the full array index
        memory_end_index = memory_start_index + (framecount * self.decoded_sound_file_channels)

        try:
            # We grab a chunk of audio
            chunk = self.decoded_sound_file.samples[memory_start_index:memory_end_index]

            # If that chunk was empty, the song finished
            if not chunk:
                if self.engine.engine_state != EngineState.FINISHED:
                    self.engine.engine_state = EngineState.FINISHED
                    print('finished')
                return b''

            # Add number of frames played to frames_played variable
            self.engine.frames_played += len(chunk) // self.decoded_sound_file_channels

            # Convert the total frames into milliseconds
            current_milliseconds = (self.engine.frames_played * 1000) // self.engine.device.sample_rate

            if current_milliseconds - self.engine.last_emitted_milliseconds >= (1000 // slider_framerate):
                self.engine.current_playback_time.emit(current_milliseconds)
                self.engine.last_emitted_milliseconds = current_milliseconds


            # return the data as bytes
            return chunk.tobytes()

        except StopIteration:
            self.engine.engine_state = EngineState.STOPPED
            return b''

        # These ensure miniaudio accepts the class as a valid iterator
    def __iter__(self):
        return self

    # miniaudio starts by asking for 0 frames
    def __next__(self):
        return self.send(0)

    # If the generator throws an error, stop iterating
    def throw(self, typ, val=None, tb=None):
        raise StopIteration

    # Called when the generator is closed
    def close(self):
        pass
            

# The purpose of the AudioEngine is to manage and play audio, as well as transmit signals from the backend to the frontend UI
class AudioEngine(QObject):
    # Signal to relay total playback time (i.e. duration) to the frontend ui
    total_playback_time = Signal(int)
    # Signal to relay current playback time (i.e. location in song stream) to the frontend ui
    current_playback_time = Signal(int)
    # Signal to sync the UI to the Engine
    engine_state_changed = Signal(object)

    def __init__(self):
        super().__init__()
        # initialise device
        self.device = miniaudio.PlaybackDevice()

        # Create an empty stream object to hold the data stream going to the device
        self.stream = None

        # Create and Set Engine State
        self.engine_state: EngineState = EngineState.STOPPED

        self.engine_state_changed.emit(self.engine_state)

        # set the frames played to 0
        self.frames_played = 0

        # Track last emitted millisecond of music
        self.last_emitted_milliseconds = -(1000 // slider_framerate)

    def unload_audio(self):
        # Stop The Audio, unload the audio
        self.device.close()
        self.file_in_memory = None
        self.stream = None
        gc.collect()

    def start_playback(self, file_path):
        # if the device is running, stop playback
        if self.device.running:
            self.device.stop()
            self.engine_state = EngineState.STOPPED
        
        # update engine state
        self.engine_state = EngineState.PLAYING

        # set frames played to 0
        self.frames_played = 0

        # Track last emitted millisecond of music
        self.last_emitted_milliseconds = -(1000 // slider_framerate)

        # convert the file path to a str, and store it in a variable
        self.file_path_str = str(file_path)

        # Grab the metadata from mutagen, use get_song_metadata function
        metadata = get_song_metadata(file_path)

        # If metadata exists
        if metadata:
            duration = metadata.duration_ms
            self.total_playback_time.emit(duration)

        # With file, read in binary mode, and load that data into memory.
        with open(file_path, 'rb') as file:
            audio_bytes = file.read()

        self.file_in_memory = miniaudio.decode(
            audio_bytes,
            output_format=miniaudio.SampleFormat.SIGNED16
        )

        # Close the file if it didn't close automatically.
        file.close()

        self.device = miniaudio.PlaybackDevice(
            output_format=miniaudio.SampleFormat.SIGNED16,
            nchannels=self.file_in_memory.nchannels,
            sample_rate=self.file_in_memory.sample_rate,
            buffersize_msec= 1000 // slider_framerate
        )

        self.stream = StreamProxy(self.file_in_memory, self)

        # Stream Song
        self.device.start(self.stream)

        # Update Engine State
        
        self.engine_state: EngineState = EngineState.PLAYING
        self.engine_state_changed.emit(self.engine_state)


    def stop_playback(self):
        # If the stream device is running, stop it.
        if self.device.running:
            self.unload_audio()

        # set frames played to 0
        self.frames_played = 0

        # Track last emitted millisecond of music
        self.last_emitted_milliseconds = -(1000 // slider_framerate)

        # Set engine state
        self.engine_state: EngineState = EngineState.STOPPED

        # Emit engine_state
        self.engine_state_changed.emit(EngineState.STOPPED)

    def resume_playback(self):
        if not self.device.running:
            self.device.start(self.stream) # type: ignore
            self.engine_state: EngineState = EngineState.PLAYING
            self.engine_state_changed.emit(self.engine_state)

    def pause_playback(self):
        if self.device.running:
            self.device.stop()
            self.engine_state: EngineState = EngineState.PAUSED
            self.engine_state_changed.emit(self.engine_state)

    def change_playback_millisecond_position(self, target_ms):
        
        # If there isn't a file in memory, return.
        if not self.file_in_memory:
            return

        # Convert the milliseconds to the frame
        target_frame = (target_ms * self.file_in_memory.sample_rate) // 1000

        if target_frame >= self.file_in_memory.num_frames:
            target_frame = self.file_in_memory.num_frames - 1

        self.frames_played = target_frame

        self.last_emitted_milliseconds = target_ms - (1000 // slider_framerate)