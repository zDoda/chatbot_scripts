import os
import uuid

import openai
import requests
from requests.auth import HTTPBasicAuth
import soundfile as sf

account_sid = os.environ['TWILIO_SID']
auth_token = os.environ['TWILIO_AUTH']
openai.api_key = os.environ['OPENAI_API_KEY']

def chat_completion(prompt: str) -> str:
    try:
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        )

        return completion['choices'][0]['message']['content']
    except:
        return "error"

def transcript_audio(media_url: str) -> dict:
    try:
        ogg_file_path = f'{uuid.uuid1()}.ogg'
        data = requests.get(url=media_url, auth=HTTPBasicAuth(account_sid, auth_token))
        print('1')
        with open(ogg_file_path, 'wb') as file:
            file.write(data.content)
        print('2')
        audio_data, sample_rate = sf.read(ogg_file_path)
        print('3')
        mp3_file_path = f'{uuid.uuid1()}.mp3'
        sf.write(mp3_file_path, audio_data, sample_rate)
        audio_file = open(mp3_file_path, 'rb')
        os.unlink(ogg_file_path)
        os.unlink(mp3_file_path)
        transcript = openai.Audio.transcribe(
            'whisper-1', audio_file, api_key=os.environ['OPENAI_API_KEY'])
        return {
            'status': 1,
            'transcript': transcript['text']
        }
    except Exception as e:
        print('Error at transcript_audio...')
        print(e)
        return {
            'status': 0,
            'transcript': transcript['text']
        }

