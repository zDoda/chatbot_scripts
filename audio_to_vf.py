import requests
import os
import pvleopard

#Whatsapp


#PicoVoice
def get_audio_data():
    #getting data
    return "/home/czook/Downloads/onlymp2.to_-_1_ScrappyKimberly_In_Search_of_Excrement_Fixing_the_Toxic_Dysfunctional_Crap_in_Organizations-6MF98fakM6A-192k-1694458120.mp3"

leopard = pvleopard.create(access_key=os.environ['PICO_API_KEY'])

transcript, words = leopard.process_file(get_audio_data())
print(transcript)
for word in words:
    print(
      "{word=\"%s\" start_sec=%.1f end_sec=%.2f confidence=%.2f}"
      % (word.word, word.start_sec, word.end_sec, word.confidence))

leopard.delete()
#Voiceflow

# api_key = os.environ['VF_API_KEY']
# user_id = "user_122"  # Unique ID used to track conversation state
# user_input = ""   # User's message to your Voiceflow assistant
#
# body = {"action": {"type": "text", "payload": "Hello world!"}}
#
# # Start a conversation
# response = requests.post(
#     f"https://general-runtime.voiceflow.com/state/user/{user_id}/interact",
#     json=body,
#     headers={"Authorization": api_key},
# )
#
# # Log the response
# print(response.json())

