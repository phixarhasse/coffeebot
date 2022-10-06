# Coffeebot
Responsible for watching the office's coffee maker and sending notifications to a Slack channel.

## How to Install

1. Clone the repository and move into the cloned repository
2. Copy `.env-template` to `.env`  and change to your credentials
3. Copy `hue-template` to `hue_username` and change to your username in the file
4. Update the global variables `SENSOR_URL` and `SLACK_URL` in `coffee-bot.py`

```sh
source env/bin/activate             # Activate python enviroment
pip install -r requirements.txt     # Installs all dependencies
deactivate                          # To deactivate the enviroment
```

## How to Run

```sh
source env/bin/activate # Activate python enviroment
python3 coffee-bot.py   # To run Coffeebot
deactivate              # To deactivate the enviroment
```

Make some coffee!

## Backlog
See 'Issues'
