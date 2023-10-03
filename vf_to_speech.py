import requests
import os
from twilio.rest import Client
import boto3

CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"

headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": f'{os.environ["ELEVEN_API_KEY"]}'
}

data = {
  "text": "Hi! My name is Bella, nice to meet you!",
  "model_id": "eleven_monolingual_v1",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.5
  }
}

response = requests.post(url, json=data, headers=headers)
with open('output.mp3', 'wb') as f:
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            f.write(chunk)

s3=boto3.client('s3')
with open("output.mp3", "rb") as f:
    s3.upload_fileobj(f, 'vf-coaching-app', 'output.mp3')

account_sid = 'AC96e137aac7d260ca7a9601c4521d827e'
auth_token = '4ad6485729afe32b80eb731eba9af5e6'
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  to='whatsapp:+13096608065',
  media_url=["https://vf-coaching-app.s3.us-east-2.amazonaws.com/output.mp3"]
)

print(message.sid)
