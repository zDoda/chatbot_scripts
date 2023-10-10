import slack
import os
from flask import Flask, request, Response, jsonify
from slackeventsapi import SlackEventAdapter
import requests
import json
from threading import Thread
import asyncio

client = slack.WebClient(token=os.environ['SLACK_API_KEY'])
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'],'/slack/events',app)
BOT_ID = client.api_call("auth.test")['user_id']
user_conversation = []

# @slack_event_adapter.on('message')
# def message(payload):
#     event = payload.get('event', {})
#     channel_id = event.get('channel')
#     user_id = event.get('user')
#     text = event.get('text')
#     if user_id != BOT_ID:
#         url = f"https://general-runtime.voiceflow.com/state/user/{user_id}/interact?logs=off"
#         headers={
#             "Authorization": os.environ["VF_API_KEY"],
#             "accept": "application/json",
#             "content-type": "application/json",
#         }
#         #response = requests.delete(url,headers={"Authorization": os.environ["VF_API_KEY"]})
#         if user_id not in user_conversation:
#             payload_vf = {
#                 "action": { "type": "launch" },
#                 "config": {
#                     "tts": False,
#                     "stripSSML": True,
#                     "stopAll": True,
#                     "excludeTypes": ["block", "debug", "flow"]
#                 }
#             }
#             response = requests.post(url=url, json=payload_vf, headers=headers)
#             user_conversation.append(user_id)
#             resp_dir = json.loads(response.text)
#             resp_text = resp_dir[0]['payload']['message']
#             print(response.text)
#
#         else:
#             payload_vf = {
#                 "action": {
#                     "type": "text",
#                     "payload": text
#                 }, "config": {
#                     "tts": False,
#                     "stripSSML": True,
#                     "stopAll": True,
#                     "excludeTypes": ["block", "debug", "flow"]
#                 }
#             }
#             response = requests.post(url=url, json=payload_vf, headers=headers)
#             resp_dir = json.loads(response.text)
#             resp_text = ""
#             if resp_dir[-1]['type'] == "text":
#                 resp_text = resp_dir[-1]['payload']['message']
#             print(response.text)
#
#         #launch message
#         client.chat_postMessage(channel=channel_id, text=resp_text)
#         #print(resp_text)
#         resp_dir = {}
#         resp_text = ""


# Ask a question
@app.route('/q', methods=['POST'])
def question():
    data = request.form

    thr = Thread(target=lambda: asyncio.run(task(data)))
    thr.start()

    # Respond to Slack immediately
    example = {
        'response_type': 'in_channel',
        'text': 'Working on it. I am searching for your answer...',
    }
    return jsonify(example), 200

async def task(data):
    channel_id = data.get('channel_id')
    text = data.get('text')

    url = "https://general-runtime.voiceflow.com/knowledge-base/query"
    payload = {
        "chunkLimit": 4,
        "synthesis": True,
        "settings": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.1,
            "system": "You are an AI FAQ assistant. Information will be provided to help answer the user's questions. Always summarize your response to be as brief as possible and be extremely concise. Your responses should be fewer than a couple of sentences. Do not reference the material provided in your response."
        },
        "question": f'{text}'
    }
    headers={
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": os.environ["VF_API_KEY"]
    }
    response = requests.post(url, json=payload, headers=headers)
    temp = json.loads(response.text)
    if temp['output'] is None:
        client.chat_postMessage(channel=channel_id, text="Sorry I can't answer that question, please ask your manager")
    else:
        client.chat_postMessage(channel=channel_id, text=response.json()['output'])
if __name__ == "__main__":
    app.run(debug=True, port=3000)
