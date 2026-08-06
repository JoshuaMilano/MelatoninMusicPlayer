from PySide6.QtCore import QObject, Signal
import miniaudio, mutagen

class StreamProxy:
    def __init__(self, raw_stream, engine):
        # Capture the original object (The Generator)
        self.raw_stream = raw_stream
        # Capture the engine responsible for playing audio
        self.engine = engine

    # We Hijack the miniaudio generator, so we can attach a finished flag to the audio flag
    def send(self, framecount):
        try:
            # Grab the raw_stream data
            data = self.raw_stream.send(framecount)

            # Track the frames used by miniaudio
            if framecount > 0:
                self.engine.frames_played += framecount

                # Convert total frames to seconds
                current_seconds = self.engine.frames_played // self.engine.device.sample_rate

                # Only update the UI when the current_seconds are greater then the last emitted second
                if current_seconds > self.engine.last_emitted_second:
                    self.engine.current_playback_time.emit(current_seconds)
                    self.engine.last_emitted_second = current_seconds

            # Pass the raw_stream data to the C-Thread
            return data
        except StopIteration:
            # The stream ran out of data, so the song is finished
            self.engine.is_finished = True
            
            # Return an empty byte string to tell the C-library to close
            return b""

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


class AudioEngine(QObject):
    total_playback_time = Signal(int)
    current_playback_time = Signal(int)

    def __init__(self):
        super().__init__()
        # Initialise the audio device
        self.device = miniaudio.PlaybackDevice()
        self.stream = None

        # Flag if the song has ended
        self.is_finished = True

        # Set variables for tracking time
        self.frames_played = 0
        self.last_emitted_second = -1
        
    def start_playback(self, file_path_str):
        # Stop anything currently playing
        if self.device.running:
            self.device.stop()

        # Reset the finished flag when starting a song
        self.is_finished = False

        # Reset variables for tracking time
        self.frames_played = 0
        self.last_emitted_second = -1
        
        # miniaudio requires the path to be a string.
        file_path = str(file_path_str)

        # Grab the song metadata from mutagen
        audio_metadata = mutagen.File(file_path)
        if audio_metadata:
            # Get duration of song (in seconds)
            duration = int(audio_metadata.info.length)
            self.total_playback_time.emit(duration)

        # Load the file, start the device.
        raw_stream = miniaudio.stream_file(file_path)

        # Wrap the raw stream in our custom class
        self.stream = StreamProxy(raw_stream, self)
        self.device.start(self.stream)

    def stop_playback(self):
        if self.device.running:
            self.device.stop()

        # Reset variables for tracking time
        self.frames_played = 0
        self.last_emitted_second = -1

        # Set is_finished to True
        self.is_finished = True