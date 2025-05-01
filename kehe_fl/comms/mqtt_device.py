import asyncio

from kehe_fl.comms.enum.mqtt_cmd_enum import MQTTCmdEnum
from kehe_fl.comms.mqtt_provider import MQTTProvider
from kehe_fl.utils.common.project_constants import ProjectConstants
from kehe_fl.utils.service.data_collection_service import DataCollectionService


class MQTTDevice(MQTTProvider):
    CMD_TOPIC = "sys/cmd/"

    def __init__(self, broker, deviceId, port=1883, username=None, password=None):
        super().__init__(broker, port, username, password)
        self.deviceId = deviceId
        self.clientTopic = f"sys/data/{deviceId}"
        self.loginTopic = f"sys/login/{deviceId}"
        self.serverTopics = [self.CMD_TOPIC]
        self._dataCollectionTask = None
        self._dataCollectionService = None

    async def subscribe_topics(self):
        for topic in self.serverTopics:
            await self.subscribe(topic)

    async def on_message(self, topic: str, payload: int):
        print(f"[MQTTDevice - {self.deviceId}] Received message: {payload} on topic {topic}")

        print(payload)

        if topic != self.CMD_TOPIC:
            print(f"[MQTTDevice - {self.deviceId}] Unknown topic {topic}: {payload}")
            return

        await self.handle_cmd(payload)

    async def send_data(self, data):
        await self.publish(self.clientTopic, data)

    async def handle_cmd(self, payload):
        if payload == MQTTCmdEnum.START_DATA_COLLECTION.value:
            self.start_data_collection()
        elif payload == MQTTCmdEnum.CHECK_DATA_COUNT.value:
            self.check_data_count()
        elif payload == MQTTCmdEnum.START_TRAINING.value:
            await self.start_training()
        elif payload == MQTTCmdEnum.CHECK_TRAINING_STATUS.value:
            await self.check_training_status()
        elif payload == MQTTCmdEnum.SEND_UPDATE.value:
            await self.send_update()
        elif payload == MQTTCmdEnum.CHECK_FOR_UPDATES.value:
            await self.check_for_update()
        else:
            print("Command not found")

    def start_data_collection(self):
        if not self._dataCollectionTask or self._dataCollectionTask.done():
            self._dataCollectionService = DataCollectionService(fields=ProjectConstants.CSV_FIELDS,
                                                                path=ProjectConstants.DATA_DIRECTORY,
                                                                interval=ProjectConstants.COLLECTION_INTERVAL)
            self._dataCollectionTask = asyncio.create_task(asyncio.to_thread(self._dataCollectionService.start))
            print(f"[MQTTDevice - {self.deviceId}] Data collection started")
        else:
            print(f"[MQTTDevice - {self.deviceId}] Data collection already running")
        return

    def check_data_count(self):
        if self._dataCollectionService and self._dataCollectionTask and not self._dataCollectionTask.done():
            count = self._dataCollectionService.check_data_count()
            print(f"[MQTTDevice - {self.deviceId}] Data count: {count}")
        else:
            print("[MQTTDevice - {self.deviceId}] Data collection not running")
        return

    async def start_training(self):
        await self._stop_data_collection()
        print("started training")
        return

    async def check_training_status(self):
        print("check training status")
        return

    async def send_update(self):
        print("send update")
        return

    async def check_for_update(self):
        print("check for update")
        return

    def __get_cmd(self, payload):
        return payload[2:]

    async def _stop_data_collection(self):
        if self._dataCollectionService and self._dataCollectionTask:
            self._dataCollectionService.stop()
            await self._dataCollectionTask
            self._dataCollectionService = None
            print("[MQTTDevice - {self.deviceId}] Data collection stopped")
        else:
            print("[MQTTDevice - {self.deviceId}] Data collection not running")
        return
