# Welcome to coffeebot
Responsible for watching the office's coffee maker and sending notifications to a Slack channel.

## Hardware requirements
[Shelly Plug or Plug S](https://www.shelly.cloud/products/shelly-plug-smart-home-automation-device/) for measuring coffeemaker power
and providing access to measurements through its embedded web server.

I recommend the Plug (without the 'S') as it's allows more current through it.

Optional: [Philips Hue Bridge](https://www.philips-hue.com/en-gb/p/hue-bridge/8719514342583) and [Hue Colored Lights](https://www.philips-hue.com/en-gb/products/smart-light-bulbs)

The Hue Bridge has an API through which coffeebot sets the color of all connected lights as follows:
- Red: coffeemaker turned off
- Slowly flashing yellow: coffee is brewing
- Green: coffee is done

## How to run
1. Download and unpack the project where you want it to run from.
2. Add a file called `.env` inside the project folder.
3. Add the following environment variables to the .env file:
```
USE_SLACK=True if you want to send coffee updates to Slack
USE_HUE=True if you want your Hue lights to reflect coffee status
SLACK_TOKEN=Secret OAuth authentication token for the app in Slack (you need to add an app called "CoffeeBot" to your Slack workspace to generate one)
CHANNEL_ID=ID of the channel to post messages in Slack
HUE_IP=The local IP address of the Hue Bridge
SENSOR_URL=The complete URL to the Shelly Plug, e.g. "http://192.168.0.10/meter/0" without the quotes (see Shelly docs for more details)
```


## Backlog
See 'Issues'
