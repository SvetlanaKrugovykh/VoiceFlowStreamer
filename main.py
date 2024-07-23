# main.py

from src.audio_recorder import AudioRecorder
from src.audio_sender import AudioSender
import time
from dotenv import load_dotenv
import os

def main():
    server_url = os.getenv('SERVER_URL')
    segment_number = 0

    recorder = AudioRecorder(rate=44100, channels=1)
    sender = AudioSender(server_url)
    segment_pause_sec = round(float(os.getenv('SEGMENT_PAUSE_SEC')), 1)

    try:
        while True:
            audio_file = recorder.record_segment()
            if audio_file and os.path.getsize(audio_file) > 0:
                segment_number += 1
                status = sender.send_audio(audio_file, segment_number)
                print(f"Segment {segment_number} sent, status: {status}")

            time.sleep(segment_pause_sec)  # Wait for a X second before recording the next segment
    except KeyboardInterrupt:
        print("Recording stopped")

if __name__ == "__main__":
    main()
