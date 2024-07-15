import pyaudio
import numpy as np
import wave
import os, time
from collections import deque

class AudioRecorder:
    def __init__(self, channels=1, rate=16000, chunk=1024, silence_limit=1, output_filename="output.wav"):
        self.format = pyaudio.paInt16
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.silence_limit = silence_limit  # Silence limit in seconds
        self.output_filename = output_filename
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.silence_frames = deque(maxlen=int(self.silence_limit * self.rate / self.chunk))

    def is_silence(self, snd_data):
        """Check if the given audio chunk is silence."""
        return max(snd_data) < 500  # Adjust this threshold based on your microphone sensitivity

    def record_segment(self):
        print("Preparing to record...")
        self.frames = []
        stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        is_speaking = False
        start_time = time.time()
        max_wait_time = int(os.getenv("MAX_WAIT_TIME_SEC", 30))

        while not is_speaking and (time.time() - start_time) < max_wait_time:
            data = stream.read(self.chunk, exception_on_overflow=False)
            snd_data = np.frombuffer(data, dtype=np.int16)
            if not self.is_silence(snd_data):
                is_speaking = True

        if not is_speaking:
            print("No speech detected within the wait time.")
            stream.stop_stream()
            stream.close()
            return None

        print("Recording segment...")

        while True:
            data = stream.read(self.chunk)
            snd_data = np.frombuffer(data, dtype=np.int16)
            if self.is_silence(snd_data) and is_speaking:
                self.silence_frames.append(1)
                if len(self.silence_frames) == self.silence_frames.maxlen:
                    break
            else:
                self.silence_frames.clear()
                is_speaking = True
                self.frames.append(data)
        
        stream.stop_stream()
        stream.close()

        output_filename = f"{self.output_filename}"
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        print("Segment recorded.")
        return output_filename

if __name__ == "__main__":
    recorder = AudioRecorder()
    segment_filename = recorder.record_segment()
    print(f"Recorded segment saved to {segment_filename}")
    