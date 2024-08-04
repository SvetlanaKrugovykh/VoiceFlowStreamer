# src/audio_sender.py
import logging
from dotenv import load_dotenv
import os
import aiohttp
import asyncio
import ssl
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class AudioSender:
    def __init__(self, server_url):
        self.server_url = server_url
        logging.basicConfig(filename='transcriptions.log', level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')
        self.logger = logging.getLogger()

    async def send_audio(self, file_path, segment_number):
        THROUGH_AS = int(os.getenv('THROUGH_AS'))     
        clientId = os.getenv('CLIENT_ID')

        if clientId is None:
            self.logger.error("CLIENT_ID environment variable is not set")
            return 400
        
        data = aiohttp.FormData()
        data.add_field('clientId', clientId)
        data.add_field('segment_number', str(segment_number))
        
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")           
        else:
            data.add_field('file', open(file_path, 'rb'), filename=os.path.basename(file_path))

        if THROUGH_AS == 1:
            AUTHORIZATION = os.getenv('AUTHORIZATION')
            prod_mode = int(os.getenv('PROD_MODE', 0))
            serviceId = os.getenv('SERVICE_ID')

            if AUTHORIZATION is None or serviceId is None:
                self.logger.error("Missing environment variables for AUTHORIZATION or SERVICE_ID")
                return 400

            data.add_field('serviceId', serviceId)
            data.add_field('token', AUTHORIZATION)

            if prod_mode == 0:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            else:
                ssl_context = ssl.create_default_context()

            connector = aiohttp.TCPConnector(ssl=ssl_context)
            server_url = os.getenv('SERVER_URL')
        else:
            connector = aiohttp.TCPConnector()
            server_url = os.getenv('DIRECT_URL')
        
        if server_url is None:
            self.logger.error("SERVER_URL environment variable is not set")
            return 400      

        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                start_time = time.time()
                async with session.post(server_url, data=data) as response:
                    status_code = response.status
                    end_time = time.time()
                    elapsed_time = end_time - start_time

                    if status_code != 200:
                        self.logger.info(f"Status Code: {status_code}")

                    try:
                        response_json = await response.json()
                        if response.status == 200:
                            print(f'segment {segment_number} sent successfully in {elapsed_time:.2f} seconds')
                            translated_text = response_json.get('translated_text', None)
                            if isinstance(translated_text, list):
                                transcription = next((text for text in translated_text if text), 'No transcription found')
                            elif isinstance(translated_text, str):
                                transcription = translated_text
                            else:
                                transcription = 'No transcription found'

                            self.logger.info(f"Transcription: {transcription}")                        
                        else:
                            error_message = response_json.get('error', 'Unknown error')
                            reason = response_json.get('reason', 'No reason provided')
                            self.logger.error(f"Error: {error_message}")
                            self.logger.error(f"Reason: {reason}")
                    except aiohttp.ContentTypeError:
                        self.logger.error("Failed to parse response as JSON")

            except aiohttp.ClientError as e:
                self.logger.error(f"ClientError occurred: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error occurred: {e}")

        return response.status