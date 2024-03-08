from flask import Flask, request, jsonify
import slack
import os

import openai_api
app = Flask(__name__)

client = slack.WebClient(token=os.environ['SLACK_API_KEY'])

BOT_ID = client.api_call("auth.test")['user_id']
senders = {}


def send_slack_message(channel_id, text):
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=text
        )
        print(text)
        return response
    except:
        print("Error sending message: 'error'")


@app.route('/slack/events', methods=['POST'])
def slack_events():
    slack_event = request.json.get('event', {})
    print(slack_event)
    channel_type = slack_event.get('channel_type', '')
    msg = slack_event.get('type')
    user = slack_event.get('user', '')
    if msg == 'message' and channel_type == 'im' and 'bot_id' not in slack_event:
        user_message = slack_event.get('text', '')
        bot_msg = ''
        if user in senders:
            bot_msg = openai_api.assistant_estimate_chat(
                user_message, user, senders)
        else:
            thread_id = openai_api.new_chat_thread()
            senders[user] = {}
            senders[user]['thread'] = thread_id
            bot_msg = openai_api.assistant_estimate_chat(
                user_message, user, senders)

        channel_id = slack_event.get('channel')
        send_slack_message(channel_id, bot_msg)


if __name__ == '__main__':
    app.run(debug=True, port=3000)
