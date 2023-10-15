from flask import Flask, request
from twilio_api import send_message
from open_api import transcript_audio
from voiceflow_api import send_vf_msg
#Whatsapp
app = Flask(__name__)
senders = []
@app.route('/whatsapp', methods=['POST'])
def twilio():
    global senders
    try:
        data = request.form.to_dict()
        print(data)
        query = data['Body']
        sender_id = data['From']
        print(f'Sender id - {sender_id}')
        response = "error"
        if 'MediaUrl0' in data.keys():
            transcript = transcript_audio(data['MediaUrl0'])
            if transcript['status'] == 1:
                print(f'Query - {transcript["transcript"]}')
                response,senders = send_vf_msg(transcript['transcript'], sender_id, senders)
                send_message(sender_id, response)
            else:
                print("error")
        else:
            print(f'Query - {query}')
            response,senders = send_vf_msg(query, sender_id, senders)
            send_message(sender_id, response)

        print('Message sent.')
        print(f'Response - {response}')
    except Exception as e:
        print(e)

    return 'OK', 200

if __name__ == "__main__":
    app.run(debug=True)
