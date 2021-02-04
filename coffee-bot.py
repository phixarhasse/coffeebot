# Shelly API doc: https://shelly-api-docs.shelly.cloud/
# This code is calibrated for a Moccamaster KBG744 AO-B (double brewer with 2 pots).
import requests
import time

SENSOR_URL = "url-to-shelly-plug/status"
SLACK_URL = ""
HEADERS = {"Content-Type":"application/json"}
SLACK_MESSAGES = {"1bryggs":"Nu bryggs det 1 kanna! :building_construction:",
                  "2bryggs":"Nu bryggs det 2 kannor! :building_construction: :building_construction:",
                  "1klar":"1 kanna färdig! :coffee:",
                  "2klar":"2 kannor färdiga! :coffee: :coffee:",
                  "1gammal":"Någon värmer 1 kanna gammalt kaffe. Mums!",
                  "2gammla":"Någon värmer 2 kannor gammalt kaffe. Mums!",
                  "slut":"Bryggare avstängd. :broken_heart:"}

# Dict to represent brewer state
STATE = {"brewing": False, "sentEndMessage": True, "onePotDone": False, "twoPotsDone": False}
MEASURE_INTERVAL = 10 # seconds

def measure():
    try:
        response = requests.request("GET", SENSOR_URL)
    except Exception as e:
        print(e)
        return -1.0
    value1 = float(response.json()['meters'][0]['power'])
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
    if(not abs(value1 - value2) > 10): return value2
    else: return -1.0

def resetState():
    STATE["brewing"] = False
    STATE["sentEndMessage"] = True
    STATE["onePotDone"] = False
    STATE["twoPotsDone"] = False


# Main loop
while(True):
    power = measure()
    if(power == -1.0):
        # Power is still changing or an exception occured, wait and measure again
        time.sleep(MEASURE_INTERVAL)
        continue

    # Heating 1 old pot
    elif((power > 0.0) and (power <= 100.0) and not STATE["brewing"] and not STATE["onePotDone"]):
        print(SLACK_MESSAGES["1gammal"])
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["1gammal"]})
        print("Slack: " + slackresponse.text)
        STATE["onePotDone"] = True
        STATE["sentEndMessage"] = False

    # Heating 1 fresh pot
    elif((power > 0.0) and (power <= 100.0) and STATE["brewing"]):
        print(SLACK_MESSAGES["1klar"])
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["1klar"]})
        print("Slack: " + slackresponse.text)
        STATE["onePotDone"] = True
        STATE["brewing"] = False
    
    # Heating 2 old pots
    elif((power > 100.0) and (power <= 300.0) and not STATE["brewing"] and not STATE["twoPotsDone"]):
        print(SLACK_MESSAGES["2gammla"])
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["2gammla"]})
        print("Slack: " + slackresponse.text)
        STATE["twoPotsDone"] = True
        STATE["sentEndMessage"] = False
        
    # Heating 2 fresh pots
    elif((power > 100.0) and (power <= 300.0) and STATE["brewing"]):
        print(SLACK_MESSAGES["2klar"])
        slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["2klar"]})
        print("Slack: " + slackresponse.text)
        STATE["twoPotsDone"] = True
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