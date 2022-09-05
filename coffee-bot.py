# Version 3.0.0
# Shelly API doc: https://shelly-api-docs.shelly.cloud/
# This code is calibrated for a Moccamaster KBG744 AO-B (double brewer with 2 pots).

"""
TODO: Data collection, automatic or semiautomatic calibration
"""

from dotenv import load_dotenv
import os
import requests
import time
from hue import Hue
from slack import Slack

# Dict representing brewer state
STATE = {"brewing": False, "turnedOff": True, "coffeeDone": False}
MEASURE_INTERVAL = 5 #seconds

"""
Main loop
"""
def main() -> None:
    load_dotenv() # Load environment variables
    sensor_url = os.environ['SENSOR_URL']
    slack = Slack()
    hue = setupHue()

    while(True):
        power = measure(sensor_url)
        if(power == -1.0):
            # Power is still changing or an exception occured, wait and measure again
            time.sleep(MEASURE_INTERVAL/2)
            continue

        # Heating old coffee
        elif((power > 1.0) and (power <= 300.0) and not STATE["brewing"] and not STATE["coffeeDone"]):
            heatingOldCoffee(hue, slack)

        # Fresh coffee has been made
        elif((power > 1.0) and (power <= 300.0) and STATE["brewing"]):
            freshCoffeeHasBeenMade(hue, slack)

        # Coffee is brewing
        elif(power > 1000.0 and not STATE["brewing"]):
            coffeeIsBrewing(hue, slack)
        
        # Still brewing, make lights blink
        elif(power > 1000.0 and STATE["brewing"]):
            stillBrewing(hue)

        # Coffee maker turned off
        elif(power == 0.0 and not STATE["turnedOff"]):
            coffeeMakerTurnedOff(hue, slack)

        # Idle, don't send messages
        elif(power == 0.0 and STATE["turnedOff"]):
            continue

        time.sleep(MEASURE_INTERVAL)

"""
Polls the Shelly embedded web server for power usage [Watt] twice with MEASURE_INTERVAL seconds between.
Returns second value if valid measure, -1.0 otherwise.
"""
def measure(sensor_url) -> float:
    tolerance = 40.0
    try:
        response = requests.request("GET", sensor_url)
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
        response = requests.request("GET", sensor_url)
    except Exception as e:
        print(e)
        return -1.0
    value2 = float(response.json()['power'])
    print(value2, "Watt")

    # If diff is larger than 10, the power is still changing
    # Diffs lower than 1.0 are ignored
    if(value1 == 0.0 and value2 == 0.0): return value2
    elif(abs(value1 - value2) <= tolerance and
        abs(value1 - value2) > 1.0): return value2
    else: return -1.0

"""
Resets the global dict respresenting the brewer state
"""
def resetState() -> None:
    STATE["brewing"] = False
    STATE["turnedOff"] = True
    STATE["coffeeDone"] = False

"""
Loads Hue username and lights
"""
def setupHue() -> Hue:
    hue = Hue()
    hue.getLights()
    return hue

"""
Messaging and Hue control methods
"""
def heatingOldCoffee(hue: Hue, slack: Slack) -> None:
    print(slack.messages["saving"])
    if(slack.useSlack):
        slack.deleteLastMessage()
        slack.postMessage(slack.messages["saving"])

    if(hue.useHue):
        hue.setAllLights(29000) # green

    STATE["coffeeDone"] = True
    STATE["turnedOff"] = False

def coffeeIsBrewing(hue: Hue, slack: Slack) -> None:
    print(slack.messages["brewing"])
    if(slack.useSlack):
        slack.deleteLastMessage()
        slack.postMessage(slack.messages["brewing"])

    if(hue.useHue):
        hue.setAllLights(10000) # yellow

    STATE["brewing"] = True
    STATE["turnedOff"] = False

def freshCoffeeHasBeenMade(hue: Hue,  slack: Slack) -> None:
    time.sleep(30) # Wait 30 seconds for coffee to drip down
    print(slack.messages["done"])
    if(slack.useSlack):
        slack.deleteLastMessage()
        slack.postMessage(slack.messages["done"])

    if(hue.useHue):
        hue.setAllLights(29000) # green

    STATE["coffeeDone"] = True
    STATE["brewing"] = False

def stillBrewing(hue: Hue) -> None:
    if(hue.useHue):
        hue.turnOffAllLights()
        time.sleep(1)
        hue.setAllLights(10000) # yellow

def coffeeMakerTurnedOff(hue: Hue,  slack: Slack) -> None:
    print(slack.messages["off"])
    resetState()
    if(slack.useSlack):
        slack.deleteLastMessage()
        slack.postMessage(slack.messages["off"])

    if(hue.useHue):
        hue.setAllLights(65000) # red


if(__name__ == "__main__"):
    main()
