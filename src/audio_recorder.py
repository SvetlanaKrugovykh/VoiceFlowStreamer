# src/audio_recorder.py
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

        output_path = os.getenv('OUTPUT_PATH', 'output')
        if output_path:
          self.output_filename = os.path.join(output_path, self.output_filename)
        
    def is_silence(self, snd_data):
        """Check if the given audio chunk is silence."""
        return max(snd_data) < 500  # Adjust this threshold based on your microphone sensitivity

    def record_segment(self):
        print("Preparing to record...")
        self.frames = []
        self.silence_frames.clear()  # Ensure silence_frames is cleared at the start
        if not 8000 <= self.rate <= 48000:
          raise ValueError(f"Rate {self.rate} is out of acceptable range (8000-48000)")

        print('self.rate', self.rate)
        stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        is_speech_detected = False

        while True:
            data = stream.read(self.chunk, exception_on_overflow=False)
            snd_data = np.frombuffer(data, dtype=np.int16)
            if not self.is_silence(snd_data):
                if not is_speech_detected:
                    print("Recording segment...")
                is_speech_detected = True
                self.frames.append(data)
                self.silence_frames.clear()  # Clear silence_frames since speech is detected
            else:
                if is_speech_detected:
                    # If speech was detected and now silence is detected, add to silence_frames
                    self.silence_frames.append(1)
                    if len(self.silence_frames) == self.silence_frames.maxlen:
                        # If continuous silence for the duration of silence_limit, stop recording
                        break
                # else:
                    # print("Waiting for speech...")
            
        stream.stop_stream()
        stream.close()

        if self.frames:
            output_filename = f"{self.output_filename}"
            wf = wave.open(output_filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            print("Segment recorded.")
            return output_filename
        else:
            print("No speech detected.")
            return None

if __name__ == "__main__":
    recorder = AudioRecorder()
    segment_filename = recorder.record_segment()
    print(f"Recorded segment saved to {segment_filename}")
    