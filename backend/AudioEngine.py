import miniaudio

class StreamProxy:
    def __init__(self, raw_stream, engine):
        # Capture the original object (The Generator)
        self.raw_stream = raw_stream
        # Capture the engine responsible for playing audio
        self.engine = engine

    # We Hijack the miniaudio generator, so we can attach a finished flag to the audio flag
    def send(self, framecount):
        try:
            # Pass the raw_stream data to the C-Thread
            return self.raw_stream.send(framecount)
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


class AudioEngine:
    def __init__(self):
        # Initialise the audio device
        self.device = miniaudio.PlaybackDevice()
        self.stream = None

        # Flag if the song has ended
        self.is_finished = True

    def start_playback(self, file_path):
        # Stop anything currently playing
        if self.device.running:
            self.device.stop()

        # miniaudio requires the path to be a string.
        file_path_str = str(file_path)

        # Reset the finished flag when starting a song
        self.is_finished = False

        # Load the file, start the device.
        raw_stream = miniaudio.stream_file(file_path_str)

        # Wrap the raw stream in our custom class
        self.stream = StreamProxy(raw_stream, self)
        self.device.start(self.stream)

    def stop_playback(self):
        if self.device.running:
            self.device.stop()

        self.is_finished = True