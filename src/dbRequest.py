"""The database management is done here !"""

import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.sql
from dateutil import parser

class DatabaseAction():
    def __init__(self):
        db_params = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'host': os.getenv('DATABASE_URL'),
            'port': os.getenv('DB_PORT')
        }

        self.conn = psycopg2.connect(**db_params)
        self.cursor = self.conn.cursor()

    def database_Exists(self, databaseName):
        self.cursor.execute(psycopg2.sql.SQL("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);"), [databaseName])
        return self.cursor.fetchone()[0]

    def create_temperature_table(self):
        if not self.database_Exists("temperature_data"):
            query = '''CREATE TABLE temperature_data
                        (timestamp TIMESTAMP NOT NULL,
                        temperature FLOAT); 
                    '''
            try:
                self.cursor.execute(query)
                self.conn.commit()
                print("Table create successfully")
            except Exception as e:
                print(f"An error occurred: {e}")
                self.conn.rollback()

    def create_HVAC_Action_table(self):
        if not self.database_Exists("hvac_data"):
            query = '''CREATE TABLE hvac_data
                        (timestamp TIMESTAMP NOT NULL,
                        action TEXT); 
                    '''
            try:
                self.cursor.execute(query)
                self.conn.commit()
                print("Table create successfully")
            except Exception as e:
                print(f"An error occurred: {e}")
                self.conn.rollback()

    def push_to_temperature_database(self, timestamp: str, temperature: float):
        query = """
            INSERT INTO temperature_data (timestamp, temperature)
            VALUES (%s, %s);
        """

        try:
            reading_timestamp = parser.isoparse(timestamp) #Parse the str temperature to datetime

            self.cursor.execute(query, [reading_timestamp, temperature])
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
    
    def push_to_hvacAction_database(self, timestamp: str, action: str):
        query = """
            INSERT INTO hvac_data (timestamp, action)
            VALUES (%s, %s);
        """

        try:
            reading_timestamp = parser.isoparse(timestamp) #Parse the str temperature to datetime

            self.cursor.execute(query, [reading_timestamp, action])
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
    
    def close_DB_conn(self):
        self.cursor.close()
        self.conn.close()
