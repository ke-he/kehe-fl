from aiomqtt import Message

from kehe_fl.comms.mqtt_provider import MQTTProvider
from kehe_fl.comms.enum.mqtt_status_enum import MQTTStatusEnum
from kehe_fl.utils.common.project_constants import ProjectConstants


class MQTTAggServer(MQTTProvider):
    LISTEN_TOPIC = f"{ProjectConstants.FEEDBACK_TOPIC}+"
    LOGIN_TOPIC = r"sys/login/+"
    clientIds = set()
    lastCommand = None
    working = False

    def __init__(self, broker, port=1883, username=None, password=None):
        super().__init__(broker, port, username, password)
        self.topics = [self.LISTEN_TOPIC, self.LOGIN_TOPIC]

    async def subscribe_topics(self):
        for topic in self.topics:
            await self.subscribe(topic)
            print(f"[MQTTAggServer] Subscribed to {topic}")

    async def on_message(self, topic: str, payload: str):
        if topic.startswith(ProjectConstants.FEEDBACK_TOPIC[:-1]):
            deviceId = MQTTAggServer.__get_device_id_from_topic(topic)
            await self.__handle_data(deviceId, payload)
        elif topic.startswith("sys/login"):
            deviceId = MQTTAggServer.__get_device_id_from_topic(topic)
            await self.__handle_login(deviceId)
        else:
            print(f"[MQTTAggServer] Received unknown topic {topic}: {payload}")

    async def send_update(self, update):
        topic = "sys/update"
        print(f"[MQTTAggServer] Sending update to {topic}: {update}")
        await self.publish(topic, update)

    async def send_command(self, command):
        topic = f"sys/cmd/"
        print(f"[MQTTAggServer] Sending command to {topic}: {command}")
        self.lastCommand = command
        self.working = True
        await self.publish(topic, command)

    async def __handle_login(self, deviceId):
        if deviceId not in self.clientIds:
            self.clientIds.add(deviceId)
            print(f"[MQTTAggServer] Device {deviceId} logged in")
        else:
            await self.send_command(deviceId, f"{MQTTStatusEnum.DUPLICATE_CLIENT_ID}")
            print(f"[MQTTAggServer] Device {deviceId} already logged in")

    async def __handle_data(self, deviceId, data):
        print(f"[MQTTAggServer] Data received from {deviceId}: {data} | action: {self.lastCommand}")
        self.working = False

    @staticmethod
    def __get_device_id_from_topic(topic):
        return topic.split("/")[-1]
