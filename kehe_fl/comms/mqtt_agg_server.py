from mqtt_provider import MQTTProvider
from kehe_fl.comms.enum.mqtt_status_enum import MQTTStatusEnum

class MQTTAggServer(MQTTProvider):
    LISTEN_TOPIC = "sys/+/data"
    LOGIN_TOPIC = "sys/+/login"
    clientIds = []

    def __init__(self, broker, port=1883, username=None, password=None, tls_config=None):
        super().__init__(broker, port, username, password, tls_config)
        self.topics = [self.LISTEN_TOPIC, self.LOGIN_TOPIC]

    def on_connect(self, client, userdata, flags, rc):
        super().on_connect(client, userdata, flags, rc)
        for topic in self.topics:
            self.client.subscribe(topic)
            print(f"[MQTTAggServer] Subscribed to {topic}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        if topic == self.LISTEN_TOPIC:
            deviceId = topic.split("/")[1]
            self.__handle_data(deviceId, msg.payload.decode())
        elif topic == self.LOGIN_TOPIC:
            deviceId = topic.split("/")[1]
            self.__handle_login(deviceId)
        else:
            print(f"[MQTTAggServer] Received unknown topic {msg.topic}: {msg.payload.decode()}")

    def send_update(self, update):
        topic = f"sys/update"
        print(f"[MQTTAggServer] Sending update to {topic}: {update}")
        self.publish(topic, update)

    def send_command(self, deviceId, command):
        topic = f"sys/{deviceId}/cmd"
        print(f"[MQTTAggServer] Sending command to {topic}: {command}")
        self.publish(topic, command)

    def __handle_login(self, deviceId):
        if deviceId not in self.clientIds:
            self.clientIds.append(deviceId)
            print(f"[MQTTAggServer] Device {deviceId} logged in")
        else:
            self.send_command(deviceId, f"{MQTTStatusEnum.SUCCESS}")
            print(f"[MQTTAggServer] Device {deviceId} already logged in")

    def __handle_data(self, deviceId, data):
        if deviceId in self.clientIds:
            print(f"[MQTTAggServer] Data received from {deviceId}: {data}")
        else:
            self.send_command(deviceId, f"{MQTTStatusEnum.IDENTIFIER_REJECTED}")
            print(f"[MQTTAggServer] Unauthorized device {deviceId}")
