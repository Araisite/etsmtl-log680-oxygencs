"""All tests should be here !"""


print("Pre-commit working !")
import pytest
from unittest.mock import patch, Mock
import os
from src.main import App
from src.db_request import DatabaseAction

@pytest.fixture(scope='module')
def app():
    # Charger les variables d'environnement pour les tests
    os.environ['HOST'] = 'http://159.203.50.162'
    os.environ['TOKEN'] = 'c41bfe2de1f7b6404fbe'
    os.environ['T_MAX'] = '22'
    os.environ['T_MIN'] = '18'
    os.environ['DATABASE_URL'] = '157.230.69.113'
    
    app = App()
    yield app
    app.db_request.close_DB_conn()

@pytest.fixture(scope='module')
def db_action():
    db_action = DatabaseAction()
    db_action.create_temperature_table()
    db_action.create_hvac_action_table()
    yield db_action
    db_action.close_DB_conn()

def test_on_sensor_data_received(app):
    data = [{"date": "2024-07-04T12:00:00", "data": "23.0"}]
    with patch.object(app, 'take_action') as mock_take_action, \
         patch.object(app, 'save_event_to_database') as mock_save_event:
        app.on_sensor_data_received(data)
        mock_take_action.assert_called_once_with("2024-07-04T12:00:00", 23.0)
        mock_save_event.assert_called_once_with("2024-07-04T12:00:00", 23.0)

def test_take_action_turn_on_ac(app):
    timestamp = "2024-07-04T12:00:00"
    temperature = 25.0
    with patch.object(app, 'send_action_to_hvac') as mock_send_action, \
         patch.object(app.db_request, 'push_to_hvac_action_database') as mock_db_push:
        app.take_action(timestamp, temperature)
        mock_send_action.assert_called_once_with("TurnOnAc")
        mock_db_push.assert_called_once_with(timestamp, "TurnOnAc")

def test_take_action_turn_on_heater(app):
    timestamp = "2024-07-04T12:00:00"
    temperature = 15.0
    with patch.object(app, 'send_action_to_hvac') as mock_send_action, \
         patch.object(app.db_request, 'push_to_hvac_action_database') as mock_db_push:
        app.take_action(timestamp, temperature)
        mock_send_action.assert_called_once_with("TurnOnHeater")
        mock_db_push.assert_called_once_with(timestamp, "TurnOnHeater")

def test_send_action_to_hvac(app):
    action = "TurnOnAc"
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.text = '{"status": "success"}'
        mock_get.return_value = mock_response
        app.send_action_to_hvac(action)
        mock_get.assert_called_once_with(f'http://159.203.50.162/api/hvac/c41bfe2de1f7b6404fbe/{action}/{app.ticks}', timeout=10)

def test_save_event_to_database(app):
    timestamp = "2024-07-04T12:00:00"
    temperature = 23.0
    with patch.object(app.db_request, 'push_to_temperature_database') as mock_db_push:
        app.save_event_to_database(timestamp, temperature)
        mock_db_push.assert_called_once_with(timestamp, temperature)

def test_push_to_temperature_database(db_action):
    timestamp = "2024-07-04T12:00:00"
    temperature = 23.0
    db_action.push_to_temperature_database(timestamp, temperature)
    result = db_action.get_last_temperature_entry()
    assert result == (timestamp, temperature)

def test_push_to_hvac_action_database(db_action):
    timestamp = "2024-07-04T12:00:00"
    action = "TurnOnAc"
    db_action.push_to_hvac_action_database(timestamp, action)
    result = db_action.get_last_hvac_action_entry()
    assert result == (timestamp, action)
