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
            audio_file = recorder.record_segment()  
            status = sender.send_audio(audio_file, segment_number)
            print(f"Segment {segment_number} sent, status: {status}")
            segment_pause_sec = round(float(os.getenv('SEGMENT_PAUSE_SEC')), 1)
            time.sleep(segment_pause_sec)  # Wait for a X second before recording the next segment
    except KeyboardInterrupt:
        print("Recording stopped")

if __name__ == "__main__":
    main()
