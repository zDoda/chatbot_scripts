from flask import Flask, request
from numpy import who
from twilio_api import send_button_message, send_message, send_audio_message
from open_api import transcript_audio, new_chat_thread, assistant_send_chat
from voiceflow_api import send_vf_msg
import json
#Whatsapp
app = Flask(__name__)
senders = {}

file_path = "users.json"

try:
    with open(file_path, "r") as json_file:
        senders = json.load(json_file)
    print("JSON file successfully loaded.")
    print("Data from file:")
    print(senders)

except FileNotFoundError:
    print(f"File '{file_path}' not found.")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON in '{file_path}': {e}")
except Exception as ex:
    print(f"An error occurred: {ex}")

@app.route('/whatsapp', methods=['POST'])
def twilio():
    global senders
    try:
        data = request.form.to_dict()
        query = data['Body']
        sender_id = data['From']
        print(f'Sender id - {sender_id}')
        payload = ""
#        try:
#            payload = data['Message']['persistent_action']['payload']
#        except Exception as ex:
#            print(f"An error occurred: {ex}")
        response = "error"
        if sender_id in senders:
            if senders[sender_id]['setup']:
                new_user(sender_id, query)#, payload)
            else:
                if 'MediaUrl0' in data.keys():
                    transcript = transcript_audio(data['MediaUrl0'])
                    if transcript['status'] == 1:
                        #response,senders = send_vf_msg(transcript['transcript'], sender_id, senders)
                        response = assistant_send_chat(transcript['transcript'], sender_id, senders)
                        print(response)
                        if senders[sender_id]['botOption']:
                            send_audio_message(sender_id, response)
                        else:
                            send_message(sender_id, response)
                    else:
                        print("error")
                else:
                    print(f'Query - {query}')
                    #response,senders = send_vf_msg(query, sender_id, senders)
                    response = assistant_send_chat(query, sender_id, senders)
                    print(response)
                    if senders[sender_id]['botOption']:
                        send_audio_message(sender_id, response)
                    else:
                        send_message(sender_id, response)

        else:
            senders[sender_id] = {}
            print(f'New Sender')
            new_user(sender_id, query)#, payload)
        print('Message sent.')
        senders[sender_id]['messageCount'] += 1
        print(senders[sender_id]['messageCount'])
        if senders[sender_id]['messageCount']>senders[sender_id]['num_til_next_ad']:
            send_message(sender_id, 'This chatbot is built by Hype Digitaly AI, check us out @ www.hypedigitaly.ai')
            senders[sender_id]['messageCount'] = 0
            senders[sender_id]['num_til_next_ad'] += 10

    except Exception as e:
        print(e)
    with open('users.json', 'w') as json_file:
        json.dump(senders,json_file)
    return 'OK', 200

def new_user(sender_id: str, query: str):#, payload: str):
    global senders
    senders[sender_id]['setup'] = True
    if 'botSetup' not in senders[sender_id]:
        senders[sender_id]['botSetup'] = True
        senders[sender_id]['botDefault'] = 0
        send_message(sender_id, 'If you want me to respond in Voice-notes, respond with VOICE. If you want me to respond with Text chat, respond with TEXT')
        #send_button_message(sender_id)
        return 0
    if senders[sender_id]['botSetup']: # and payload != None:
        #if payload == 'audio':
        #    senders[sender_id]['botOption'] = True
        #elif payload == 'text':
        senders[sender_id]['botOption'] = False
        query_lower = query.lower()
        if "voice" == query_lower:
            senders[sender_id]['botOption'] = True
        elif "text" == query_lower:
            senders[sender_id]['botOption'] = False
        else:
            if senders[sender_id]['botDefault'] < 2:
                send_message(sender_id, "Unable to read your response, please type VOICE or TEXT")
                senders[sender_id]['botDefault'] += 1
                return 0
            else:
                send_message(sender_id, "Unable to read your response, defaulted to TEXT")
                senders[sender_id]['botOption'] = False
        senders[sender_id]['botSetup'] = False
        senders[sender_id]['setup'] = False
        senders[sender_id]['vfSetup'] = True
        senders[sender_id]['messageCount'] = 0
        senders[sender_id]['num_til_next_ad'] = 5
        if senders[sender_id]['botOption']:
            send_message(sender_id, "You have chosen voice-notes, feel free to text or record a voicenote any questions to me")
        else:
            send_message(sender_id, "You have chosen text, feel free to text or record a voicenote any questions to me")
        send_message(sender_id, "You can change change my response setting by asking me to switch")
        #response,senders = send_vf_msg('', sender_id, senders)
        senders = new_chat_thread(senders, sender_id)
        #send_message(sender_id, response)

if __name__ == "__main__":
    app.run(debug=True)
