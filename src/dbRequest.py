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

        self.databaseName = "temperature_data"

        self.conn = psycopg2.connect(**db_params)
        self.cursor = self.conn.cursor()
        
    def database_Exists(self):
        self.cursor.execute(psycopg2.sql.SQL("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);"), [self.databaseName])
        return self.cursor.fetchone()[0]

    def create_table(self):
        if not self.database_Exists():
            query = f'''CREATE TABLE {self.databaseName}
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

    def push_to_database(self, timestamp: str, temperature: float):
        query = f"""
            INSERT INTO {self.databaseName} (timestamp, temperature)
            VALUES (%s, %s);
        """

        try:
            reading_timestamp = parser.isoparse(timestamp) #Parse the str temperature to datetime

            self.cursor.execute(query, [reading_timestamp, temperature])
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
    
    def close_DB_conn(self):
        self.cursor.close()
        self.conn.close()
