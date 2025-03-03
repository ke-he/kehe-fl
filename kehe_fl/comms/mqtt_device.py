from socketserver import UDPServer

from mqtt_provider import MQTTProvider

class MQTTDevice(MQTTProvider):
    UPDATE_TOPIC = "sys/update"
    CMD_TOPIC = "sys/cmd"

    def __init__(self, broker, deviceId, port=1883, username=None, password=None, tls_config=None):
        super().__init__(broker, port, username, password, tls_config)
        self.deviceId = deviceId
        self.clientTopic = f"sys/{deviceId}/data"
        self.loginTopic = f"sys/{deviceId}/login"
        self.serverTopics = [self.UPDATE_TOPIC, self.CMD_TOPIC]

    def on_connect(self, client, userdata, flags, rc):
        super().on_connect(client, userdata, flags, rc)

        self.__handle_login()

        for topic in self.serverTopics:
            self.client.subscribe(topic)
            print(f"[MQTTDevice - {self.deviceId}] Subscribed to {topic}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        if topic == self.CMD_TOPIC:
            self.__handle_command(msg.payload.decode())
        elif topic == self.UPDATE_TOPIC:
            self.__handle_update(msg.payload.decode())
        else:
            print(f"[MQTTDevice - {self.deviceId}] Received unknown topic {msg.topic}: {msg.payload.decode()}")

    def send_data(self, data):
        print(f"[MQTTDevice - {self.deviceId}] Sending data: {data} to {self.clientTopic}")
        self.publish(self.clientTopic, data)

    def __handle_login(self):
        print(f"[MQTTDevice - {self.deviceId}] Logging in")
        self.publish(self.loginTopic, "login")

    def __handle_command(self, command):
        print(f"[MQTTDevice - {self.deviceId}] Command received: {command} on {self.CMD_TOPIC}")

    def __handle_update(self, update):
        print(f"[MQTTDevice - {self.deviceId}] Update received: {update} on {self.UPDATE_TOPIC}")
