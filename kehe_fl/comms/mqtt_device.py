import asyncio

from kehe_fl.comms.enum.mqtt_cmd_enum import MQTTCmdEnum
from kehe_fl.comms.enum.mqtt_status_enum import MQTTStatusEnum
from kehe_fl.comms.mqtt_provider import MQTTProvider
from kehe_fl.utils.common.project_constants import ProjectConstants
from kehe_fl.utils.service.data_collection_service import DataCollectionService
from kehe_fl.utils.service.model_service import ModelService


class MQTTDevice(MQTTProvider):
    def __init__(self, broker, deviceId, port=1883, username=None, password=None):
        super().__init__(broker, port, username, password)
        self.deviceId = deviceId
        self.clientTopic = f"{ProjectConstants.FEEDBACK_TOPIC}{deviceId}"
        self.loginTopic = f"{ProjectConstants.LOGIN_TOPIC}{deviceId}"
        self.serverTopics = [ProjectConstants.CMD_TOPIC]
        self._dataCollectionTask = None
        self._dataCollectionService = None
        self._modelTask = None
        self._modelService = None

    async def subscribe_topics(self):
        for topic in self.serverTopics:
            await self.subscribe(topic)

    async def on_message(self, topic: str, payload: int):
        print(f"[MQTTDevice - {self.deviceId}] Received message: {payload} on topic {topic}")

        print(payload)

        if topic != ProjectConstants.CMD_TOPIC:
            print(f"[MQTTDevice - {self.deviceId}] Unknown topic {topic}: {payload}")
            return

        await self.handle_cmd(payload)

    async def send_data(self, data):
        await self.publish(self.clientTopic, data)

    async def handle_cmd(self, payload):
        if payload == MQTTCmdEnum.START_DATA_COLLECTION.value:
            await self.start_data_collection()
        elif payload == MQTTCmdEnum.CHECK_DATA_COUNT.value:
            await self.check_data_count()
        elif payload == MQTTCmdEnum.START_TRAINING.value:
            await self.start_training()
        elif payload == MQTTCmdEnum.CHECK_TRAINING_STATUS.value:
            await self.check_training_status()
        elif payload == MQTTCmdEnum.SEND_UPDATE.value:
            await self.send_update()
        elif payload == MQTTCmdEnum.CHECK_FOR_UPDATES.value:
            await self.check_for_update()
        elif payload == MQTTCmdEnum.REGISTER_DEVICE.value:
            await self.send_data(MQTTStatusEnum.SUCCESS.value)
        else:
            print("Command not found")

    async def start_data_collection(self):
        if not self._dataCollectionTask or self._dataCollectionTask.done():
            self._dataCollectionService = DataCollectionService(fields=ProjectConstants.CSV_FIELDS,
                                                                path=ProjectConstants.DATA_DIRECTORY,
                                                                interval=ProjectConstants.COLLECTION_INTERVAL)
            self._dataCollectionTask = asyncio.create_task(asyncio.to_thread(self._dataCollectionService.start))
            print(f"[MQTTDevice - {self.deviceId}] Data collection started")
            await self.send_data("Data collection started")
        else:
            print(f"[MQTTDevice - {self.deviceId}] Data collection already running")
            await self.send_data("Data collection already running")
        return

    async def check_data_count(self):
        if self._dataCollectionService and self._dataCollectionTask and not self._dataCollectionTask.done():
            count = self._dataCollectionService.check_data_count()
            await self.send_data(count)
        else:
            print(f"[MQTTDevice - {self.deviceId}] Data collection not running")
            await self.send_data("Data collection not running")
        return

    async def start_training(self):
        if self._dataCollectionService and self._dataCollectionTask and not self._dataCollectionTask.done():
            print(f"[MQTTDevice - {self.deviceId}] Data collection running, stopping it first")
            await self._stop_data_collection()

        if not self._modelTask or self._modelTask.done():
            self._modelService = ModelService()
            self._modelTask = asyncio.create_task(asyncio.to_thread(self._modelService.start_training,
                                                                    data_path=ProjectConstants.DATA_DIRECTORY))
            print(f"[MQTTDevice - {self.deviceId}] Training started")
            await self.send_data("Training started")
        return

    async def check_training_status(self):
        if self._modelTask and not self._modelTask.done():
            iterationCount, weights = self._modelService.check_training_status()
            await self.send_data(f"Iteration count: {iterationCount}, Weights: {weights}")
        else:
            print(f"[MQTTDevice - {self.deviceId}] Training not running")
            await self.send_data("Training not running")
        return

    async def send_update(self):
        data = self._modelService.get_weights()
        await self.send_data(data)
        return

    async def check_for_update(self):
        print("check for update")
        return

    async def _stop_data_collection(self):
        if self._dataCollectionService and self._dataCollectionTask:
            self._dataCollectionService.stop()
            await self._dataCollectionTask
            self._dataCollectionService = None
            print("[MQTTDevice - {self.deviceId}] Data collection stopped")
        else:
            print("[MQTTDevice - {self.deviceId}] Data collection not running")
        return
