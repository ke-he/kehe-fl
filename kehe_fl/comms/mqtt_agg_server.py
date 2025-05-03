from kehe_fl.comms.enum.mqtt_cmd_enum import MQTTCmdEnum
from kehe_fl.comms.mqtt_provider import MQTTProvider
from kehe_fl.comms.enum.mqtt_status_enum import MQTTStatusEnum
from kehe_fl.utils.common.project_constants import ProjectConstants


class MQTTAggServer(MQTTProvider):
    LISTEN_TOPIC = f"{ProjectConstants.FEEDBACK_TOPIC}+"
    clientIds = set()
    lastCommand = None
    working = False

    def __init__(self, broker, port=1883, username=None, password=None):
        super().__init__(broker, port, username, password)
        self.topics = [self.LISTEN_TOPIC]

    async def subscribe_topics(self):
        for topic in self.topics:
            await self.subscribe(topic)
            print(f"[MQTTAggServer] Subscribed to {topic}")

    async def on_message(self, topic: str, payload: str):
        if topic.startswith(ProjectConstants.FEEDBACK_TOPIC[:-1]):
            deviceId = MQTTAggServer.__get_device_id_from_topic(topic)
            await self.__handle_data(deviceId, payload)
        else:
            print(f"[MQTTAggServer] Received unknown topic {topic}: {payload}")

    async def send_update(self, update):
        topic = "sys/update"
        print(f"[MQTTAggServer] Sending update to {topic}: {update}")
        await self.publish(topic, update)

    async def send_command(self, command):
        print(f"[MQTTAggServer] Sending command to {ProjectConstants.CMD_TOPIC}: {command}")
        self.lastCommand = command
        self.working = True
        await self.publish(ProjectConstants.CMD_TOPIC, command)

    async def __handle_data(self, deviceId, data):
        if self.lastCommand == MQTTCmdEnum.REGISTER_DEVICE:
            if data == MQTTStatusEnum.SUCCESS.value:
                self.__handle_register(deviceId)
        self.working = False

    def __handle_register(self, deviceId):
        if deviceId not in self.clientIds:
            self.clientIds.add(deviceId)
            print(f"[MQTTAggServer] Device {deviceId} registered")
        return

    @staticmethod
    def __get_device_id_from_topic(topic):
        return topic.split("/")[-1]
