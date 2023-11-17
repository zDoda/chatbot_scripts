import os
import uuid
import time
from openai import OpenAI
import requests
from requests.auth import HTTPBasicAuth
import soundfile as sf
 
account_sid = os.environ['TWILIO_SID']
auth_token = os.environ['TWILIO_AUTH']
client = OpenAI()
client.api_key = os.environ['OPENAI_API_KEY']
assistant_id = "asst_meYff3tPeBHrBKzHibCDRsQK"

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

def transcript_audio(media_url: str) -> dict:
    try:
        ogg_file_path = f'{uuid.uuid1()}.ogg'
        data = requests.get(url=media_url, auth=HTTPBasicAuth(account_sid, auth_token))
        print('1')
        with open(ogg_file_path, 'wb') as file:
            file.write(data.content)
        print('2')
        audio_data, sample_rate = sf.read(ogg_file_path)
        print('3')
        mp3_file_path = f'{uuid.uuid1()}.mp3'
        sf.write(mp3_file_path, audio_data, sample_rate)
        audio_file = open(mp3_file_path, 'rb')
        os.unlink(ogg_file_path)
        os.unlink(mp3_file_path)
        transcript = client.audio.transcriptions.create(
            model='whisper-1', file=audio_file)
        return {
            'status': 1,
            'transcript': transcript.model_dump()['text']
        }
    except Exception as e:
        print('Error at transcript_audio...')
        print(e)
        return {
            'status': 0,
            'transcript': transcript.model_dump()['text']
        }

def assistant_send_chat(msg: str,sender_id, senders) -> str:
    message = client.beta.threads.messages.create(
        thread_id=senders[sender_id]['thread'],
        role="user",
        content=msg
    )
    run = client.beta.threads.runs.create(
        thread_id=senders[sender_id]['thread'],
        assistant_id=assistant_id
    )
    run = wait_on_run(run,senders[sender_id]['thread'])
    response = ""
    if run.model_dump()['status'] == 'requires_action':
        function_name = run.model_dump()['required_action']['submit_tool_outputs']['tool_calls'][0]['function']['name']
        tool_id = run.model_dump()['required_action']['submit_tool_outputs']['tool_calls'][0]['id']
        if function_name == "clear_chat":
            response = "Chat has been reset"
            new_chat_thread(senders, sender_id)
        elif function_name == "change_response_option":
            if senders[sender_id]['botOption']:
                senders[sender_id]['botOption'] = False
                response = "I am now responding with text"
            else:
                senders[sender_id]['botOption'] = True
                response = "I am now responding with voice"

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
        print(message_json['data'][0]['content'])
        response = message_json['data'][0]['content'][0]['text']['value']
    return response

def new_chat_thread(senders, sender_id):
    senders[sender_id]['thread'] = client.beta.threads.create().id
    return senders
import time

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run
