# Version 1.5
# Shelly API doc: https://shelly-api-docs.shelly.cloud/
# This code is calibrated for a Moccamaster KBG744 AO-B (double brewer with 2 pots).
import requests
import time
from datetime import date
from datetime import datetime
from signal import signal, SIGINT
from sys import exit

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
    tolerance = 20.0
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
    if(value1 == 0.0 and value2 == 0.0): return value2
    elif(abs(value1 - value2) <= tolerance and
        abs(value1 - value2) > 1.0): return value2
    else: return -1.0

def resetState():
    STATE["brewing"] = False
    STATE["sentEndMessage"] = True
    STATE["coffeeDone"] = False

def exitHandler(numberofpots, start):
    print("Ctrl-c pressed. Exiting gracefully.")
    if(type(numberofpots) is int):
        print("Since {}, {} pots have been brewed.".format(start, numberofpots))
    print("Thank you for using CoffeeBot™!")
    exit(0)

def writeStatsToFile(pots):
    today = date.today()
    now = datetime.now()
    if(not type(pots) is int):
        print("Input to file not an integer")
        return -1
    try:
        # Open log file, creates if does not exist
        f = open("./logs/stats-{}.stat".format(today), "a")
        f.write("{}|{}".format(now, pots))
        f.close()
        return 0
    except Exception as e:
        print(e)
        return -1

def main():
    start = datetime.now()
    numberofpots = 0
    signal(SIGINT, exitHandler(numberofpots, start))
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
            numberofpots += 1
            filewritten = writeStatsToFile(1)
            if(filewritten == -1):
                print("Failed to write stats to file.")

        # Two pots are brewing
        elif(power > 2000.0 and not STATE["brewing"]):
            print(SLACK_MESSAGES["2bryggs"])
            slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["2bryggs"]})
            print("Slack: " + slackresponse.text)
            STATE["brewing"] = True
            STATE["sentEndMessage"] = False
            numberofpots += 2
            filewritten = writeStatsToFile(2)
            if(filewritten == -1):
                print("Failed to write stats to file.")

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

if(__name__ == "__main__"):
    main()