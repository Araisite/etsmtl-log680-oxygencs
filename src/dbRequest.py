import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.sql

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
        
    def database_Exists(self, databaseName: str):
        self.cursor.execute(psycopg2.sql.SQL("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);"), [databaseName])
        return self.cursor.fetchone()[0]

    def create_table(self, databaseName: str):
        if not self.database_Exists(databaseName):
            query = f'''CREATE TABLE {databaseName}
                        (id SERIAL PRIMARY KEY,
                        reading_timestamp TIMESTAMP NOT NULL,
                        temperature FLOAT); 
                    '''
            try:
                self.cursor.execute(query)
                self.conn.commit()
                print("Table create successfully")
            except Exception as e:
                print(f"An error occurred: {e}")
                self.conn.rollback()
    
    def close_DB_conn(self):
        self.cursor.close()
        self.conn.close()
