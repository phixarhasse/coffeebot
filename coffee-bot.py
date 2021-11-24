# Version 2.0
# Shelly API doc: https://shelly-api-docs.shelly.cloud/
# This code is calibrated for a Moccamaster KBG744 AO-B (double brewer with 2 pots).
import requests
import time
from datetime import date
from datetime import datetime
from hue import Hue

SENSOR_URL = "http://url-to-shelly/meter/0"
HUE_IP = "ip-to-hue-bridge"
SLACK_URL = ""

HEADERS = {"Content-Type":"application/json"}
MESSAGES = {"1bryggs":"Nu bryggs det 1 kanna! :building_construction:",
                  "2bryggs":"Nu bryggs det 2 kannor! :building_construction: :building_construction:",
                  "klart":"Nu är kaffet färdigt! :coffee: :brown_heart:",
                  "slut":"Bryggare avstängd. :broken_heart:",
                  "svalnande": "Någon räddar svalnande kaffe! :ambulance:"}

# Dict to represent brewer state
STATE = {"brewing": False, "sentEndMessage": True, "coffeeDone": False}
MEASURE_INTERVAL = 5 #seconds
SEND_TO_SLACK = False

"""Polls the Shelly embedded web server for power usage [Watt] twice with MEASURE_INTERVAL seconds between.
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

def resetState():
    STATE["brewing"] = False
    STATE["sentEndMessage"] = True
    STATE["coffeeDone"] = False

def writeStatsToFile(pots):
    today = date.today()
    now = datetime.now()
    if(not type(pots) is int):
        print("Input to file not an integer")
        return -1
    try:
        # Open log file, creates one if does not exist
        f = open(f"./logs/stats-{today}.stat", "a")
        f.write(f"{now}|{pots}\n")
        f.close()
        return 0
    except Exception as e:
        print(e)
        return -1

def main():
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

    # Main loop
    while(True):
        power = measure()
        if(power == -1.0):
            # Power is still changing or an exception occured, wait and measure again
            time.sleep(MEASURE_INTERVAL/2)
            continue

        # Heating old coffee
        elif((power > 1.0) and (power <= 300.0) and not STATE["brewing"] and not STATE["coffeeDone"]):
            print(MESSAGES["svalnande"])
            if(SEND_TO_SLACK):
                slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": MESSAGES["svalnande"]})
                print(f"Slack: {slackresponse.text}")
            hue.setAllLights(29000) # green
            STATE["coffeeDone"] = True
            STATE["sentEndMessage"] = False

        # Fresh coffee has been made
        elif((power > 1.0) and (power <= 300.0) and STATE["brewing"]):
            time.sleep(30) # Wait for coffee to drip down
            print(MESSAGES["klart"])
            if(SEND_TO_SLACK):
                slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": MESSAGES["klart"]})
                print(f"Slack: {slackresponse.text}")
            hue.setAllLights(29000) # green
            STATE["coffeeDone"] = True
            STATE["brewing"] = False

        # One pot is brewing
        elif(power > 1000.0 and power <= 2000.0 and not STATE["brewing"]):
            print(MESSAGES["1bryggs"])
            if(SEND_TO_SLACK):
                slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": MESSAGES["1bryggs"]})
                print(f"Slack: {slackresponse.text}")
            hue.setAllLights(10000) # yellow
            STATE["brewing"] = True
            STATE["sentEndMessage"] = False
            filewritten = writeStatsToFile(1)
            if(filewritten == -1):
                print("Failed to write stats to file.")
        
        # Still brewing, make lights blink
        elif(power > 1000.0 and STATE["brewing"]):
            hue.turnOffAllLights()
            time.sleep(1)
            hue.setAllLights(10000) # yellow

        # Two pots are brewing
        elif(power > 2000.0 and not STATE["brewing"]):
            print(MESSAGES["2bryggs"])
            if(SEND_TO_SLACK):
                slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": MESSAGES["2bryggs"]})
                print(f"Slack: {slackresponse.text}")
            hue.setAllLights(10000) # yellow
            STATE["brewing"] = True
            STATE["sentEndMessage"] = False
            filewritten = writeStatsToFile(2)
            if(filewritten == -1):
                print("Failed to write stats to file.")

        # Coffee maker turned off
        elif(power == 0.0 and not STATE["sentEndMessage"]):
            print(MESSAGES["slut"])
            if(SEND_TO_SLACK):
                slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": MESSAGES["slut"]})
                print(f"Slack: {slackresponse.text}")
            hue.setAllLights(65000) # red
            resetState()

        # Idle, don't send messages
        elif(power == 0.0 and STATE["sentEndMessage"]):
            print("Bryggare avstängd.")

        time.sleep(MEASURE_INTERVAL)

if(__name__ == "__main__"):
    main()