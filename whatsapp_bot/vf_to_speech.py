import requests
import os
from twilio.rest import Client
import boto3
from pydub import AudioSegment
#import shutil
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

# # Load the MP3 file
mp3_file = AudioSegment.from_file("output.mp3", format="mp3")
#
# # Convert to OGG format
mp3_file.export("output.ogg", format="ogg", codec="libopus")
# shutil.move(f'{os.getcwd()}/output.ogg', '/opt/lampp/htdocs/tmp/output.ogg')
#
s3=boto3.client('s3')
with open("output.ogg", "rb") as f:
    s3.upload_fileobj(f, 'vf-coaching-app', 'output.ogg')

account_sid = os.environ['TWILIO_SID']
auth_token = os.environ['TWILIO_AUTH']
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  to='whatsapp:+13096608065',
  media_url=['https://vf-coaching-app.s3.us-east-2.amazonaws.com/output.ogg'],
  body='test message'
)

print(message.sid)
print(message.media._uri)
#message = client.messages(message.sid).fetch()
print(message.status)
