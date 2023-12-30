from twilio.rest import Client
import os
import requests
from twilio.rest import Client
import boto3
from pydub import AudioSegment
account_sid = os.environ['TWILIO_SID']
auth_token = os.environ['TWILIO_AUTH']
client = Client(account_sid, auth_token)

def send_message(to: str, message: str) -> None:
    '''
    Send message to a whatsapp user.
    Parameters:
        - to(str): sender whatsapp number in this whatsapp:+919558515995 form
        - message(str): text message to send
    Returns:
        - None
    '''

    _ = client.messages.create(
        #from_='whatsapp:+14155238886', #twilio sandbox
        from_='whatsapp:+18447469113',
        body=message,
        to=to
    )

def send_button_message(to: str) -> None:
    message = {
    'persistent_action': [
        {
            'type': 'reply',
            'payload': 'audio',
            'title': 'Voice Notes'
        }
    ]
}
    _ = client.messages.create(
        from_='whatsapp:+14155238886', #twilio sandbox
#        from_='whatsapp:+18447469113',
        body="How would you like me to respond?",
        to=to,
        persistent_action=message['persistent_action']
    )

def send_audio_message(to: str, message: str) -> None:
    '''
    Send message to a whatsapp user.
    Parameters:
        - to(str): sender whatsapp number in this whatsapp:+919558515995 form
        - fessage(str): text message to send
    Returns:
        - None
    '''
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/I6ug5epEXF0LpaHEqxFY"

    headers = {
      "Accept": "audio/mpeg",
      "Content-Type": "application/json",
      "xi-api-key": f'{os.environ["ELEVEN_API_KEY"]}'
    }

    data = {
      "text": f'{message}',
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

    #Load the MP3 file
    mp3_file = AudioSegment.from_file("output.mp3", format="mp3")

    # Convert to OGG format
    mp3_file.export("output.ogg", format="ogg", codec="libopus")
    # Modify the S3 object's metadata (e.g., Content-Type) here
    s3 = boto3.client('s3')

    object_name = os.path.basename('output.ogg')
    s3.upload_file('output.ogg', 'vf-coaching-app', object_name, ExtraArgs={'ContentType': "audio/ogg"})
    _ = client.messages.create(
        media_url=['http://vf-coaching-app.s3.us-east-2.amazonaws.com/output.ogg'],
        #from_='whatsapp:+14155238886', #twilio sandbox
        from_='whatsapp:+18447469113',
        to=to
    )
