import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv

class db:
    def __init__(self):
        try:
            self.host = os.environ['DB_HOST']
            self.user = os.environ['DB_USER']
            self.password = os.environ['DB_PASSWORD']
            self.ssl_ca = os.environ['DB_PATH_TO_SSL_CA']
            self.database = os.environ['DB_DATABASE']
            self.table = os.environ['DB_TABLE']
        except KeyError:
            print("Could not parse database parameters.")
            quit()
        try:
            db_config = {
                "host": self.host,
                "user": self.user,
                "password": self.password,
                "database": self.database,
                "client_flags":[mysql.connector.ClientFlag.SSL],
                "ssl_ca":self.ssl_ca
                }
            self.conn = mysql.connector.connect(**db_config)
            print("Database connection established")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
              print("Something is wrong with the user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            self.cursor = self.conn.cursor()

            # Create table if not exists
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table}(ts INT(11) NOT NULL DEFAULT 0, watts DOUBLE NOT NULL DEFAULT 0.0);")
            print("Finished creating table.")

