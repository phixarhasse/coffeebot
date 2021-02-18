# Version 1.4
# Shelly API doc: https://shelly-api-docs.shelly.cloud/
# This code is calibrated for a Moccamaster KBG744 AO-B (double brewer with 2 pots).
import requests
import time

SENSOR_URL = "http://url-to-shelly/status"
SLACK_URL = ""
HEADERS = {"Content-Type":"application/json"}
SLACK_MESSAGES = {"1bryggs":"Nu bryggs det 1 kanna! :building_construction:",
                  "2bryggs":"Nu bryggs det 2 kannor! :building_construction: :building_construction:",
                  "klart":"Nu är kaffet färdigt! :coffee: :brown_heart:",
                  "slut":"Bryggare avstängd. :broken_heart:",
                  "svalnande": "Någon räddar svalnande kaffe! :ambulance:"}

# Dict to represent brewer state
STATE = {"brewing": False, "sentEndMessage": True, "coffeeDone": False}

MEASURE_INTERVAL = 10 # seconds

"""Polls the Shelly embedded web server for power usage [Watt] twice with MEASURE_INTERVAL seconds between.
Returns second value if valid measure, -1.0 otherwise.
"""
def measure():
    tolerance = 10
    try:
        response = requests.request("GET", SENSOR_URL)
    except Exception as e:
        print(e)
        return -1.0
    value1 = float(response.json()['meters'][0]['power'])
    # Increase tolerance for higher values
    if(value1 > 2000.0):
        tolerance = 40
    print(value1,"Watt")
    time.sleep(MEASURE_INTERVAL)
    try:
        response = requests.request("GET", SENSOR_URL)
    except Exception as e:
        print(e)
        return -1.0
    value2 = float(response.json()['meters'][0]['power'])
    print(value2, "Watt")
    # If diff is larger than 10, the power is still changing
    # Diffs lower than 1.0 should not trigger anything
    if((not abs(value1 - value2) > tolerance) or
        (not abs(value1 - value2) < 1.0)): return value2
    else: return -1.0

def resetState():
    STATE["brewing"] = False
    STATE["sentEndMessage"] = True
    STATE["coffeeDone"] = False

# Main loop
while(True):
    power = measure()
    if(power == -1.0):
        # Power is still changing or an exception occured, wait and measure again
        time.sleep(MEASURE_INTERVAL)
        continue

    # Heating old coffee
    elif((power > 1.0) and (power <= 300.0) and not STATE["brewing"] and not STATE["coffeeDone"]):
        print(SLACK_MESSAGES["svalnande"])
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["svalnande"]})
        print("Slack: " + slackresponse.text)
        STATE["coffeeDone"] = True
        STATE["sentEndMessage"] = False

    # Fresh coffee has been made
    elif((power > 1.0) and (power <= 300.0) and STATE["brewing"]):
        # Wait for coffee to drip down
        time.sleep(30)
        print(SLACK_MESSAGES["klart"])
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["klart"]})
        print("Slack says: " + slackresponse.text)
        STATE["coffeeDone"] = True
        STATE["brewing"] = False

    # One pot is brewing
    elif(power > 1000.0 and power <= 2000.0 and not STATE["brewing"]):
        print(SLACK_MESSAGES["1bryggs"])
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["1bryggs"]})
        print("Slack: " + slackresponse.text)
        STATE["brewing"] = True
        STATE["sentEndMessage"] = False

    # Two pots are brewing
    elif(power > 2000.0 and not STATE["brewing"]):
        print(SLACK_MESSAGES["2bryggs"])
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["2bryggs"]})
        print("Slack: " + slackresponse.text)
        STATE["brewing"] = True
        STATE["sentEndMessage"] = False

    # Coffee maker turned off
    elif(power == 0.0 and not STATE["sentEndMessage"]):
        print(SLACK_MESSAGES["slut"])
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["slut"]})
        print("Slack: " + slackresponse.text)
        resetState()
        
    # Idle, don't send messages
    elif(power == 0.0 and STATE["sentEndMessage"]):
        print("Bryggare avstängd.")

    time.sleep(MEASURE_INTERVAL)
