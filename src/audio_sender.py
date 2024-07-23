# src/audio_sender.py
from dotenv import load_dotenv
import os

import requests

class AudioSender:
    def __init__(self, server_url):
        self.server_url = server_url

    def send_audio(self, file_path, segment_number):
        # Open the audio file and prepare the POST request
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {'segment': segment_number}
            response = requests.post(self.server_url, files=files, data=data)

        print(f"Status Code: {response.status_code}")

        try:
            response_json = response.json()
            if response.status_code == 200:
                print(f"Transcription: {response_json.get('transcription', 'No transcription found')}")
            else:
                print(f"Error: {response_json.get('error', 'Unknown error')}")
                print(f"Reason: {response_json.get('reason', 'No reason provided')}")
        except ValueError:
            print("Failed to parse response as JSON")

        return response.status_code
