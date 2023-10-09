import slack
import os
from flask import Flask
from slackeventsapi import SlackEventAdapter
import requests
import json

client = slack.WebClient(token=os.environ['SLACK_API_KEY'])
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'],'/slack/events',app)
BOT_ID = client.api_call("auth.test")['user_id']
user_conversation = []
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if user_id != BOT_ID:
        url = f"https://general-runtime.voiceflow.com/state/user/{user_id}/interact?logs=off"
        headers={
            "Authorization": os.environ["VF_API_KEY"],
            "accept": "application/json",
            "content-type": "application/json",
        }
        #response = requests.delete(url,headers={"Authorization": os.environ["VF_API_KEY"]})
        if user_id not in user_conversation:
            payload_vf = {
                "action": { "type": "launch" },
                "config": {
                    "tts": False,
                    "stripSSML": True,
                    "stopAll": True,
                    "excludeTypes": ["block", "debug", "flow"]
                }
            }
            response = requests.post(url=url, json=payload_vf, headers=headers)
            user_conversation.append(user_id)
            resp_dir = json.loads(response.text)
            resp_text = resp_dir[0]['payload']['message']
            print(response.text)
        else:
            payload_vf = {
                "action": {
                    "type": "text",
                    "payload": text
                },
                "config": {
                    "tts": False,
                    "stripSSML": True,
                    "stopAll": True,
                    "excludeTypes": ["block", "debug", "flow"]
                }
            }
            response = requests.post(url=url, json=payload_vf, headers=headers)
            resp_dir = json.loads(response.text)
            resp_text = ""
            if resp_dir[-1]['type'] == "text":
                resp_text = resp_dir[-1]['payload']['message']
            print(response.text)
        #launch message
        client.chat_postMessage(channel=channel_id, text=resp_text)
        #print(resp_text)
        resp_dir = {}
        resp_text = ""



if __name__ == "__main__":
    app.run(debug=True, port=3000)
