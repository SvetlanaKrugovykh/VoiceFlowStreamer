# src/audio_sender.py
import logging
from dotenv import load_dotenv
import os
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AudioSender:
    def __init__(self, server_url):
        self.server_url = server_url
        logging.basicConfig(filename='transcriptions.log', level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')
        self.logger = logging.getLogger()

    def send_audio(self, file_path, segment_number):
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {'segment': segment_number}
            AUTHORIZATION = os.getenv('AUTHORIZATION')
            prod_mode = int(os.getenv('PROD_MODE'))
            response = requests.post(self.server_url, files=files, data=data, headers={'Authorization': AUTHORIZATION}, verify=prod_mode)
        try:
            response_json = response.json()
            if response.status_code == 200:
                transcription = response_json.get('transcription', 'No transcription found')
                self.logger.info(f": {transcription}")
            else:
                error_message = response_json.get('error', 'Unknown error')
                reason = response_json.get('reason', 'No reason provided')
                self.logger.info(f"Status Code: {response.status_code}")
                self.logger.error(f"Error: {error_message}")
                self.logger.error(f"Reason: {reason}")
        except ValueError:
            self.logger.error("Failed to parse response as JSON")

        return response.status_code