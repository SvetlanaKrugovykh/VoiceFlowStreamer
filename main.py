# main.py

from src.audio_recorder import AudioRecorder
from src.audio_sender import AudioSender
import time
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    server_url = os.getenv('SERVER_URL')
    segment_number = 0

    recorder = AudioRecorder(rate=44100, channels=1)
    sender = AudioSender(server_url)
    segment_pause_sec = round(float(os.getenv('SEGMENT_PAUSE_SEC')), 1)

    tasks = []

    try:
        while True:
            audio_file = recorder.record_segment()
            if audio_file and os.path.getsize(audio_file) > 0:
                segment_number += 1
                task = asyncio.create_task(sender.send_audio(audio_file, segment_number))
                tasks.append(task)

            await asyncio.sleep(segment_pause_sec)

    except KeyboardInterrupt:
        print("Recording stopped")

if __name__ == "__main__":
    asyncio.run(main())