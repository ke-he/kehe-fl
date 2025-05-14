import asyncio

from kehe_fl.comms.enum.mqtt_cmd_enum import MQTTCmdEnum
from kehe_fl.comms.mqtt_provider import MQTTProvider
from kehe_fl.comms.enum.mqtt_status_enum import MQTTStatusEnum
from kehe_fl.utils.common.project_constants import ProjectConstants


class MQTTAggServer(MQTTProvider):
    LISTEN_TOPIC = f"{ProjectConstants.FEEDBACK_TOPIC}+"
    clientIds = set()
    commandClientIds = set()
    lastCommand = None
    working = False
    messageQueue = []
    deviceErrorOccurred = False

    def __init__(self, broker, port=1883, username=None, password=None):
        super().__init__(broker, port, username, password)
        self.topics = [self.LISTEN_TOPIC]
        self._in_queue = asyncio.Queue()
        asyncio.create_task(self._worker())

    async def subscribe_topics(self):
        for topic in self.topics:
            await self.subscribe(topic)
            print(f"[MQTTAggServer] Subscribed to {topic}")

    async def _worker(self):
        while True:
            deviceId, payload = await self._in_queue.get()
            try:
                await self.__handle_data(deviceId, payload)
            finally:
                self._in_queue.task_done()
                self.commandClientIds.add(deviceId)

            if self.deviceErrorOccurred:
                self.deviceErrorOccurred = False
                self.commandClientIds.clear()
                self.lastCommand = None
                self.working = False

            if self.lastCommand == MQTTCmdEnum.REGISTER_DEVICE.value and ProjectConstants.CLIENT_DEVICES == len(
                    self.clientIds):
                print(f"[MQTTAggServer] All devices registered: {self.clientIds}")
                self.commandClientIds.clear()
                self.lastCommand = None
                self.working = False

            if self.lastCommand != MQTTCmdEnum.REGISTER_DEVICE.value and len(self.commandClientIds) == len(
                    self.clientIds):
                self.commandClientIds.clear()
                print(f"[MQTTAggServer] All devices have responded to command {self.lastCommand}")
                self.lastCommand = None
                self.working = False

    async def on_message(self, topic: str, payload: str):
        if topic.startswith(ProjectConstants.FEEDBACK_TOPIC[:-1]):
            deviceId = MQTTAggServer.__get_device_id_from_topic(topic)
            await self._in_queue.put((deviceId, payload))
        else:
            print(f"[MQTTAggServer] Received unknown topic {topic}: {payload}")

    async def send_update(self, update):
        topic = "sys/update"
        print(f"[MQTTAggServer] Sending update to {topic}: {update}")
        await self.publish(topic, update)

    async def send_command(self, command):
        numCommand = int(command)
        if not any(numCommand == cmd.value for cmd in MQTTCmdEnum):
            print(f"[MQTTAggServer] Invalid command: {command}")
            return

        if numCommand != MQTTCmdEnum.REGISTER_DEVICE.value and len(self.clientIds) == 0:
            print(f"[MQTTAggServer] No devices registered. Cannot send command: {command}")
            return

        print(f"[MQTTAggServer] Sending command to {ProjectConstants.CMD_TOPIC}: {command}")
        self.lastCommand = numCommand
        self.working = True
        await self.publish(ProjectConstants.CMD_TOPIC, command)

    async def __handle_data(self, deviceId, data):
        if deviceId not in self.clientIds and self.lastCommand != MQTTCmdEnum.REGISTER_DEVICE.value:
            print(f"[MQTTAggServer] Device {deviceId} not registered.")
            self.deviceErrorOccurred = True
        elif data == MQTTStatusEnum.UNKNOWN_CMD.value:
            MQTTAggServer.__printStatus(deviceId, data)
            self.deviceErrorOccurred = True
        elif self.lastCommand == MQTTCmdEnum.REGISTER_DEVICE.value:
            if data == MQTTStatusEnum.REGISTRATION_SUCCESSFUL.value:
                self.__handle_register(deviceId)
                MQTTAggServer.__printStatus(deviceId, data)
            else:
                MQTTAggServer.__printStatus(deviceId, data)
        elif self.lastCommand == MQTTCmdEnum.START_DATA_COLLECTION.value:
            if data == MQTTStatusEnum.DATA_COLLECTION_STARTED.value:
                MQTTAggServer.__printStatus(deviceId, data)
            else:
                MQTTAggServer.__printStatus(deviceId, data)
        elif self.lastCommand == MQTTCmdEnum.CHECK_DATA_COUNT.value:
            if data.isnumeric():
                print(f"[MQTTAggServer] Device {deviceId}: Data count {data}")
            else:
                MQTTAggServer.__printStatus(deviceId, data)

    def __handle_register(self, deviceId):
        if deviceId not in self.clientIds:
            self.clientIds.add(deviceId)
        return

    @staticmethod
    def __get_device_id_from_topic(topic):
        return topic.split("/")[-1]

    @staticmethod
    def __printStatus(deviceId, data):
        print(f"[MQTTAggServer] Device {deviceId}: {MQTTStatusEnum.get_status_message(data)}")
