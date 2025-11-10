import os
import json
import logging
import requests
from brewingState import BrewingState


class Hue:
    def __init__(self):
        logging.basicConfig(
            format="%(asctime)s %(levelname)s: %(message)s",
            level=logging.DEBUG,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        try:
            logging.debug(f"Hue.__init__: Initializing Hue class")
            self.bridgeIp = os.getenv("HUE_IP")
            self.url = f"http://{self.bridgeIp}/api"
            self.urlV2 = f"http://{self.bridgeIp}/clip/v2"
        except KeyError:
            logging.error("Hue.__init__: Could not parse HUE_IP in the file .env")
            quit(1)

        self.lights = []
        self.username = ""
        self.loadUsername()
        if (self.username == ""):
            logging.info("Hue.__init__: Waiting for Hue authorization...")
            self.authorize()
            logging.info("---> Hue Authorization complete!")

    def saveUsername(self, username):
        try:
            f = open("hue_username", "w")
            f.write(username)
            f.close()
            logging.debug(f"Saved user name.")
        except Exception as e:
            logging.error(e)

    def loadUsername(self):
        try:
            f = open("hue_username", "r")
            self.username = f.readline()
            f.close()
            logging.debug(f"Loaded user name.")
        except Exception as e:
            logging.error(e)
            self.username = ""
            return

    def authorize(self):
        self.username = ""
        logging.debug(f"Starting authorization process.")
        try:
            hueResponse = requests.post(self.url, json={"devicetype": "coffeebot"})
            # Need to generate username
            if (hueResponse.json()[0]["error"]["type"] == 101):
                logging.info("\tPlease press the link button on the HUE Bridge.")
                user_input = input("Have you pressed it? [y/n] ")
                if (not user_input == "y"):
                    logging.info("\tHue authentication cancelled. Exiting.")
                    quit(0)
                else:
                    hueResponse = requests.post(
                        self.url, json={"devicetype": "coffeebot"}
                    )
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

    def getLightsV2(self):
        # headers = {"Authorization": f"Bearer {self.authToken}"}
        # headers = {"hue-application-key": {self.username}}
        headers = {'hue-application-key': f"{self.username}"}
        logging.debug(f"Hue.getLightsV2: Getting all lights with headers: {headers}")
        self.lights = []
        if (self.username == ""):
            return
        try:
            hueResponse = requests.get(
                f"{self.urlV2}/resource/light/",
                headers=headers,
            )
            if (not hueResponse.ok):
                logging.warning(f"Hue.getLightsV2: Unable to get Hue lights V2, got the response {hueResponse.status_code} {hueResponse.text}")
                # response = format(hueResponse.status_code, hueResponse.text)
                # logging.warning(f"Unable to get Hue lights. {response}")
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

    def setAllLightsV2(self, colorX, colorY):
        headers = {"hue-application-key": f"{self.username}"}
        logging.debug(f"Hue.setAllLightsV2: Setting lights with headers: {headers} and {self.lights.count()} number of lights.")
        try:
            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.urlV2}/resource/light/{light}",
                    headers=headers,
                    json={
                        "dimming": {"brightness": 200.0},
                        "color": {"xy": {"x": colorX, "y": colorY}},
                    },
                )
                logging.debug(f"Hue.setAllLightsV2: Hue light V2 {light}: {hueResponse.status_code}")
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

    def turnOffAllLightsV2(self):
        headers = {"hue-application-key": f"{self.username}"}
        logging.debug(f"Hue.turnOffAllLightsV2: Turning off lights with headers: {headers}")
        try:
            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.urlV2}/resource/light/{light}",
                    headers=headers,
                    json={"on": {"on": False}},
                )
                logging.debug(f"Hue.turnOffAllLightsV2: Hue light {light}: {hueResponse.status_code}")
        except Exception as e:
            logging.error(e)
            return

    def setBrewingLights(self):
        headers = {"hue-application-key": f"{self.username}"}
        logging.debug(f"Hue.setBrewingLights: Brewing has started with headers: {headers} and {self.lights.count()} number of lights.")
        try:
            brewingState = BrewingState(BrewingState.Dimming(100.0), BrewingState.Color(0.4931, 0.455), "sparkle", BrewingState.Parameters(BrewingState.Color(0.4931, 0.455), BrewingState.ColorTemperature(153, False), 0.5))
            jsonState = json.dumps(brewingState.reprJSON(), cls=BrewingState.ComplexEncoder)

            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.urlV2}/resource/light/{light}",
                    headers=headers,
                    json = jsonState
                )
                logging.debug(f"Hue.setBrewingLights: Hue light {light}: {hueResponse.status_code}")
        except Exception as e:
            logging.error(e)
            return

    def setCoffeeIsDoneLights(self):
        headers = {"hue-application-key": f"{self.username}"}
        logging.debug(f"Hue.setCoffeeIsDoneLights: Coffee is ready with headers: {headers} and {self.lights.count()} number of lights.")
        try:
            brewingState = BrewingState(BrewingState.Dimming(100.0), BrewingState.Color(0.1673, 0.5968), "sparkle", BrewingState.Parameters(BrewingState.Color(0.1673, 0.5968), BrewingState.ColorTemperature(153, False), 0.5))
            jsonState = json.dumps(brewingState.reprJSON(), cls=BrewingState.ComplexEncoder)

            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.urlV2}/resource/light/{light}",
                    headers=headers,
                    json = jsonState
                )
                logging.debug(f"Hue.setCoffeeIsDoneLights: Hue light {light}: {hueResponse.status_code}")
        except Exception as e:
            logging.error(e)
            return
