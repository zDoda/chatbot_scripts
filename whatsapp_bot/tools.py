{
  "name": "clear_chat",
  "description": "The user can ask to clear the chat to reset the history",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
{
  "name": "change_response_option",
  "description": "This changes the response from text to audio or vise versa",
  "parameters": {
    "type": "object",
    "properties": {
      "response_option": {
        "type": "string",
        "description": "The user can ask to switch the response option of the bot, values can only be text and audio (sometimes called voicenotes)"
      }
    },
    "required": [
      "response_option"
    ]
  }
}
