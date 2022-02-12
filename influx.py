from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

class Influx:
    def __init__(self, url, token, org, bucket):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.dbclient = InfluxDBClient(url=self.url, token=self.token, org=self.org)

# You can generate an API token from the "API Tokens Tab" in the UI (http://localhost:8086)
token = ""
org = ""
bucket = "coffeebot-watt-values"

dbclient = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
