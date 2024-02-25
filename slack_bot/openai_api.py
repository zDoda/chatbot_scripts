import os
import time
from openai import OpenAI
client = OpenAI()
client.api_key = os.environ['OPENAI_API_KEY']
# TODO
assistant_id = ""


def chat_completion(prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return completion.choices[0].message.content
    except:
        return "error"


def assistant_send_chat(msg: str, sender_id: str, senders: dict) -> str:
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

    messages = client.beta.threads.messages.list(
        thread_id=senders[sender_id]['thread']
    )
    message_json = messages.model_dump()
    response = message_json['data'][0]['content'][0]['text']['value']
    return response


def new_chat_thread(senders: dict, sender_id: str):
    senders[sender_id]['thread'] = client.beta.threads.create().id
    return senders


def wait_on_run(run, thread: str):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread,
            run_id=run.id,
        )
        time.sleep(1)
    return run


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

