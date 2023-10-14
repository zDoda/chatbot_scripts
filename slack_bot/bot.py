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

def window_sum(data,user_id):
    # Calculate the estimate for each category and update estimate_user_dir
    estimate_user_dir[str(user_id)]['ext'] += (
        (data['fixe']['TP'] * pricing_dir['fixe']['TP'][0]) +
        (data['fixe']['P'] * pricing_dir['fixe']['P'][0]) +
        (data['fixe']['M'] * pricing_dir['fixe']['M'][0]) +
        (data['fixe']['G'] * pricing_dir['fixe']['G'][0]) +
        (data['fixe']['TG'] * pricing_dir['fixe']['TG'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['fixe']['TP'] * pricing_dir['fixe']['TP'][1]) +
        (data['fixe']['P'] * pricing_dir['fixe']['P'][1]) +
        (data['fixe']['M'] * pricing_dir['fixe']['M'][1]) +
        (data['fixe']['G'] * pricing_dir['fixe']['G'][1]) +
        (data['fixe']['TG'] * pricing_dir['fixe']['TG'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['manivelle']['P'] * pricing_dir['manivelle']['P'][0]) +
        (data['manivelle']['M'] * pricing_dir['manivelle']['M'][0]) +
        (data['manivelle']['G'] * pricing_dir['manivelle']['G'][0]) +
        (data['manivelle']['TG'] * pricing_dir['manivelle']['TG'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['manivelle']['P'] * pricing_dir['manivelle']['P'][1]) +
        (data['manivelle']['M'] * pricing_dir['manivelle']['M'][1]) +
        (data['manivelle']['G'] * pricing_dir['manivelle']['G'][1]) +
        (data['manivelle']['TG'] * pricing_dir['manivelle']['TG'][1])
    )
    estimate_user_dir[str(user_id)]['ext'] += (
        (data['guillotine_simple']['P'] * pricing_dir['guillotine_simple']['P'][0]) +
        (data['guillotine_simple']['M'] * pricing_dir['guillotine_simple']['M'][0]) +
        (data['guillotine_simple']['G'] * pricing_dir['guillotine_simple']['G'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['guillotine_simple']['P'] * pricing_dir['guillotine_simple']['P'][1]) +
        (data['guillotine_simple']['M'] * pricing_dir['guillotine_simple']['M'][1]) +
        (data['guillotine_simple']['G'] * pricing_dir['guillotine_simple']['G'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['guillotine_double']['P'] * pricing_dir['guillotine_double']['P'][0]) +
        (data['guillotine_double']['M'] * pricing_dir['guillotine_double']['M'][0]) +
        (data['guillotine_double']['G'] * pricing_dir['guillotine_double']['G'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['guillotine_double']['P'] * pricing_dir['guillotine_double']['P'][1]) +
        (data['guillotine_double']['M'] * pricing_dir['guillotine_double']['M'][1]) +
        (data['guillotine_double']['G'] * pricing_dir['guillotine_double']['G'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['couissante_simple']['TP'] * pricing_dir['couissante_simple']['TP'][0]) +
        (data['couissante_simple']['P'] * pricing_dir['couissante_simple']['P'][0]) +
        (data['couissante_simple']['M'] * pricing_dir['couissante_simple']['M'][0]) +
        (data['couissante_simple']['G'] * pricing_dir['couissante_simple']['G'][0]) +
        (data['couissante_simple']['SS'] * pricing_dir['couissante_simple']['SS'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['couissante_simple']['TP'] * pricing_dir['couissante_simple']['TP'][1]) +
        (data['couissante_simple']['P'] * pricing_dir['couissante_simple']['P'][1]) +
        (data['couissante_simple']['M'] * pricing_dir['couissante_simple']['M'][1]) +
        (data['couissante_simple']['G'] * pricing_dir['couissante_simple']['G'][1]) +
        (data['couissante_simple']['SS'] * pricing_dir['couissante_simple']['SS'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['couissante_double']['TP'] * pricing_dir['couissante_double']['TP'][0]) +
        (data['couissante_double']['P'] * pricing_dir['couissante_double']['P'][0]) +
        (data['couissante_double']['M'] * pricing_dir['couissante_double']['M'][0]) +
        (data['couissante_double']['G'] * pricing_dir['couissante_double']['G'][0]) +
        (data['couissante_double']['SS'] * pricing_dir['couissante_double']['SS'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['couissante_double']['TP'] * pricing_dir['couissante_double']['TP'][1]) +
        (data['couissante_double']['P'] * pricing_dir['couissante_double']['P'][1]) +
        (data['couissante_double']['M'] * pricing_dir['couissante_double']['M'][1]) +
        (data['couissante_double']['G'] * pricing_dir['couissante_double']['G'][1]) +
        (data['couissante_double']['SS'] * pricing_dir['couissante_double']['SS'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (data['francaise'] * pricing_dir['francaise'][0])
    estimate_user_dir[str(user_id)]['both'] += (data['francaise'] * pricing_dir['francaise'][1])

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['puit_de_lumiere']['P'] * pricing_dir['puit_de_lumiere']['P'][0]) +
        (data['puit_de_lumiere']['M'] * pricing_dir['puit_de_lumiere']['M'][0]) +
        (data['puit_de_lumiere']['G'] * pricing_dir['puit_de_lumiere']['G'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['puit_de_lumiere']['P'] * pricing_dir['puit_de_lumiere']['P'][1]) +
        (data['puit_de_lumiere']['M'] * pricing_dir['puit_de_lumiere']['M'][1]) +
        (data['puit_de_lumiere']['G'] * pricing_dir['puit_de_lumiere']['G'][1])
    )

    estimate_user_dir[str(user_id)]['ext'] += (
        (data['porte_coulissante']['S'] * pricing_dir['porte_coulissante']['S'][0]) +
        (data['porte_coulissante']['D'] * pricing_dir['porte_coulissante']['D'][0])
    )
    estimate_user_dir[str(user_id)]['both'] += (
        (data['porte_coulissante']['S'] * pricing_dir['porte_coulissante']['S'][1]) +
        (data['porte_coulissante']['D'] * pricing_dir['porte_coulissante']['D'][1])
    )
    _tmp = (
        data['vider_les_gouttiere']['Facile'] * pricing_dir['vider_les_gouttiere']['Facile'] +
        data['vider_les_gouttiere']['Moyen'] * pricing_dir['vider_les_gouttiere']['Moyen'] +
        data['vider_les_gouttiere']['Difficile'] * pricing_dir['vider_les_gouttiere']['Difficile']
    )

    _tmp += ( data['laver_soffites'] * pricing_dir['laver_soffites'] )

    _tmp += data['installation_de_plaques'] * pricing_dir['installation_de_plaques']

    _tmp += (
        data['ampoules']['rdc'] * pricing_dir['ampoules']['rdc'] +
        data['ampoules']['etage'] * pricing_dir['ampoules']['etage']
    )

    _tmp += data['nettoyage_de_lumiere'] * pricing_dir['nettoyage_de_lumiere']

    _tmp += (
        data['lavage_a_pression']['sols']['asphalte'] * pricing_dir['lavage_a_pression']['sols']['asphalte'] +
        data['lavage_a_pression']['sols']['beton'] * pricing_dir['lavage_a_pression']['sols']['beton']
    )

    _tmp += data['lavage_a_pression']['murs'] * pricing_dir['lavage_a_pression']['murs']

    _tmp += (
        data['lavage_a_pression']['bois']['sols'] * pricing_dir['lavage_a_pression']['bois']['sols'] +
        data['lavage_a_pression']['bois']['cloture'] * pricing_dir['lavage_a_pression']['bois']['cloture'] +
        data['lavage_a_pression']['bois']['escalier'] * pricing_dir['lavage_a_pression']['bois']['escalier'] +
        data['lavage_a_pression']['bois']['rampes'] * pricing_dir['lavage_a_pression']['bois']['rampes']
    )

    _tmp += (
        data['lavage_a_pression']['pave_seulment'] * pricing_dir['lavage_a_pression']['pave_seulment'] +
        data['lavage_a_pression']['pave_sable_g'] * pricing_dir['lavage_a_pression']['pave_sable_g'] +
        data['lavage_a_pression']['pave_sable_p'] * pricing_dir['lavage_a_pression']['pave_sable_p']
    )

    _tmp += (
        data['nettoyage_de_murs']['P'] * pricing_dir['nettoyage_de_murs']['P'] +
        data['nettoyage_de_murs']['M'] * pricing_dir['nettoyage_de_murs']['M'] +
        data['nettoyage_de_murs']['G'] * pricing_dir['nettoyage_de_murs']['G']
    )

    _tmp += (
        data['nettoyage_de_stores']['P'] * pricing_dir['nettoyage_de_stores']['P'] +
        data['nettoyage_de_stores']['M'] * pricing_dir['nettoyage_de_stores']['M'] +
        data['nettoyage_de_stores']['G'] * pricing_dir['nettoyage_de_stores']['G']
    )

    _tmp += ( data['travaux_vip_heure'] * pricing_dir['travaux_vip_heure'] )
    estimate_user_dir[str(user_id)]['ext'] += _tmp
    estimate_user_dir[str(user_id)]['both'] += _tmp

def estimate_tax(user_id):
    both_tax=(pricing_dir['tax']['tps']*estimate_user_dir[str(user_id)]['both']) + (pricing_dir['tax']['tvq']*estimate_user_dir[str(user_id)]['both'])
    ext_tax=(pricing_dir['tax']['tps']*estimate_user_dir[str(user_id)]['ext']) + (pricing_dir['tax']['tvq']*estimate_user_dir[str(user_id)]['ext'])
    return (ext_tax+estimate_user_dir[str(user_id)]['ext'],both_tax+estimate_user_dir[str(user_id)]['both'])

async def estimate_task(data):
    channel_id = data.get('channel_id')
    user_id = data.get('user_id')
    text = data.get('text')
    estimate_user_dir[str(user_id)] = {}
    estimate_user_dir[str(user_id)]['ext'] = 0
    estimate_user_dir[str(user_id)]['both'] = 0
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
    ext_total,both_total = estimate_tax(user_id)
    client.chat_postMessage(channel=channel_id, text=f"Ext: {estimate_user_dir[str(user_id)]['ext']}, Ext+Int: {estimate_user_dir[str(user_id)]['both']}\nExt: {ext_total}, Ext+Int: {both_total}")

if __name__ == "__main__":
    app.run(debug=True, port=3000)
