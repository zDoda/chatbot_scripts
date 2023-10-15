from twilio.rest import Client
import sys
import os

account_sid = os.environ['TWILIO_SID']
auth_token = os.environ['TWILIO_AUTH']
client = Client(account_sid, auth_token)
message = client.messages(sys.argv[1]).fetch()
print(message.status)
error_code = message.error_code
error_message = message.error_message
print(str(message))

print("Message SID:", message.sid)
print("Error Code:", error_code)
print("Error Message:", error_message)
