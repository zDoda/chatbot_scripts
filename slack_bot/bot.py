import slack
import os
from flask import Flask, request, Response, jsonify
from slackeventsapi import SlackEventAdapter
import requests
import json
from threading import Thread
import asyncio
from pricing import estimate_prompt, pricing_dir
import openai

client = slack.WebClient(token=os.environ['SLACK_API_KEY'])
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'],'/slack/events',app)
BOT_ID = client.api_call("auth.test")['user_id']

estimate_user_dir = {}
estimate_str = ["", ""]
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


# creating an estimate
@app.route('/e', methods=['POST'])
def estimate():
    data = request.form
    thr = Thread(target=lambda: asyncio.run(estimate_task(data)))
    thr.start()

    # Respond to Slack immediately
    example = {
        'response_type': 'in_channel',
        'text': 'Working on it. I am creating your estimate...',
    }
    return jsonify(example), 200

def print_helper(num, price, price2, header, header2="", header3=""):
    global estimate_str
    if header3 != "" and header2 != "":
        estimate_str[0] += (str(header) + " - " + str(header2) + " - " + str(header3)
                     + ":\n"
                     +  " (# of Windows: " + str(num)
                     +  " + Price: " + str(price)
                     +  " = " + f'{num*price2:.2f}'+ " )\n")

        estimate_str[1] += (str(header) + " - " + str(header2) + " - " + str(header3)
                     + ":\n"
                     +  " (# of Windows: " + str(num)
                     +  " + Price: " + str(price)
                     +  " = " + f'{num*price2:.2f}'+ " )\n")

    elif header2 != "":
        estimate_str[0] += (str(header) + " - " + str(header2)
                     + ":\n"
                     +  " (# of Windows: " + str(num)
                     +  " + Price: " + str(price)
                     +  " = " + f'{num*price2:.2f}'+ " )\n")

        estimate_str[1] += (str(header)  + " - " + str(header2)
                     + ":\n"
                     +  " (# of Windows: " + str(num)
                     +  " + Price: " + str(price)
                     +  " = " + f'{num*price2:.2f}'+ " )\n")

    else:
        estimate_str[0] += (str(header) + ":\n"
                     +  " (# of Windows: " + str(num)
                     +  " + Price: " + str(price)
                     +  " = " + f'{num*price2:.2f}'+ " )\n")

        estimate_str[1] += (str(header) + ":\n"
                     +  " (# of Windows: " + str(num)
                     +  " + Price: " + str(price)
                     +  " = " + f'{num*price2:.2f}'+ " )\n")

def window_sum(data,user_id):
    # Calculate the estimate for each category and update estimate_user_dir
    global estimate_str
    for x in data:
        if isinstance(data[x], dict):
            for y in data[x]:
                if isinstance(data[x][y], dict):
                    for z in data[x][y]:
                        if data[x][y][z] != 0:
                            estimate_user_dir[str(user_id)]['ext'] += data[x][y][z] * pricing_dir[x][y][z]
                            estimate_user_dir[str(user_id)]['both'] += data[x][y][z] * pricing_dir[x][y][z]
                            print_helper(
                                data[x][y][z],
                                pricing_dir[x][y][z],
                                pricing_dir[x][y][z],
                                x,
                                y,
                                z
                            )
                else:
                    if isinstance(pricing_dir[x][y],(int,float)):
                        if data[x][y] != 0:
                            estimate_user_dir[str(user_id)]['ext'] += data[x][y] * pricing_dir[x][y]
                            estimate_user_dir[str(user_id)]['both'] += data[x][y] * pricing_dir[x][y]
                            print_helper(
                                data[x][y],
                                pricing_dir[x][y],
                                pricing_dir[x][y],
                                x,
                                y
                            )
                    else:
                        if data[x][y] != 0:
                            estimate_user_dir[str(user_id)]['ext'] += data[x][y] * pricing_dir[x][y][0]
                            estimate_user_dir[str(user_id)]['both'] += data[x][y] * pricing_dir[x][y][1]
                            print_helper(
                                data[x][y],
                                pricing_dir[x][y][0],
                                pricing_dir[x][y][1],
                                x,
                                y
                            )
        else:
            if isinstance(pricing_dir[x],(int,float)):
                if data[x] != 0:
                    estimate_user_dir[str(user_id)]['ext'] += data[x] * pricing_dir[x]
                    estimate_user_dir[str(user_id)]['both'] += data[x] * pricing_dir[x]
                    print_helper(data[x],
                        pricing_dir[x],
                        pricing_dir[x],
                        x
                    )
            else:
                if data[x] != 0:
                    estimate_user_dir[str(user_id)]['ext'] += data[x] * pricing_dir[x][0]
                    estimate_user_dir[str(user_id)]['both'] += data[x] * pricing_dir[x][1]
                    print_helper(data[x],
                        pricing_dir[x][0],
                        pricing_dir[x][1],
                        x
                    )

def estimate_tax(user_id):
    both_tax=(pricing_dir['tax']['tps']*estimate_user_dir[str(user_id)]['both']) + (pricing_dir['tax']['tvq']*estimate_user_dir[str(user_id)]['both'])
    ext_tax=(pricing_dir['tax']['tps']*estimate_user_dir[str(user_id)]['ext']) + (pricing_dir['tax']['tvq']*estimate_user_dir[str(user_id)]['ext'])
    return (ext_tax+estimate_user_dir[str(user_id)]['ext'],both_tax+estimate_user_dir[str(user_id)]['both'])

async def estimate_task(data):
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    text = data.get('text')
    estimate_user_dir[str(user_id)] = {}
    estimate_user_dir[str(user_id)]['ext'] = 0.0
    estimate_user_dir[str(user_id)]['both'] = 0.0
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": estimate_prompt},
            {"role": "user", "content": text}
        ]
    )
    data = json.loads(response['choices'][0]['message']['content'])
    print(str(response))
    window_sum(data,user_id)
    print_estimate(channel_id,user_id)

def print_estimate(channel_id, user_id):
    ext_total,both_total = estimate_tax(user_id)
    _tmp = ""
    _tmp += "External Only: \n" + estimate_str[0] + f"Ext: {estimate_user_dir[str(user_id)]['ext']:.2f},w/ Tax: {ext_total:.2f}\n"
    _tmp += "External & Internal:  \n" + estimate_str[1] + f"Ext+Int: {estimate_user_dir[str(user_id)]['both']:.2f}\n w/ Tax: {both_total:.2f}"
    client.chat_postMessage(
        channel=channel_id,
        text=_tmp
    )

if __name__ == "__main__":
    app.run(debug=True, port=3000)
