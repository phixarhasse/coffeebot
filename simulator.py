from flask import Flask, request

app = Flask(__name__)

VALUES = [0.0, 0.0, 0.0, 0.0,
          1257.4, 1523.3, 1493.6, 1300.2, 1300.7, 1302.4, 1297.2, 1300.2, 1300.7, 1302.4, 1297.2,
          1300.2, 1300.7, 1302.4, 1297.2, 1300.2, 1300.7, 1302.4, 1297.2,
          102.3, 102.3, 150.4, 149.2, 100.2, 100.2, 102.3, 102.3, 150.4,
          149.2, 100.2, 100.2, 102.3, 102.3, 150.4, 149.2, 100.2, 100.2,
          102.3, 102.3, 150.4, 149.2, 100.2, 100.2,
          0.0, 0.0]

VALUE_SELECTOR = 0

def incrementSelector():
    VALUE_SELECTOR = (VALUE_SELECTOR + 1) % len(VALUES)


@app.route('/meter/0', methods=['GET'])
def getMeterValue():
    simulatedValue = VALUES[VALUE_SELECTOR]
    incrementSelector()
    return simulatedValue

app.run(host='localhost', port=8080)