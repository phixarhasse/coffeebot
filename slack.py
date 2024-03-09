import os
import time
import logging
import requests


class Slack:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")
        try:
            self.baseUrl = "https://slack.com/api/"
            self.authToken = os.getenv('SLACK_TOKEN')
            self.channelId = os.getenv('CHANNEL_ID')
        except KeyError:
            logging.error(
                "Could not parse one or several of SLACK_TOKEN; CHANNEL_ID in the file .env")
            quit()
        self.messages = {"brewing": "Nu bryggs det kaffe! :building_construction:",
                         "done": "Det finns kaffe! :coffee: :brown_heart:",
                         "off": "Bryggare avstängd. :broken_heart:",
                         "saving": "Någon räddar svalnande kaffe! :ambulance:"}
        try:
            self.getLastMessageTimestamp()
        except IndexError:
            logging.error("Could not retrieve the last Slack message.")
            # quit()

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
            if (not response.ok):
                logging.warning(
                    f"Unable to get all Slack messages: {response.status_code}")
                return []
            responseJson = response.json()
            messages = responseJson["messages"]
        except Exception as e:
            logging.error(e)
            return messages

        return messages

    '''
    Gets the timestamp of last message posted to channel
    '''

    def getLastMessageTimestamp(self) -> None:
        # TODO: This seems to set the ts to None all the time on startup
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
                response = requests.post(
                    url=url, headers=headers, params=params)
                if (not response.ok):
                    logging.warning(
                        f"Unable to delete message: {response.status_code} {response.json()['error']}")
                    return
            except Exception as e:
                logging.error(e)
                return
            counter += 1
            time.sleep(1)  # await slack api rate limit
        logging.info("Messages deleted.")

    '''
    Deletes the last message
    '''

    def deleteLastMessage(self) -> None:
        url = f"{self.baseUrl}/chat.delete"
        headers = {"Authorization": f"Bearer {self.authToken}"}
        params = {"channel": f"{self.channelId}",
                  "ts": f"{self.lastMessageTimestamp}"}
        deletedTimestamp = self.lastMessageTimestamp
        try:
            response = requests.post(url=url, headers=headers, params=params)
            if (not response.ok):
                logging.warning(
                    f"Unable to delete message: {response.status_code} {response.json()['error']}")
                return
        except Exception as e:
            logging.error(e)
            return
        logging.debug(f"Message with timestamp {deletedTimestamp} deleted.")

    '''
    Posts the given message text to Slack, returns message timestamp
    '''

    def postMessage(self, messageText) -> None:
        url = f"{self.baseUrl}/chat.postMessage"
        headers = {"Authorization": f"Bearer {self.authToken}"}
        params = {"channel": f"{self.channelId}",
                  "as_user": "true", "text": f"{messageText}"}
        try:
            response = requests.post(url=url, headers=headers, params=params)
            if (not response.ok):
                logging.warning(
                    f"Unable to post message: {response.status_code} {response.json()['error']}")
                self.getLastMessageTimestamp()

        except Exception as e:
            logging.error(e)
            self.getLastMessageTimestamp()

        self.lastMessageTimestamp = response.json()["ts"]
        logging.debug(
            f"Message posted successfully. New timestamp is {self.lastMessageTimestamp}")
