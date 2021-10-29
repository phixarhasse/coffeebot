import requests

class Hue:
    def __init__(self, bridgeIp):
        self.bridgeIp = bridgeIp
        self.url = f"http://{bridgeIp}/api"
        self.lights = []
        self.username = ""

    def saveUsername(self, username):
        try:
            f = open("hue_username", "w")
            f.write(username)
            f.close()
        except Exception as e:
            print(e)
    
    def loadUsername(self):
        try:
            f = open("hue_username", "r")
            self.username = f.readline()
            f.close()
        except Exception as e:
            print(e)
            self.username = ""
            return

    def authorize(self):
        self.username = ""
        try:
            hueResponse = requests.post(self.url, json={"devicetype": "coffeebot"})
            if(hueResponse.json()[0]["error"]["type"] == 101): # Need to generate username
                print("Please press the link button on the HUE Bridge.")
                user_input = input("Have you pressed it? [y/n] ")
                if(not user_input == 'y'):
                    print("Error during Hue authentication. Exiting.")
                    exit(1)
                else:
                    hueResponse = requests.post(self.url, json={"devicetype": "coffeebot"})
                    username = hueResponse.json()[0]["success"]["username"]
                    self.username = username
                    self.saveUsername(username)
            elif(hueResponse.ok):
                username = hueResponse.json()[0]["success"]["username"]
                self.username = username
                self.saveUsername(username)
        except Exception as e:
            print("Error during Hue authentication.")
            print("Exception: ", e)
            return

    def getLights(self):
        self.lights = []
        if(self.username == ""):
            return
        try:
            hueResponse = requests.get(f"{self.url}/{self.username}/lights/")
            if(not hueResponse.ok):
                print("Unable to get Hue lights.")
                return
        except Exception as e:
            print(e)
            return
        for light in hueResponse.json():
            self.lights.append(light)
        return
    
    def setAllLights(self, color):
        try:
            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.url}/{self.username}/lights/{light}/state",
                    json={"on":True, "sat": 254, "bri":200, "hue": color})
                print(f"Hue light {light}: {hueResponse.status_code}")
        except Exception as e:
            print(e)
            return
    
    def turnOffAllLights(self):
        try:
            for light in self.lights:
                hueResponse = requests.put(
                    f"{self.url}/{self.username}/lights/{light}/state",
                    json={"on":False})
                print(f"Hue light {light}: {hueResponse.status_code}")
        except Exception as e:
            print(e)
            return
