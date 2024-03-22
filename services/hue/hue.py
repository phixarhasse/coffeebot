import os
import logging
import requests


class Hue:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")
        try:
            self.bridgeIp = os.getenv('HUE_IP')
            self.url = f"http://{self.bridgeIp}/api"
        except KeyError:
            logging.error("Could not parse HUE_IP in the file .env")
            quit(1)

        self.lights = []
        self.username = ""
        self.loadUsername()
        if (self.username == ""):
            logging.info("Waiting for Hue authorization...")
            self.authorize()
            logging.info("---> Hue Authorization complete!")

    def saveUsername(self, username):
        try:
            f = open("hue_username", "w")
            f.write(username)
            f.close()
        except Exception as e:
            logging.error(e)

    def loadUsername(self):
        try:
            f = open("hue_username", "r")
            self.username = f.readline()
            f.close()
        except Exception as e:
            logging.error(e)
            self.username = ""
            return

    def authorize(self):
        self.username = ""
        try:
            hueResponse = requests.post(
                self.url, json={"devicetype": "coffeebot"})
            # Need to generate username
            if (hueResponse.json()[0]["error"]["type"] == 101):
                logging.info(
                    "\tPlease press the link button on the HUE Bridge.")
                user_input = input("Have you pressed it? [y/n] ")
                if (not user_input == 'y'):
                    logging.info("\tHue authentication cancelled. Exiting.")
                    quit(0)
                else:
                    hueResponse = requests.post(
                        self.url, json={"devicetype": "coffeebot"})
                    username = hueResponse.json()[0]["success"]["username"]
                    self.username = username
                    self.saveUsername(username)
            elif (hueResponse.ok):
                username = hueResponse.json()[0]["success"]["username"]
                self.username = username
                self.saveUsername(username)
        except Exception as e:
            logging.error("Error during Hue authentication.")
            logging.error("Exception: ", e)
            quit(1)

    def getLights(self):
        self.lights = []
        if (self.username == ""):
            return
        try:
            hueResponse = requests.get(f"{self.url}/{self.username}/lights/")
            if (not hueResponse.ok):
                logging.warning("Unable to get Hue lights.")
                return
        except Exception as e:
            logging.error(e)
            return
        for light in hueResponse.json():
            self.lights.append(light)
        return

    def setAllLights(self, color):
        try:
            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.url}/{self.username}/lights/{light}/state",
                    json={"on": True, "sat": 254, "bri": 200, "hue": color})
                logging.debug(f"Hue light {light}: {hueResponse.status_code}")
        except Exception as e:
            logging.error(e)
            return

    def turnOffAllLights(self):
        try:
            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.url}/{self.username}/lights/{light}/state",
                    json={"on": False})
                logging.debug(f"Hue light {light}: {hueResponse.status_code}")
        except Exception as e:
            logging.error(e)
            return
