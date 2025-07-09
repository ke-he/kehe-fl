import asyncio

from kehe_fl_s3.comms.enum.mqtt_cmd_enum import MQTTCmdEnum
from kehe_fl_s3.comms.enum.mqtt_status_enum import MQTTStatusEnum
from kehe_fl_s3.comms.mqtt_provider import MQTTProvider
from kehe_fl_s3.utils.common.project_constants import ProjectConstants
from kehe_fl_s3.utils.service.data_collection_service import DataCollectionService
from kehe_fl_s3.utils.service.model_service import ModelService
from kehe_fl_s3.utils.service.monitoring_service import MonitoringService


class MQTTDevice(MQTTProvider):
    def __init__(self, broker, deviceId, port=1883, username=None, password=None):
        super().__init__(broker, port, username, password)
        self.deviceId = deviceId
        self.clientTopic = f"{ProjectConstants.FEEDBACK_TOPIC}{deviceId}"
        self.flRoundClientTopic = f"{ProjectConstants.FL_ROUND_TOPIC}{deviceId}"
        self.serverTopics = [ProjectConstants.CMD_TOPIC, ProjectConstants.DATA_TOPIC, ProjectConstants.FL_ROUND_HANDLE]
        self._dataCollectionTask = None
        self._dataCollectionService = None
        self._monitoringService = None
        self._monitoringTask = None
        self._modelTask = None
        self._modelService = None
        self._roundCounter = 0

    async def subscribe_topics(self):
        for topic in self.serverTopics:
            await self.subscribe(topic)

    async def on_message(self, topic: str, payload: int):
        print(f"[MQTTDevice - {self.deviceId}] Received message: {payload} on topic {topic}")

        if topic not in (ProjectConstants.CMD_TOPIC, ProjectConstants.DATA_TOPIC, ProjectConstants.FL_ROUND_HANDLE):
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
        elif payload == MQTTCmdEnum.STOP_DATA_COLLECTION.value:
            await self._stop_data_collection(withFeedback=True)
        elif payload == MQTTCmdEnum.START_TRAINING.value:
            self._monitoringService = MonitoringService()
            self._monitoringTask = asyncio.create_task(asyncio.to_thread(self._monitoringService.start))
            await self.start_training()
            await self._monitoringService.stop()
            await self._monitoringTask
            self._monitoringService = None
        elif payload == MQTTCmdEnum.REGISTER_DEVICE.value:
            await self.send_data(MQTTStatusEnum.REGISTRATION_SUCCESSFUL.value)
        else:
            print("Command not found")

    async def start_data_collection(self):
        if self.__isTraining():
            print(f"[MQTTDevice - {self.deviceId}] Training in process, cannot start data collection")
            await self.send_data(MQTTStatusEnum.TRAINING_IN_PROCESS.value)
            return

        if not self.__isDataCollecting():
            self._dataCollectionService = DataCollectionService(fields=ProjectConstants.CSV_FIELDS,
                                                                path=ProjectConstants.DATA_DIRECTORY,
                                                                interval=ProjectConstants.COLLECTION_INTERVAL)
            self._dataCollectionTask = asyncio.create_task(asyncio.to_thread(self._dataCollectionService.start))
            await self.send_data(MQTTStatusEnum.DATA_COLLECTION_STARTED.value)
        else:
            await self.send_data(MQTTStatusEnum.DATA_COLLECTION_ALREADY_RUNNING.value)
        return

    async def check_data_count(self):
        if self.__isTraining():
            print(f"[MQTTDevice - {self.deviceId}] Training in process, cannot check data count")
            await self.send_data(MQTTStatusEnum.TRAINING_IN_PROCESS.value)
            return

        if self.__isDataCollecting():
            count = self._dataCollectionService.check_data_count()
            await self.send_data(count)
        else:
            print(f"[MQTTDevice - {self.deviceId}] Data collection not running")
            await self.send_data(MQTTStatusEnum.DATA_COLLECTION_NOT_RUNNING.value)
        return

    async def start_training(self):
        if not self.__isTraining():
            self._modelService = ModelService()
            self._modelTask = asyncio.create_task(
                asyncio.to_thread(self._modelService.start_training, ProjectConstants.DATA_DIRECTORY))
            await self._modelTask

    def __isTraining(self):
        if self._modelTask and not self._modelTask.done():
            return True
        return False

    def __isDataCollecting(self):
        if self._dataCollectionTask and not self._dataCollectionTask.done():
            return True
        return False

    async def _stop_data_collection(self, withFeedback=False):
        if self.__isDataCollecting():
            self._dataCollectionService.stop()
            await self._dataCollectionTask
            self._dataCollectionService = None
            print(f"[MQTTDevice - {self.deviceId}] Data collection stopped")
            if withFeedback:
                await self.send_data(MQTTStatusEnum.DATA_COLLECTION_STOPPED.value)
        else:
            print(f"[MQTTDevice - {self.deviceId}] Data collection not running")
            if withFeedback:
                await self.send_data(MQTTStatusEnum.DATA_COLLECTION_NOT_RUNNING.value)
        return
