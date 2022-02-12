# Version 2.0.1
# Shelly API doc: https://shelly-api-docs.shelly.cloud/
# This code is calibrated for a Moccamaster KBG744 AO-B (double brewer with 2 pots).

"""
TODO: Set up environment variables.
Add (better) documentation.
"""

import requests
import time
from hue import Hue

SENSOR_URL = "http://ip-to-shelly/meter/0"
HUE_IP = "ip-to-hue-bridge"
SLACK_URL = ""

HEADERS = {"Content-Type":"application/json"}
MESSAGES = {"1bryggs":"Nu bryggs det 1 kanna! :building_construction:",
                  "2bryggs":"Nu bryggs det 2 kannor! :building_construction: :building_construction:",
                  "klart":"Nu är kaffet färdigt! :coffee: :brown_heart:",
                  "slut":"Bryggare avstängd. :broken_heart:",
                  "svalnande": "Någon räddar svalnande kaffe! :ambulance:"}

# Dict representing brewer state
STATE = {"brewing": False, "sentEndMessage": True, "coffeeDone": False}
MEASURE_INTERVAL = 5 #seconds
SEND_TO_SLACK = True
USE_HUE = True


"""
Polls the Shelly embedded web server for power usage [Watt] twice with MEASURE_INTERVAL seconds between.
Returns second value if valid measure, -1.0 otherwise.
"""
def measure():
    tolerance = 40.0
    try:
        response = requests.request("GET", SENSOR_URL)
    except Exception as e:
        print(e)
        return -1.0
    value1 = float(response.json()['power'])
    # Increase tolerance for higher values
    if(value1 > 2000.0):
        tolerance = 80
    print(value1,"Watt")

    time.sleep(MEASURE_INTERVAL)
    try:
        response = requests.request("GET", SENSOR_URL)
    except Exception as e:
        print(e)
        return -1.0
    value2 = float(response.json()['power'])
    print(value2, "Watt")

    # If diff is larger than 10, the power is still changing
    # Diffs lower than 1.0 should not trigger anything
    if(value1 == 0.0 and value2 == 0.0): return value2
    elif(abs(value1 - value2) <= tolerance and
        abs(value1 - value2) > 1.0): return value2
    else: return -1.0

"""
Resets the global dict respresenting the brewer state
"""
def resetState():
    STATE["brewing"] = False
    STATE["sentEndMessage"] = True
    STATE["coffeeDone"] = False

def setupHue():
    hue = Hue(HUE_IP)
    # Get Hue username
    hue.loadUsername()
    if(hue.username == ""):
        print("Waiting for Hue authorization...")
        hue.authorize()
        print("---> Hue Authorization complete!")
    # Get Hue lights
    hue.getLights()
    # Set all lights to red
    hue.setAllLights(65000)
    return hue

"""
Main loop
"""
def main():
    if(USE_HUE):
        hue = setupHue()
    # Main loop
    while(True):
        power = measure()
        if(power == -1.0):
            # Power is still changing or an exception occured, wait and measure again
            time.sleep(MEASURE_INTERVAL/2)
            continue

        # Heating old coffee
        elif((power > 1.0) and (power <= 300.0) and not STATE["brewing"] and not STATE["coffeeDone"]):
            heatingOldCoffee(hue)

        # Fresh coffee has been made
        elif((power > 1.0) and (power <= 300.0) and STATE["brewing"]):
            freshCoffeeHasBeenMade(hue)

        # One pot is brewing
        elif(power > 1000.0 and power <= 2000.0 and not STATE["brewing"]):
            onePotIsBrewing(hue)
        
        # Still brewing, make lights blink
        elif(power > 1000.0 and STATE["brewing"]):
            stillBrewing(hue)

        # Two pots are brewing
        elif(power > 2000.0 and not STATE["brewing"]):
            twoPotsAreBrewing(hue)

        # Coffee maker turned off
        elif(power == 0.0 and not STATE["sentEndMessage"]):
            coffeeMakerTurnedOff(hue)

        # Idle, don't send messages
        elif(power == 0.0 and STATE["sentEndMessage"]):
            print("Bryggare avstängd.")

        time.sleep(MEASURE_INTERVAL)

"""
Messaging and Hue control methods
"""
def heatingOldCoffee(hue):
    print(MESSAGES["svalnande"])
    if(SEND_TO_SLACK):
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": MESSAGES["svalnande"]})
        print(f"Slack: {slackresponse.text}")

    if(USE_HUE):
        hue.setAllLights(29000) # green

    STATE["coffeeDone"] = True
    STATE["sentEndMessage"] = False

def freshCoffeeHasBeenMade(hue):
    time.sleep(30) # Wait for coffee to drip down
    print(MESSAGES["klart"])
    if(SEND_TO_SLACK):
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": MESSAGES["klart"]})
        print(f"Slack: {slackresponse.text}")

    if(USE_HUE):
        hue.setAllLights(29000) # green

    STATE["coffeeDone"] = True
    STATE["brewing"] = False

def onePotIsBrewing(hue):
    print(MESSAGES["1bryggs"])
    if(SEND_TO_SLACK):
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": MESSAGES["1bryggs"]})
        print(f"Slack: {slackresponse.text}")

    if(USE_HUE):
        hue.setAllLights(10000) # yellow

    STATE["brewing"] = True
    STATE["sentEndMessage"] = False

def twoPotsAreBrewing(hue):
    print(MESSAGES["2bryggs"])
    if(SEND_TO_SLACK):
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": MESSAGES["2bryggs"]})
        print(f"Slack: {slackresponse.text}")

    if(USE_HUE):
        hue.setAllLights(10000) # yellow

    STATE["brewing"] = True
    STATE["sentEndMessage"] = False

def stillBrewing(hue):
    if(USE_HUE):
        hue.turnOffAllLights()
        time.sleep(1)
        hue.setAllLights(10000) # yellow

def coffeeMakerTurnedOff(hue):
    print(MESSAGES["slut"])
    if(SEND_TO_SLACK):
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": MESSAGES["slut"]})
        print(f"Slack: {slackresponse.text}")

    if(USE_HUE):
        hue.setAllLights(65000) # red

    resetState()


if(__name__ == "__main__"):
    main()
