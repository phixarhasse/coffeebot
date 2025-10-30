FROM debian:12
RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get install python3-venv -y

ADD . /kaffebot/
RUN ls
WORKDIR /kaffebot/

# Assuming somewhere on top there is already `python3-venv` installed 
# via system package manager, e.g. `apt-get install -y python3-venv`
RUN python3 -m venv .venv

RUN /kaffebot/.venv/bin/python3 -m pip install -r requirements.txt
CMD ["/kaffebot/.venv/bin/python3", "coffee-bot.py"]
