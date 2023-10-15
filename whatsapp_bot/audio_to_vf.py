from flask import Flask, request
from twilio_api import send_message
from open_api import transcript_audio

#Whatsapp
app = Flask(__name__)
@app.route('/whatsapp', methods=['POST'])
def twilio():
    try:
        data = request.form.to_dict()
        print(data)
        query = data['Body']
        sender_id = data['From']
        print(f'Sender id - {sender_id}')
        # TODO
        if 'MediaUrl0' in data.keys():
            transcript = transcript_audio(data['MediaUrl0'])
            if transcript['status'] == 1:
                print(f'Query - {transcript["transcript"]}')
                send_message(sender_id, f'Query - {transcript["transcript"]}')
                #response = chat_completion(transcript['transcript'])
            else:
                print("error")
        else:
            print(f'Query - {query}')
            #response = chat_completion(query)
        #print(f'Response - {response}')
        #print('Message sent.')
    except Exception as e:
        print(e)

    return 'OK', 200

if __name__ == "__main__":
    app.run(debug=True)
