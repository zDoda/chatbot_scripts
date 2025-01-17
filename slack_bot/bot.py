import slack
import os
from flask import Flask, request, jsonify
from slackeventsapi import SlackEventAdapter
import json
from threading import Thread
import asyncio
from pricing import estimate_prompt, pricing_dir
import openai_api
import requests

client = slack.WebClient(token=os.environ['SLACK_API_KEY'])
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SLACK_SIGNING_SECRET'], '/slack/events', app)
BOT_ID = client.api_call("auth.test")['user_id']

estimate_user_dir = {}
estimate_str = ["", ""]


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
    thread = openai_api.new_chat_thread()

    output = openai_api.assistant_send_chat(text, thread)

    if output is None:
        client.chat_postMessage(
            channel=channel_id, text="Sorry I can't answer that question, please ask your manager")
    else:
        client.chat_postMessage(
            channel=channel_id, text=output)


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
        estimate_str[0] += ("\t - " + str(header) + " - " + str(header2) + " - " + str(header3)
                            + ":  "
                            + " (# of Windows: " + str(num)
                            + " + Price: " + str(price)
                            + " = " + f'{num*price:.2f}' + " )\n")

        estimate_str[1] += ("\t - " + str(header) + " - " + str(header2) + " - " + str(header3)
                            + ":  "
                            + " (# of Windows: " + str(num)
                            + " + Price: " + str(price2)
                            + " = " + f'{num*price2:.2f}' + " )\n")

    elif header2 != "":
        estimate_str[0] += ("\t - " + str(header) + " - " + str(header2)
                            + ":  "
                            + " (# of Windows: " + str(num)
                            + " + Price: " + str(price)
                            + " = " + f'{num*price:.2f}' + " )\n")

        estimate_str[1] += ("\t - " + str(header) + " - " + str(header2)
                            + ":  "
                            + " (# of Windows: " + str(num)
                            + " + Price: " + str(price)
                            + " = " + f'{num*price2:.2f}' + " )\n")

    else:
        estimate_str[0] += ("\t - " + str(header) + ":  "
                            + " (# of Windows: " + str(num)
                            + " + Price: " + str(price)
                            + " = " + f'{num*price:.2f}' + " )\n")

        estimate_str[1] += ("\t - " + str(header) + ":  "
                            + " (# of Windows: " + str(num)
                            + " + Price: " + str(price2)
                            + " = " + f'{num*price2:.2f}' + " )\n")


def window_sum(data, user_id):
    # Calculate the estimate for each category and update estimate_user_dir
    global estimate_str
    for x in data:
        if isinstance(data[x], dict):
            for y in data[x]:
                if isinstance(data[x][y], dict):
                    for z in data[x][y]:
                        if data[x][y][z] != 0:
                            estimate_user_dir[str(
                                user_id)]['ext'] += data[x][y][z] * pricing_dir[x][y][z]
                            estimate_user_dir[str(
                                user_id)]['both'] += data[x][y][z] * pricing_dir[x][y][z]
                            print_helper(
                                data[x][y][z],
                                pricing_dir[x][y][z],
                                pricing_dir[x][y][z],
                                x,
                                y,
                                z
                            )
                else:
                    if isinstance(pricing_dir[x][y], (int, float)):
                        if data[x][y] != 0:
                            estimate_user_dir[str(
                                user_id)]['ext'] += data[x][y] * pricing_dir[x][y]
                            estimate_user_dir[str(
                                user_id)]['both'] += data[x][y] * pricing_dir[x][y]
                            print_helper(
                                data[x][y],
                                pricing_dir[x][y],
                                pricing_dir[x][y],
                                x,
                                y
                            )
                    else:
                        if data[x][y] != 0:
                            estimate_user_dir[str(
                                user_id)]['ext'] += data[x][y] * pricing_dir[x][y][0]
                            estimate_user_dir[str(
                                user_id)]['both'] += data[x][y] * pricing_dir[x][y][1]
                            print_helper(
                                data[x][y],
                                pricing_dir[x][y][0],
                                pricing_dir[x][y][1],
                                x,
                                y
                            )
        else:
            if isinstance(pricing_dir[x], (int, float)):
                if data[x] != 0:
                    estimate_user_dir[str(
                        user_id)]['ext'] += data[x] * pricing_dir[x]
                    estimate_user_dir[str(
                        user_id)]['both'] += data[x] * pricing_dir[x]
                    print_helper(data[x],
                                 pricing_dir[x],
                                 pricing_dir[x],
                                 x
                                 )
            else:
                if data[x] != 0:
                    estimate_user_dir[str(
                        user_id)]['ext'] += data[x] * pricing_dir[x][0]
                    estimate_user_dir[str(
                        user_id)]['both'] += data[x] * pricing_dir[x][1]
                    print_helper(data[x],
                                 pricing_dir[x][0],
                                 pricing_dir[x][1],
                                 x
                                 )


def estimate_tax(user_id):
    both_tax = (pricing_dir['tax']['tps']*estimate_user_dir[str(user_id)]['both']) + (
        pricing_dir['tax']['tvq']*estimate_user_dir[str(user_id)]['both'])
    ext_tax = (pricing_dir['tax']['tps']*estimate_user_dir[str(user_id)]['ext']) + (
        pricing_dir['tax']['tvq']*estimate_user_dir[str(user_id)]['ext'])
    return (ext_tax, both_tax)


async def estimate_task(data):
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    text = data.get('text')
    estimate_user_dir[str(user_id)] = {}
    estimate_user_dir[str(user_id)]['ext'] = 0.0
    estimate_user_dir[str(user_id)]['both'] = 0.0
    data = json.loads(openai_api.openai_json(estimate_prompt, text))
    print(str(data))
    window_sum(data, user_id)
    print_estimate(channel_id, user_id)


def print_estimate(user_id) -> str:
    ext_tax, both_tax = estimate_tax(user_id)
    _tmp = ""
    _tmp += "\t*External Only*:\n" + \
        estimate_str[0]
    _tmp += "\t*External & Internal*:\n" + \
        estimate_str[1] + \
        "\t*TOTAL*:\n" + \
        f"\t\tExternal Only: {estimate_user_dir[str(user_id)]['ext']:.2f} + Tax: {ext_tax:.2f}" + \
        f" = *{(estimate_user_dir[str(user_id)]['ext']+ext_tax):.2f}*\n" + \
        f"\t\tExternal & Internal: {estimate_user_dir[str(user_id)]['both']:.2f} + Tax: {both_tax:.2f}" + \
        f" = *{(estimate_user_dir[str(user_id)]['both']+both_tax):.2f}*\n"
    if 'unknown' in estimate_user_dir[str(user_id)]:
        f"\tUnknown Items: {estimate_user_dir[str(user_id)]['unknown']}"
    return _tmp


# Add a prospect to CRM
@app.route('/add-prospect', methods=['POST'])
def add_prospect():
    data = request.form

    thr = Thread(target=lambda: asyncio.run(add_prospect_task(data)))
    thr.start()

    # Respond to Slack immediately
    example = {
        'response_type': 'in_channel',
        'text': 'En attente de la réponse du CRM.',
    }
    return jsonify(example), 200


async def add_prospect_task(data):
    text = data.get('text')
    channel_id = data.get('channel_id')
    add_prospect_prompt = '''
    You will be recieving a string of text, first name, last name
    , email, phone,  address, city, state/providence, zipcode into a json.
    <example_str>
    John Doe, (111)-222-3333, 1 Main St,Tampa, FL, 33710,
    johndoe@gmail.com
    </example_str>
    <exampe_json>
    {
        'first_name': 'John',
        'last_name': 'Doe',
        'phone': '(111)-222-3333',
        'address': '1 Main St',
        'city': 'Tampa',
        'state_province': 'FL',
        'zipcode': '33710',
        'email': 'johndoe@gmail.com'
    }
    </exampe_json>
    '''

    data = json.loads(openai_api.openai_json(add_prospect_prompt, text))

    url = 'https://hooks.zapier.com/hooks/catch/16204948/3ilsh1a/'
    response = requests.post(url, json=data)
    response_code = response.status_code

    _tmp = ""
    if response_code == 200:
        _tmp = "La requête a réussi"
    elif response_code == 201:
        _tmp = "La requête a été créée avec succès"
    else:
        _tmp = "La requête a échoué avec le code d'état {response_code}"

    client.chat_postMessage(
        channel=channel_id,
        text=_tmp
    )


def print_prospect(data, user_id) -> str:
    return f'''
    - Customer Type: {'Commercial' if 'company_name' in data else 'Residential'}\n
    - First Name: {data['first_name']}\n
    - Last Name: {data['last_name']}\n
    - Email: {data['email']}\n
    - Phone: {data['phone']}\n
    - Address: {data['address']}\n
    - City: {data['city']}\n
    - State/Province: {data['state_province']}\n
    - Zipcode: {data['zipcode']}\n
    - Marketing Source: <@{user_id}>\n
    '''


if __name__ == "__main__":
    app.run(debug=True, port=3000)
