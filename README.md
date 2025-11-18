# Welcome to Coffeebot
Responsible for watching the office's coffee maker and sending notifications to a Slack channel.

## Hardware Requirements
[Shelly Plug or Plug S](https://www.shelly.cloud/products/shelly-plug-smart-home-automation-device/) for measuring coffeemaker power
and providing access to measurements through its embedded web server.

I recommend the Plug (without the 'S') as it's allows more current through it.

Optional: [Philips Hue Bridge](https://www.philips-hue.com/en-gb/p/hue-bridge/8719514342583) and [Hue Colored Lights](https://www.philips-hue.com/en-gb/products/smart-light-bulbs)

The Hue Bridge has an API through which coffeebot sets the color of all connected lights as follows:
- Red: coffeemaker turned off
- Slowly flashing yellow: coffee is brewing
- Green: coffee is done

## How to Install the Bot

The instructions assumes a working Python 3 enviroment. On `apt`-based operating systems try something like
`sudo apt install python3-pip python3-venv`.

### _Note: The bot is currently calibrated for a Moccamaster KBG744 AO-B (double brewer)._

1. Download and unpack the project where you want it to run from.
2. Copy `.env-template` to `.env`  and adjust the following environment variables to the .env file:

```sh
USE_SLACK=      # True if you want to send coffee updates to Slack
SLACK_TOKEN=    # Secret OAuth authentication token for the app in Slack (you need to add an app called "CoffeeBot" to your Slack workspace to generate one)
CHANNEL_ID=     # ID of the channel to post messages in Slack
USE_HUE=        # True if you want your Hue lights to reflect coffee status
HUE_IP=         # The local IP address of the Hue Bridge
SENSOR_URL=     # The complete URL to the Shelly Plug, e.g. "http://192.168.0.10/meter/0" without the quotes (see Shelly docs for more details)
```

3. Copy `hue-template` to `hue_username` and change to your username in the file
4. If you chose to use Slack and/or Hue, the script will first setup these services. During Hue setup, you will be prompted to go press the button on the Hue Bridge to generate a token for the bot to use.
5. python3 -m venv env                 # Create python virtual enviroment 
5. source env/bin/activate             # Activate python virtual enviroment
6. pip install -r requirements.txt     # Install all dependencies
7. deactivate                          # Deactivate the enviroment

## How to use HTTPS

Philips state in the API documentation that you should use HTTPS when going to production. 
1. Get the Hue Bridge certificate by running `C:\coffeebot> openssl s_client -showcerts -connect [Hue Bridge IP]:443` and save it as a `.crt` file, or open the URL to 
the bridge in a web browser and download the certificate from the browser's security info (the padlock near the URL).
2. Install the certificate in the appropriate place where the coffeebot is running. On Linux, this would be by copying the `.crt` file to `/usr/share/ca-certificates` 
and run `%> sudo update-ca-certificates`.
3. The certificate is broken according to https://www.reddit.com/r/Hue/comments/1npl0id/philips_hue_bridge_ssl_certificates_are_broken/ so for now you must tell the 
API calls to not verify the certificate: `requests.get(<url>, verify=False)` 

## How to Run the Bot

1. `source env/bin/activate` activates the python enviroment
2. `python coffee-bot.py` run Coffeebot
3. `deactivate` deactivates the enviroment
4. Now the bot should be running, time to make some coffee!

## Development

If you add any extra dependencies run (while inside the python enviroment)
`pip list --local --format=freeze > requirements.txt`
to update the requirements.

## Backlog
See [Issues](https://github.com/phixarhasse/coffeebot/issues)
