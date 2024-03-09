from pymongo import MongoClient
from datetime import datetime
import logging


'''
MongoDb class responsible for storing and retrieving data from MongoDB

An MongoDB Atlas free tier with 5GB storage will hold about 2 months of data
when storing a value every 5 seconds.
'''


class MongoDb:
    def __init__(self, url: str, db: str, collection: str):
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")
        self.client = MongoClient(
            host=url)
        self.db = self.client[db]
        self.collection = self.db[collection]

    async def store(self, value: float):
        document = {
            "ts": datetime.now(),
            "power": value
        }
        try:
            result = self.collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            logging.error(f"Failed to store data in MongoDb: {e}")
            return None

    async def retrieve(self, document_id):
        try:
            document = self.collection.find_one({'_id': document_id})
            return {"ts": document["ts"], "power": document["power"]}
        except Exception as e:
            logging.error(f"Failed to retrieve data from MongoDb: {e}")
            return {}
