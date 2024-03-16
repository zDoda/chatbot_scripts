import slack
import os
client = slack.WebClient(token=os.environ['SLACK_API_KEY'])

BOT_ID = client.api_call("auth.test")['user_id']

try:
    # Call the users.list method using the WebClient
    result = client.users_list()
    users = result['members']

    # Print the user's name and ID (or other details you need)
    for user in users:
        print(user['id'], user['name'])
except:
    print(f"Error fetching users:")
