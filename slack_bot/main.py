from flask import Flask, request, jsonify
import slack
import os
import json
from threading import Thread
import bot
import asyncio

import openai_api
app = Flask(__name__)

slack_client = slack.WebClient(token=os.environ['SLACK_API_KEY'])

BOT_ID = slack_client.api_call("auth.test")['user_id']
senders = {}
owner_id = 'U06LVBK8VGD'
file_path = "users.json"

try:
    with open(file_path, "r") as json_file:
        bot.estimate_user_dir = json.load(json_file)
    print("JSON file successfully loaded.")
    print("Data from file:")
    print(bot.estimate_user_dir)

except FileNotFoundError:
    print(f"File '{file_path}' not found.")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON in '{file_path}': {e}")
except Exception as ex:
    print(f"An error occurred: {ex}")


def send_slack_message(channel_id, text):
    try:
        response = slack_client.chat_postMessage(
            channel=channel_id,
            text=text
        )
        return response
    except:
        print("Error sending message: 'error'")


@app.route('/slack/events', methods=['POST'])
def slack_events():
    if 'challenge' in request.json:
        return jsonify({'challenge': request.json['challenge']})
    slack_event = request.json.get('event', {})

    thr = Thread(target=lambda: asyncio.run(task(slack_event)))
    thr.start()

    # Respond to Slack immediately
    return jsonify({'ok': 'true'}), 200


async def task(slack_event):
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
        with open(file_path, 'w') as json_file:
            json.dump(bot.estimate_user_dir, json_file)

if __name__ == '__main__':
    app.run(debug=True, port=3000)
