"""The main app is there!"""

import logging
import json
import time
import os
import requests

from signalrcore.hub_connection_builder import HubConnectionBuilder

from dotenv import load_dotenv

from db_request import DatabaseAction

load_dotenv()

# Global variables for environment variables
HOST = os.getenv("HOST")
TOKEN = os.getenv("TOKEN")
T_MAX = float(os.getenv("T_MAX"))
T_MIN = float(os.getenv("T_MIN"))
DATABASE_URL = os.getenv("DATABASE_URL")

# Test


class App:
    """Main application"""

    def __init__(self):
        self._hub_connection = None
        self.ticks = 10

        self.db_request = DatabaseAction()
        self.db_request.create_temperature_table()
        self.db_request.create_hvac_action_table()

    def __del__(self):
        if self._hub_connection is not None:
            self._hub_connection.stop()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{HOST}/SensorHub?token={TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(timestamp, temperature)
            self.save_event_to_database(timestamp, temperature)
        except Exception as err:
            print(err)

    def take_action(self, timestamp, temperature):
        """Take action to HVAC depending on current temperature."""
        action = ""

        if temperature >= T_MAX:
            action = "TurnOnAc"
        elif temperature <= T_MIN:
            action = "TurnOnHeater"
        self.send_action_to_hvac(action)
        self.db_request.push_to_hvac_action_database(timestamp, action)

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        try:
            r = requests.get(
                f"{HOST}/api/hvac/{TOKEN}/{action}/{self.ticks}", timeout=10
            )
            details = json.loads(r.text)
            print(details, flush=True)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    def save_event_to_database(self, timestamp, temperature):
        """Save sensor data into database."""
        try:
            self.db_request.push_to_temperature_database(timestamp, temperature)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    app = App()
    app.start()
    app.db_request.close_DB_conn()
