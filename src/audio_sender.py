# src/audio_sender.py
import logging
from dotenv import load_dotenv
import os
import aiohttp
import asyncio
import ssl
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class AudioSender:
    def __init__(self, server_url):
        self.server_url = server_url
        logging.basicConfig(filename='transcriptions.log', level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')
        self.logger = logging.getLogger()

    async def send_audio(self, file_path, segment_number):
        AUTHORIZATION = os.getenv('AUTHORIZATION')
        prod_mode = int(os.getenv('PROD_MODE'))
        
        # Create an SSL context to disable SSL verification if prod_mode is 0
        if prod_mode == 0:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        else:
            ssl_context = ssl.create_default_context()

        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(connector=connector) as session:
            with open(file_path, 'rb') as file:
                data = aiohttp.FormData()
                data.add_field('file', file, filename=os.path.basename(file_path))
                data.add_field('segment', str(segment_number))
                async with session.post(self.server_url, data=data, headers={'Authorization': AUTHORIZATION}) as response:
                    self.logger.info(f"Status Code: {response.status}")

                    try:
                        print(f"Segment {segment_number} sent asynchronously")
                        response_json = await response.json()
                        if response.status == 200:
                            transcription = response_json.get('transcription', 'No transcription found')
                            self.logger.info(f"Transcription: {transcription}")
                        else:
                            error_message = response_json.get('error', 'Unknown error')
                            reason = response_json.get('reason', 'No reason provided')
                            self.logger.error(f"Error: {error_message}")
                            self.logger.error(f"Reason: {reason}")
                    except aiohttp.ContentTypeError:
                        self.logger.error("Failed to parse response as JSON")

        return response.status
