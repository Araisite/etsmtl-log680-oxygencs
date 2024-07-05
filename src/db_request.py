"""Module for handling database actions for temperature and HVAC data."""

import os
import psycopg2
import psycopg2.sql
from dateutil import parser


class DatabaseAction:
    """Class for performing database actions."""

    def __init__(self):
        """Initialize the database connection."""
        db_params = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASS"),
            "host": os.getenv("DATABASE_URL"),
            "port": os.getenv("DB_PORT"),
        }

        self.conn = psycopg2.connect(**db_params)
        self.cursor = self.conn.cursor()

    def database_exists(self, database_name):
        """Check if the specified database exists.

        Args:
            database_name (str): The name of the database to check.

        Returns:
            bool: True if the database exists, False otherwise.
        """
        self.cursor.execute(
            psycopg2.sql.SQL(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);"
            ),
            [database_name],
        )
        return self.cursor.fetchone()[0]

    def create_temperature_table(self):
        """Create the temperature_data table if it does not exist."""
        if not self.database_exists("temperature_data"):
            query = """CREATE TABLE temperature_data
                        (timestamp TIMESTAMP NOT NULL,
                        temperature FLOAT); 
                    """
            try:
                self.cursor.execute(query)
                self.conn.commit()
                print("Table created successfully")
            except Exception as e:
                print(f"An error occurred: {e}")
                self.conn.rollback()

    def create_hvac_action_table(self):
        """Create the hvac_data table if it does not exist."""
        if not self.database_exists("hvac_data"):
            query = """CREATE TABLE hvac_data
                        (timestamp TIMESTAMP NOT NULL,
                        action TEXT); 
                    """
            try:
                self.cursor.execute(query)
                self.conn.commit()
                print("Table created successfully")
            except Exception as e:
                print(f"An error occurred: {e}")
                self.conn.rollback()

    def push_to_temperature_database(self, timestamp: str, temperature: float):
        """Insert a temperature reading into the database.

        Args:
            timestamp (str): The timestamp of the reading.
            temperature (float): The temperature reading.
        """
        query = """
            INSERT INTO temperature_data (timestamp, temperature)
            VALUES (%s, %s);
        """

        try:
            reading_timestamp = parser.isoparse(
                timestamp
            )  # Parse the str timestamp to datetime
            self.cursor.execute(query, [reading_timestamp, temperature])
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()

    def push_to_hvac_action_database(self, timestamp: str, action: str):
        """Insert an HVAC action into the database.

        Args:
            timestamp (str): The timestamp of the action.
            action (str): The HVAC action.
        """
        query = """
            INSERT INTO hvac_data (timestamp, action)
            VALUES (%s, %s);
        """

        try:
            reading_timestamp = parser.isoparse(
                timestamp
            )  # Parse the str timestamp to datetime
            self.cursor.execute(query, [reading_timestamp, action])
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()

    def close_db_conn(self):
        """Close the database connection."""
        self.cursor.close()
        self.conn.close()
