# src/audio_sender.py
from dotenv import load_dotenv
import os

import requests

class AudioSender:
    def __init__(self, server_url):
        self.server_url = server_url

    def send_audio(self, file_path, segment_number):
        files = {'file': open(file_path, 'rb')}
        data = {'segment': segment_number}
        response = requests.post(self.server_url, files=files, data=data)
        return response.status_code
