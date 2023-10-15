from twilio.rest import Client
import os
account_sid = os.environ['TWILIO_SID']
auth_token = os.environ['TWILIO_AUTH']
client = Client(account_sid, auth_token)

def send_message(to: str, message: str) -> None:
    '''
    Send message to a Telegram user.
    Parameters:
        - to(str): sender whatsapp number in this whatsapp:+919558515995 form
        - message(str): text message to send
    Returns:
        - None
    '''

    _ = client.messages.create(
        from_='whatsapp:+14155238886',
        body=message,
        to=to
    )
