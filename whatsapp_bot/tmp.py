from twilio.rest import Client
import sys
import os

account_sid = os.environ['TWILIO_SID']
auth_token = os.environ['TWILIO_AUTH']
client = Client(account_sid, auth_token)
msg = client.messages.create(
    media_url=['https://vf-coaching-app.s3.us-east-2.amazonaws.com/output.ogg'],
    from_='whatsapp:+14155238886',
    to='whatsapp:+13096608065'
)
print(msg)
# message = client.messages(sys.argv[1]).fetch()
# print(message.status)
# error_code = message.error_code
# error_message = message.error_message
# print(str(message))
#
# print("Message SID:", message.sid)
# print("Error Code:", error_code)
# print("Error Message:", error_message)
