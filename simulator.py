from flask import Flask

app = Flask(__name__)

VALUES = [0.0, 0.0, 0.0, 0.0,
          1257.4, 1523.3, 1493.6, 1300.2, 1300.7, 1302.4, 1297.2, 1300.2, 1300.7, 1302.4, 1297.2,
          1257.4, 1523.3, 1493.6, 1300.2, 1300.7, 1302.4, 1297.2, 1300.2, 1300.7, 1302.4, 1297.2,
          1300.2, 1300.7, 1302.4, 1297.2, 1300.2, 1300.7, 1302.4, 1297.2,
          102.3, 102.3, 150.4, 149.2, 100.2, 100.2, 102.3, 102.3, 150.4,
          149.2, 100.2, 100.2, 102.3, 102.3, 150.4, 149.2, 100.2, 100.2,
          149.2, 100.2, 100.2, 102.3, 102.3, 150.4, 149.2, 100.2, 100.2,
          149.2, 100.2, 100.2, 102.3, 102.3, 150.4, 149.2, 100.2, 100.2,
          102.3, 102.3, 150.4, 149.2, 100.2, 100.2,
          0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

VALUE_SELECTOR = 0

def incrementSelector():
    global VALUE_SELECTOR, VALUES
    VALUE_SELECTOR = (VALUE_SELECTOR + 1) % len(VALUES)


@app.route('/', methods=['GET'])
def root():
    return "Hello world!"

@app.route('/meter/0', methods=['GET'])
def getMeterValue():
    global VALUE_SELECTOR, VALUES
    simulatedValue = VALUES[VALUE_SELECTOR]
    incrementSelector()
    return {"power": simulatedValue}

app.run(host='localhost', port=5000)