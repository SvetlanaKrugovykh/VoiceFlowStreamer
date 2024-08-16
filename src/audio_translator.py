import aiohttp
import time
import os
import json
from .logger_setup import setup_logger


translator_logger = setup_logger('translator', 'translators.log')

class AudioTranslator:
    def __init__(self):
        self.translator_url = os.getenv('TRANSLATOR_URL') 
        self.connector = None
        self.logger = translator_logger  

    async def translate_text(self, transcription, headers):
        async with aiohttp.ClientSession(connector=self.connector) as session:
            try:
                start_time = time.time()
                timeout = aiohttp.ClientTimeout(total=None)  

                service_id = os.getenv('SERVICE_TRANSLATE_ID')
                client_id = os.getenv('CLIENT_ID')
                email = os.getenv('EMAIL')
                authorization = os.getenv('AUTHORIZATION_TRANSLATE')
                direction = os.getenv('DIRECTION')
                
                data = {
                    'serviceId': service_id,
                    'clientId': client_id,
                    'email': email,
                    'direction': direction,
                    'text': transcription,
                    'token': authorization
                }
                headers['Content-Type'] = 'application/json' 
                headers['Authorization'] = authorization

                json_data = json.dumps(data)

                async with session.post(self.translator_url, data=json_data, headers=headers, timeout=timeout) as response:
                    status_code = response.status
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    print(f"Elapsed Time: {elapsed_time}")

                    if status_code != 200:
                        self.logger.info(f"Status Code: {status_code}")
                    else:
                        response_text = await response.text()
                        response_data = json.loads(response_text)
                        translated_text = response_data.get('replyData', {}).get('translated_text', [""])[0]
                        self.logger.info(f"Translated Text: {translated_text}")
                        return translated_text
            except Exception as e:
                self.logger.error(f"Error: {e}")

    async def process_transcription(self, translated_text, headers):
        if isinstance(translated_text, list):
            transcription = next((text for text in translated_text if text), 'No transcription found')
        elif isinstance(translated_text, str):
            transcription = translated_text
        else:
            transcription = 'No transcription found'

        self.logger.info(f": {transcription}")

        if transcription != 'No transcription found':
            translated_text = await self.translate_text(transcription, headers)
            if translated_text:
                self.logger.info(f"Translated Text: {translated_text}")