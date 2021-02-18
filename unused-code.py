# This is just kept as an archive to not clog up main file

# SLACK_MESSAGES = {"1klar":"1 kanna färdig! :coffee:","2klar":"2 kannor färdiga! :coffee: :coffee:","1gammal":"Någon värmer 1 kanna gammalt kaffe. Mums!","2gammla":"Någon värmer 2 kannor gammalt kaffe. Mums!"}

# # Heating 1 fresh pot
# elif((power > 0.0) and (power <= 100.0) and STATE["brewing"]):
#     print(SLACK_MESSAGES["1klar"])
#     slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["1klar"]})
#     print("Slack: " + slackresponse.text)
#     STATE["onePotDone"] = True
#     STATE["brewing"] = False

# # Heating 2 old pots
# elif((power > 100.0) and (power <= 300.0) and not STATE["brewing"] and not STATE["twoPotsDone"]):
#     print(SLACK_MESSAGES["2gammla"])
#     slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["2gammla"]})
#     print("Slack: " + slackresponse.text)
#     STATE["twoPotsDone"] = True
#     STATE["sentEndMessage"] = False
        
# # Heating 2 fresh pots
# elif((power > 100.0) and (power <= 300.0) and STATE["brewing"]):
#     print(SLACK_MESSAGES["2klar"])
#     slackresponse = requests.post(SLACK_URL, headers = HEADERS, json = {"text": SLACK_MESSAGES["2klar"]})
#     print("Slack: " + slackresponse.text)
#     STATE["twoPotsDone"] = True
#     STATE["brewing"] = False

# def resetState():
    # STATE["onePotDone"] = False
    # STATE["twoPotsDone"] = False