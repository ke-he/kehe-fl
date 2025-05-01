import unittest
from unittest.mock import MagicMock, patch
from kehe_fl.comms.mqtt_provider import MQTTClient


class TestMQTTClient(unittest.TestCase):

    @patch("kehe_fl.mqtt_client.mqtt.Client")  # Mock MQTT client
    def setUp(self, mock_mqtt):
        """Set up a mock MQTT client for each test"""
        self.mock_mqtt = mock_mqtt.return_value
        self.device_id = "device123"
        self.client = MQTTClient(broker="test.mosquitto.org", deviceId=self.device_id)

    def test_initialization(self):
        """Test if the client is initialized correctly"""
        self.assertEqual(self.client.broker, "test.mosquitto.org")
        self.assertEqual(self.client.port, 1883)
        self.assertEqual(self.client.clientTopic, f"sys/{self.device_id}/data")
        self.assertEqual(self.client.serverTopic, f"sys/{self.device_id}/cmd")

    def test_connect_calls_mqtt_connect(self):
        """Test that connect() calls mqtt.Client.connect()"""
        self.client.connect()
        self.mock_mqtt.connect.assert_called_with("test.mosquitto.org", 1883, 60)
        self.mock_mqtt.loop_start.assert_called_once()

    def test_disconnect_calls_mqtt_disconnect(self):
        """Test that disconnect() stops loop and disconnects"""
        self.client.disconnect()
        self.mock_mqtt.loop_stop.assert_called_once()
        self.mock_mqtt.disconnect.assert_called_once()

    def test_publish_calls_mqtt_publish(self):
        """Test that publish() calls mqtt.Client.publish() with correct parameters"""
        payload = "test message"
        self.client.publish(payload, qos=1, retain=True)
        self.mock_mqtt.publish.assert_called_with(self.client.clientTopic, payload, qos=1, retain=True)

    def test_on_connect_subscribes_to_server_topic(self):
        """Test that on_connect subscribes to the correct server topic"""
        self.client.on_connect(self.mock_mqtt, None, None, 0)
        self.mock_mqtt.subscribe.assert_called_with(f"sys/{self.device_id}/cmd")

    def test_on_message_receives_message(self):
        """Test that on_message prints the correct output"""
        mock_msg = MagicMock()
        mock_msg.topic = f"sys/{self.device_id}/cmd"
        mock_msg.payload.decode.return_value = "command1"

        with patch("builtins.print") as mock_print:
            self.client.on_message(self.mock_mqtt, None, mock_msg)
            mock_print.assert_called_with(f"Message received: command1 on topic sys/{self.device_id}/cmd")


if __name__ == "__main__":
    unittest.main()
