# Version 4.0.0
# Shelly API doc: https://shelly-api-docs.shelly.cloud/
# This code is calibrated for a Moccamaster KBG744 AO-B (double brewer with 2 pots).

"""
TODO: Automatic or semiautomatic calibration
TODO: Approximate amount of coffee made by timing a full pot brewing.
Problematic with a double brewer, as the second pot is not always started at the same time as the first.
"""

import os
import time
import asyncio
import logging
import requests
from hue import Hue
from slack import Slack
from db.mongodb import MongoDb
from dotenv import load_dotenv

# Dict representing brewer state
STATE = {"brewing": False, "turnedOff": True, "coffeeDone": False}
MEASURE_INTERVAL = 5  # seconds


"""
Main loop
"""


async def main() -> None:
    # Setup logging
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    loadAndCheckEnvironment()

    sensor_url = os.getenv("SENSOR_URL")

    slack = None
    hue = None
    if (os.getenv("USE_SLACK") == "True"):
        slack = Slack()
    if (os.getenv("USE_HUE") == "True"):
        hue = Hue()

    db = None
    if (os.getenv("STORE_DATA") == "True"):
        logging.info("Connecting to MongoDb Database...")
        try:
            db = MongoDb(url=os.getenv("MONGODB_CONNECTION_STRING"),
                         db=os.getenv("MONGODB_DATABASE"), collection=os.getenv("MONGODB_COLLECTION"))
            logging.info("MongoDb Database connection successful")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDb Database: {e}")
            quit(1)

    while (True):
        power = await measure(sensor_url, db=db)
        if (power == -1.0):
            # Power is still changing or an exception occured, wait and measure again
            time.sleep(MEASURE_INTERVAL/2)
            continue

        # Heating old coffee
        elif ((power > 1.0) and (power <= 300.0) and not STATE["brewing"] and not STATE["coffeeDone"]):
            heatingOldCoffee(hue, slack)

        # Fresh coffee has been made
        elif ((power > 1.0) and (power <= 300.0) and STATE["brewing"]):
            freshCoffeeHasBeenMade(hue, slack)

        # Coffee is brewing
        elif (power > 1000.0 and not STATE["brewing"]):
            coffeeIsBrewing(hue, slack)

        # Still brewing, make lights blink
        elif (power > 1000.0 and STATE["brewing"]):
            stillBrewing(hue)

        # Coffee maker turned off
        elif (power == 0.0 and not STATE["turnedOff"]):
            coffeeMakerTurnedOff(hue, slack)

        # Idle, don't send messages
        elif (power == 0.0 and STATE["turnedOff"]):
            continue

        time.sleep(MEASURE_INTERVAL)


def loadAndCheckEnvironment():
    env_loaded = load_dotenv(".env")  # Load environment variables
    if (not env_loaded):
        logging.error("Could not load .env file. Exiting.")
        quit(1)
    try:
        sensor_url = os.getenv("SENSOR_URL")
        if (sensor_url == "" or sensor_url is None):
            raise KeyError
    except KeyError:
        logging.error(
            "Could not parse SENSOR_URL in the file '.env'. Exiting.")
        quit(1)

    try:
        use_slack = os.getenv("USE_SLACK")
        slack_token = os.getenv("SLACK_TOKEN")
        slack_channel = os.getenv("SLACK_CHANNEL")
        use_hue = os.getenv("USE_HUE")
        hue_ip = os.getenv("HUE_IP")
        store_data = os.getenv("STORE_DATA")
        mongodb_connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        mongodb_database = os.getenv("MONGODB_DATABASE")
        mongodb_collection = os.getenv("MONGODB_COLLECTION")

        if (not use_slack and not use_hue and not store_data):
            logging.error("No services enabled. Exiting.")
            quit(1)
        elif (use_slack and (slack_token == "" or slack_channel == "")):
            logging.error(
                "Slack is active but missing auth token and/or channel ID. Exiting.")
            quit(1)
        elif (use_hue and hue_ip == ""):
            logging.error(
                "Hue is active but missing bridge IP address. Exiting.")
            quit(1)
        elif (store_data and (mongodb_connection_string == "" or mongodb_database == "" or mongodb_collection == "")):
            logging.error(
                "Storing data is active but missing MongoDB connection string, database name or collection name. Exiting.")
            quit(1)

    except KeyError:
        logging.error(
            "Could not parse one or more environment variables in the file '.env'. Exiting.")
        quit(1)


"""
Polls the Shelly embedded web server for power usage [Watt] twice with MEASURE_INTERVAL seconds between.
If databse is active, stores the values in the MongoDB database.
Returns second value if valid measure, -1.0 otherwise.
"""


async def measure(sensor_url: str, db: MongoDb | None) -> float:
    tolerance = 40.0
    try:
        response = requests.request("GET", sensor_url)
    except Exception as e:
        logging.error(e)
        return -1.0
    value1 = float(response.json()['power'])
    if (db):
        await db.store(value1)
    # Increase tolerance for higher values
    if (value1 > 2000.0):
        tolerance = 80
    logging.debug(f"{value1} Watt")
    time.sleep(MEASURE_INTERVAL)
    try:
        response = requests.request("GET", sensor_url)
    except Exception as e:
        print(e)
        return -1.0
    value2 = float(response.json()['power'])
    if (db):
        await db.store(value2)
    logging.debug(f"{value2} Watt")

    # If diff is larger than tolerance, the power is still changing
    # Diffs lower than 1.0 are ignored
    if (value1 == 0.0 and value2 == 0.0):
        return value2
    elif (abs(value1 - value2) <= tolerance and
          abs(value1 - value2) > 1.0):
        return value2
    else:
        return -1.0


"""
Resets global dict respresenting the brewer state
"""


def resetState() -> None:
    STATE["brewing"] = False
    STATE["turnedOff"] = True
    STATE["coffeeDone"] = False


"""
Messaging and Hue control functions
"""


def heatingOldCoffee(hue: Hue | None, slack: Slack | None) -> None:
    logging.info("Heating old coffee.")
    if (slack):
        slack.deleteLastMessage()
        slack.postMessage(slack.messages["saving"])

    if (hue):
        hue.setAllLights(29000)  # green

    STATE["coffeeDone"] = True
    STATE["turnedOff"] = False


def coffeeIsBrewing(hue: Hue | None, slack: Slack | None) -> None:
    logging.info("Coffee is brewing.")
    if (slack):
        slack.deleteLastMessage()
        slack.postMessage(slack.messages["brewing"])

    if (hue):
        hue.setAllLights(10000)  # yellow

    STATE["brewing"] = True
    STATE["turnedOff"] = False


def freshCoffeeHasBeenMade(hue: Hue | None,  slack: Slack | None) -> None:
    time.sleep(30)  # Wait 30 seconds for coffee to drip down
    logging.info("Fresh coffee has been made.")
    if (slack):
        slack.deleteLastMessage()
        slack.postMessage(slack.messages["done"])

    if (hue):
        hue.setAllLights(29000)  # green

    STATE["coffeeDone"] = True
    STATE["brewing"] = False


def stillBrewing(hue: Hue | None) -> None:
    if (hue):
        hue.turnOffAllLights()
        time.sleep(1)
        hue.setAllLights(10000)  # yellow


def coffeeMakerTurnedOff(hue: Hue | None,  slack: Slack | None) -> None:
    logging.info("Coffee maker turned off.")
    resetState()
    if (slack):
        slack.deleteLastMessage()
        slack.postMessage(slack.messages["off"])

    if (hue):
        hue.setAllLights(65000)  # red


if (__name__ == "__main__"):
    asyncio.run(main())
