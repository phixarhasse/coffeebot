import os
import requests
import time
from dotenv import load_dotenv

class Slack:
    def __init__(self):
        load_dotenv('.env')
        self.useSlack = os.environ['USE_SLACK']
        self.baseUrl = "https://slack.com/api/"
        self.authToken = os.environ['SLACK_TOKEN']
        self.channelId = os.environ['CHANNEL_ID']
        self.messages = {"brewing":"Nu bryggs det kaffe! :building_construction:",
                "done":"Det finns kaffe! :coffee: :brown_heart:",
                "off":"Bryggare avstängd. :broken_heart:",
                "saving": "Någon räddar svalnande kaffe! :ambulance:"}
        self.lastMessageTimestamp = self.getLastMessageTimestamp()

    '''
    Returns: list with all messages in channel history, up to the first 100
    '''
    def getAllMessages(self) -> list[str]:
        url = f"{self.baseUrl}/conversations.history"
        headers = {"Authorization": f"Bearer {self.authToken}"}
        params = {"channel": f"{self.channelId}"}
        messages = []
        try:
            response = requests.get(url, params=params, headers=headers)
            if(not response.ok):
                print(f"Unable to get all Slack messages: {response.status_code}")
                return []
            responseJson = response.json()
            messages = responseJson["messages"]
        except Exception as e:
            print(e)
            return messages

        return messages
    
    '''
    Gets the timestamp of last message posted to channel
    '''
    def getLastMessageTimestamp(self) -> None:
        allMessages = self.getAllMessages()
        self.lastMessageTimestamp = allMessages[0]['ts']

    '''
    Deletes all messages in the given list
    '''
    def deleteMessages(self, messages) -> None:
        url = f"{self.baseUrl}/chat.delete"
        headers = {"Authorization": f"Bearer {self.authToken}"}
        print(f"Deleting {len(messages)} messages...")
        counter = 1
        for message in messages:
            print(f"Deleting message {counter} out of {len(messages)}")
            params = {"channel": f"{self.channelId}", "ts": f"{message['ts']}"}
            try:
                response = requests.post(url=url, headers=headers, params=params)
                if(not response.ok):
                    print(f"Unable to delete message: {response.status_code} {response.json()['error']}")
                    return
            except Exception as e:
                print(e)
                return
            counter += 1
            time.sleep(1) # await slack api rate limit
        print("Messages deleted.")

    '''
    Deletes the last message
    '''
    def deleteLastMessage(self) -> None:
        url = f"{self.baseUrl}/chat.delete"
        headers = {"Authorization": f"Bearer {self.authToken}"}
        params = {"channel": f"{self.channelId}", "ts": f"{self.lastMessageTimestamp}"}
        deletedTimestamp = self.lastMessageTimestamp
        try:
            response = requests.post(url=url, headers=headers, params=params)
            if(not response.ok):
                print(f"Unable to delete message: {response.status_code} {response.json()['error']}")
                return
        except Exception as e:
            print(e)
            return
        print(f"Message with timestamp {deletedTimestamp} deleted.")
    
    '''
    Posts the given message text to Slack, returns message timestamp
    '''
    def postMessage(self, messageText) -> None:
        url = f"{self.baseUrl}/chat.postMessage"
        headers = {"Authorization": f"Bearer {self.authToken}"}
        params = {"channel": f"{self.channelId}", "as_user":"true", "text": f"{messageText}"}
        try:
            response = requests.post(url=url, headers=headers, params=params)
            if(not response.ok):
                print(f"Unable to post message: {response.status_code} {response.json()['error']}")
                self.getLastMessageTimestamp()

        except Exception as e:
            print(e)
            self.getLastMessageTimestamp()

        self.lastMessageTimestamp = response.json()["ts"]
        print(f"Message posted successfully. New timestamp is {self.lastMessageTimestamp}")
