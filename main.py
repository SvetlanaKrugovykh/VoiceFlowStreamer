# main.py

from src.audio_recorder import AudioRecorder
from src.audio_sender import AudioSender
import time
from dotenv import load_dotenv
import os

def main():
    server_url = os.getenv('SERVER_URL')
    segment_number = 0

    recorder = AudioRecorder()
    sender = AudioSender(server_url)

    try:
        while True:
            segment_number += 1
            audio_file = recorder.record_segment()  # Assume this method now handles a single recording segment
            status = sender.send_audio(audio_file, segment_number)
            print(f"Segment {segment_number} sent, status: {status}")
            time.sleep(1)  # Pause between segments
    except KeyboardInterrupt:
        print("Recording stopped")

if __name__ == "__main__":
    main()
