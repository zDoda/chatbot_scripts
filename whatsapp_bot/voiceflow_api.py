import requests
import json
import os

def send_vf_msg(text:str, user_id:str, user_conversation:list):
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
            }, "config": {
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
    return resp_text,user_conversation
