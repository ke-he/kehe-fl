from kehe_fl.comms.mqtt_provider import MQTTProvider


class MQTTDevice(MQTTProvider):
    UPDATE_TOPIC = "sys/update"
    CMD_TOPIC = "sys/cmd/"

    def __init__(self, broker, deviceId, port=1883, username=None, password=None):
        super().__init__(broker, port, username, password)
        self.deviceId = deviceId
        self.clientTopic = f"sys/data/{deviceId}"
        self.loginTopic = f"sys/login/{deviceId}"
        self.CMD_TOPIC += f"{self.deviceId}"
        self.serverTopics = [self.UPDATE_TOPIC, self.CMD_TOPIC]

    async def subscribe_topics(self):
        for topic in self.serverTopics:
            await self.subscribe(topic)

    async def on_message(self, message):
        print(f"[MQTTDevice - {self.deviceId}] Received message: {message.payload.decode()} on topic {message.topic}")
        topic = message.topic
        payload = message.payload.decode()

        if topic == self.CMD_TOPIC:
            print(f"[MQTTDevice - {self.deviceId}] Command received: {payload}")
        elif topic == self.UPDATE_TOPIC:
            print(f"[MQTTDevice - {self.deviceId}] Update received: {payload}")
        else:
            print(f"[MQTTDevice - {self.deviceId}] Unknown topic {topic}: {payload}")

    async def send_data(self, data):
        await self.publish(self.clientTopic, data)
