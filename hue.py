import json
import logging
import os
import requests
from brewingStateHelper import BrewingState, Dimming, Color, ColorTemperature, Parameters, ComplexEncoder


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
            self.url = f"https://{self.bridgeIp}/api"
            self.urlV2 = f"https://{self.bridgeIp}/clip/v2"
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


    def initializeLights(self):

        headers = {'hue-application-key': f"{self.username}"}
        self.lights = []
        if (self.username == ""):
            return
        try:
            hueResponse = requests.get(
                f"{self.urlV2}/resource/light",
                headers = headers, 
                verify = False
            )
            if (not hueResponse.ok):
                logging.warning(f"Hue.getLightsV2: Unable to get Hue lights V2, got the response {hueResponse.status_code} {hueResponse.text}")
                return

        except Exception as e:
            logging.error(e)
            return
        for light in hueResponse.json()["data"]:
            self.lights.append(light)
        logging.debug(f"Hue.getLightsV2: Hue lights V2 retrieved and saved to: {self.lights}")


    def getLightV2(self, lightId = None):

        headers = {"hue-application-key": f"{self.username}"}

        if(lightId is None):
            logging.error("Hue.getLightV2: No light ID provided.")
            return

        if (self.username == ""):
            logging.error("Hue.getLightV2: No username loaded.")
            return

        try:
            hueResponse = requests.get(
                f"{self.urlV2}/resource/light/{lightId}",
                headers = headers, 
                verify = False
            )
            if (not hueResponse.ok):
                logging.warning(f"Hue.getLightV2: Unable to get Hue light info, got the response {hueResponse.status_code} {hueResponse.text}")
                return
            logging.debug(f"Hue.getLightV2: Hue light {hueResponse.json()} info retrieved.")
        except Exception as e:
            logging.error(e)
            return
        
        return hueResponse.json()["data"]


# API v1: json={"on": True, "sat": 254, "bri": 200, "hue": color})
# The different values of [color] used earlier:
# 29000 - green - heating old coffee - "xy": [0.1673,0.5968]
# 10000 - yellow - brewing - "xy": [0.4878,0.4613]
# 29000 - green - coffee is done
# 10000 - yellow - still brewing
# 65000 - red - turned off - "xy": [0.6758,0.3007]
    def setAllLightsV2(self, colorX, colorY) -> None:

        headers = {"hue-application-key": f"{self.username}"}

        try:
            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.urlV2}/resource/light/{light}",
                    headers=headers,
                    json={
                        "dimming": {"brightness": 78.66},
                        "color": {"xy": {"x": colorX, "y": colorY}},
                    },
                )
                logging.debug(f"Hue.setAllLightsV2: Hue light V2 {light} is lit : {hueResponse.status_code}")
        except Exception as e:
            logging.error(e)


    def setLightV2(self, colorX, colorY, lightId = None) -> None:

        headers = {"hue-application-key": f"{self.username}"}

        if(lightId is None):
            logging.error("Hue.setLightV2: No light ID provided.")
            return
        
        if (self.username == ""):
            logging.error("Hue.setLightV2: No username loaded.")
            return

        try:
            hueResponse = requests.put(
                f"{self.urlV2}/resource/light/{lightId}",
                headers = headers, 
                verify = False,
                json = {
                    "dimming": {"brightness": 78.66},
                    "color": {"xy": {"x": colorX, "y": colorY}},
                },
            )
            logging.debug(f"Hue.setLightV2: Hue light V2 {lightId} responded with: {hueResponse.status_code}, {hueResponse.text}")
        except Exception as e:
            logging.error(e)


    def turnOffAllLightsV2(self) -> None:

        headers = {"hue-application-key": f"{self.username}"}
        try:
            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.urlV2}/resource/light/{light}",
                    headers = headers,
                    verify = False,
                    json = {"on": {"on": False}},
                )
                logging.debug(f"Hue.turnOffAllLightsV2: Hue light {light}: {hueResponse.status_code}")
        except Exception as e:
            logging.error(e)


    def setBrewingLights(self) -> None:

        headers = {"hue-application-key": f"{self.username}"}
        try:
            brewingState = BrewingState(Dimming(78.66), Color(0.4931, 0.455), "sparkle", Parameters(Color(0.4931, 0.455), ColorTemperature(153, False), 0.5))
            jsonState = json.dumps(brewingState.reprJSON(), cls = ComplexEncoder)

            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.urlV2}/resource/light/{light}",
                    headers = headers,
                    verify = False,
                    json = jsonState
                )
                logging.debug(f"Hue.setBrewingLights: Hue light {light}: {hueResponse.status_code}")
        except Exception as e:
            logging.error(e)


    def setCoffeeIsDoneLights(self) -> None:

        headers = {"hue-application-key": f"{self.username}"}
        try:
            brewingState = BrewingState(Dimming(78.66), Color(0.1673, 0.5968), None, Parameters(Color(0.1673, 0.5968), ColorTemperature(153, False)))
            jsonState = json.dumps(brewingState.reprJSON(), cls = ComplexEncoder)

            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.urlV2}/resource/light/{light}",
                    headers = headers,
                    verify = False,
                    json = jsonState
                )
                logging.debug(f"Hue.setCoffeeIsDoneLights: Hue light {light}: {hueResponse.status_code}")
        except Exception as e:
            logging.error(e)


    def setCoffeeMakerTurnedOff(self) -> None:

        headers = {"hue-application-key": f"{self.username}"}
        try:
            brewingState = BrewingState(None, Color(0.6758, 0.3008), None, Parameters(Color(0.6758, 0.3008), ColorTemperature(153, False)))
            jsonState = json.dumps(brewingState.reprJSON(), cls = ComplexEncoder)

            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.urlV2}/resource/light/{light}",
                    headers = headers,
                    verify = False,
                    json = jsonState
                )
                logging.debug(f"Hue.setCoffeeMakerTurnedOff: Hue light {light}: {hueResponse.status_code}")
        except Exception as e:
            logging.error(e)
