import os
import time
import json
import requests
import slack
from openai import OpenAI
import bot
from main import owner_id, send_slack_message, slack_client
client = OpenAI()
client.api_key = os.environ['OPENAI_API_KEY']
# TODO
assistant_id = "asst_ZuM9sbc1LKdFADFYl7IPhZt7"


def chat_completion(prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return completion.choices[0].message.content
    except:
        return "error"


def openai_json(system_prompt: str, prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        return completion.choices[0].message.content
    except:
        return "error"


def assistant_send_chat(msg: str, thread_id: str) -> str:
    _ = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=msg
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    run = wait_on_run(run, thread_id)
    response = ""

    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    message_json = messages.model_dump()
    response = message_json['data'][0]['content'][0]['text']['value']
    return response


def new_chat_thread():
    thread = client.beta.threads.create().id
    return thread


def wait_on_run(run, thread: str):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread,
            run_id=run.id,
        )
        time.sleep(1)
    return run


def assistant_estimate_chat(msg: str, sender_id: str, senders: dict) -> str:
    _ = client.beta.threads.messages.create(
        thread_id=senders[sender_id]['thread'],
        role="user",
        content=msg
    )

    run = client.beta.threads.runs.create(
        thread_id=senders[sender_id]['thread'],
        assistant_id=assistant_id
    )

    run = wait_on_run(run, senders[sender_id]['thread'])
    response = ""
    run_dir = run.model_dump()

    if run_dir['status'] == 'requires_action':
        required_action = run_dir['required_action']['submit_tool_outputs']['tool_calls'][0]
        function_name = required_action['function']['name']
        tool_id = required_action['id']

        if function_name == "send_estimate":
            args = json.loads(required_action['function']['arguments'])
            print(args['prospect_info'])

            print(args['service_details'])
            bot.estimate_user_dir[str(sender_id)] = {}
            bot.estimate_user_dir[str(sender_id)]['ext'] = 0.0
            bot.estimate_user_dir[str(sender_id)]['both'] = 0.0
            if 'unknown_items' in args['service_details']:
                bot.estimate_user_dir[str(
                    sender_id)]['unknown'] = args['service_details']['unknown_items']
            bot.estimate_user_dir[str(
                sender_id)]['prospect_info'] = args['prospect_info']
            bot.window_sum(args['service_details'], sender_id)
            response = f"*Estimation*\n{bot.print_estimate(sender_id)}\n\n*Prospect*\n\t{bot.print_prospect(args['prospect_info'], sender_id)}" + \
                "*Please confirm details provided correct?*"
            messages = client.beta.threads.runs.submit_tool_outputs(
                thread_id=senders[sender_id]['thread'],
                run_id=run.id,
                tool_outputs=[{"tool_call_id": tool_id, "output": response}]
            )

        elif function_name == "confirm_estimate":
            args = json.loads(required_action['function']['arguments'])
            confirm = bool(args['confirmation'])
            response = ''
            if confirm:
                zap_url = 'https://hooks.zapier.com/hooks/catch/16204948/3ilsh1a/'
                _, both_tax = bot.estimate_tax(sender_id)
                data = {
                    'estimate': str(bot.estimate_user_dir[str(sender_id)]['both']),
                    'tax_amount': f'{both_tax:.2f}'
                }

                data.update(bot.estimate_user_dir[str(
                    sender_id)]['prospect_info'])
                req = requests.post(
                    zap_url, json=data)

                response_code = req.status_code

                if response_code == 200:
                    response = "La requête a réussi"
                elif response_code == 201:
                    response = "La requête a été créée avec succès"
                else:
                    response = f"La requête a échoué avec le code d'état {response_code}"

            messages = client.beta.threads.runs.submit_tool_outputs(
                thread_id=senders[sender_id]['thread'],
                run_id=run.id,
                tool_outputs=[{"tool_call_id": tool_id, "output": response}]
            )

        elif function_name == "unanswered_question":
            args = json.loads(required_action['function']['arguments'])
            print(args)
            question = str(args['user_question'])

            response = f"I am unable to answer your question, I messaged <@{owner_id}> your question"

            conversation_res = slack_client.conversations_open(users=[owner_id])
            channel_id = conversation_res["channel"]["id"]

            send_slack_message(channel_id, f"Hello, <@{sender_id}> had the following question:\n{question}")
            messages = client.beta.threads.runs.submit_tool_outputs(
                thread_id=senders[sender_id]['thread'],
                run_id=run.id,
                tool_outputs=[{"tool_call_id": tool_id, "output": response}]
            )

    else:
        messages = client.beta.threads.messages.list(
            thread_id=senders[sender_id]['thread']
        )
        message_json = messages.model_dump()
        print(message_json)
        response = message_json['data'][0]['content'][0]['text']['value']
    return response


def delete_assistants():
    my_assistants = client.beta.assistants.list(
        order="desc",
    )

    for assistant in my_assistants.model_dump()['data']:
        _assistant = str(assistant['id'])
        assistant_files = client.beta.assistants.files.list(
            assistant_id=_assistant
        )
        for file in assistant_files:
            _id = str(file.model_dump()['id'])
            print(_id)
            # try:
            #     client.beta.assistants.files.delete(
            #         assistant_id=_assistant,
            #         file_id=_id
            #     )
            # except:
            #     print('No file to delete')
        client.beta.assistants.delete(assistant_id=_assistant)


def delete_files():
    files = client.files.list()
    my_files = files.model_dump()['data']
    for file in my_files:
        _id = str(file['id'])
        print(_id)
        client.files.delete(_id)
