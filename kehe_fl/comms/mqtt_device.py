import asyncio

from kehe_fl.comms.enum.mqtt_cmd_enum import MQTTCmdEnum
from kehe_fl.comms.enum.mqtt_status_enum import MQTTStatusEnum
from kehe_fl.comms.mqtt_provider import MQTTProvider
from kehe_fl.utils.common.project_constants import ProjectConstants
from kehe_fl.utils.service.data_collection_service import DataCollectionService
from kehe_fl.utils.service.model_service import ModelService
from kehe_fl.utils.service.monitoring_service import MonitoringService


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

        if topic == ProjectConstants.DATA_TOPIC:
            await self.check_for_update(payload)
            return

        if topic == ProjectConstants.FL_ROUND_HANDLE:
            if self._roundCounter == 0:
                self._monitoringService = MonitoringService()
                self._monitoringTask = asyncio.create_task(asyncio.to_thread(self._monitoringService.start))
            self._roundCounter += 1
            await self.handle_fl_round(payload)
            if self._roundCounter == ProjectConstants.FL_GLOBAL_EPOCHS:
                self._monitoringService.stop()
                self._monitoringService = None
                await self._monitoringTask
                self._monitoringTask = None
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
            await self.start_training()
        elif payload == MQTTCmdEnum.CHECK_TRAINING_STATUS.value:
            await self.check_training_status()
        elif payload == MQTTCmdEnum.SEND_UPDATE.value:
            await self.send_update()
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
        if self.__isDataCollecting():
            print(f"[MQTTDevice - {self.deviceId}] Data collection running, stopping it first")
            await self._stop_data_collection()

        if not self.__isTraining():
            self._modelService = ModelService()
            self._modelTask = asyncio.create_task(asyncio.to_thread(self._modelService.start_training,
                                                                    data_path=ProjectConstants.DATA_DIRECTORY))
            print(f"[MQTTDevice - {self.deviceId}] Training started")
            await self.send_data(MQTTStatusEnum.STARTED_TRAINING.value)
        else:
            print(f"[MQTTDevice - {self.deviceId}] Training already running")
            await self.send_data(MQTTStatusEnum.STARTED_TRAINING.value)

    async def check_training_status(self):
        if self.__isDataCollecting():
            print(f"[MQTTDevice - {self.deviceId}] Data collection running, cannot check training status")
            await self.send_data(MQTTStatusEnum.DATA_COLLECTION_IN_PROCESS.value)
            return

        if self.__isTraining():
            await self.send_data(self._modelService.check_training_status())
        else:
            print(f"[MQTTDevice - {self.deviceId}] Training not running")
            await self.send_data(MQTTStatusEnum.TRAINING_NOT_RUNNING.value)
        return

    async def send_update(self):
        if self.__isTraining():
            print(f"[MQTTDevice - {self.deviceId}] Training in process, cannot send update")
            await self.send_data(MQTTStatusEnum.TRAINING_IN_PROCESS.value)
            return

        if self.__isDataCollecting():
            print(f"[MQTTDevice - {self.deviceId}] Data collection in process, cannot send update")
            await self.send_data(MQTTStatusEnum.DATA_COLLECTION_IN_PROCESS.value)
            return

        data = self._modelService.get_weights()
        await self.send_data(data)
        return

    async def check_for_update(self, update):
        if self.__isTraining():
            print(f"[MQTTDevice - {self.deviceId}] Training in process, cannot check for update")
            await self.send_data(MQTTStatusEnum.TRAINING_IN_PROCESS.value)
            return

        if self.__isDataCollecting():
            print(f"[MQTTDevice - {self.deviceId}] Data collection running, cannot check for update")
            await self.send_data(MQTTStatusEnum.DATA_COLLECTION_IN_PROCESS.value)

        if update:
            self._modelService.set_weights(update)
        else:
            print(f"[MQTTDevice - {self.deviceId}] No updates available")
            await self.send_data("No updates available")
        return

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

    async def handle_fl_round(self, _weights):
        if self.__isTraining():
            print(f"[MQTTDevice - {self.deviceId}] Training in process, cannot handle FL round")
            return

        if self.__isDataCollecting():
            print(f"[MQTTDevice - {self.deviceId}] Data collection running, cannot handle FL round")
            return

        if not self._modelService:
            self._modelService = ModelService()

        if _weights:
            self._modelService.set_weights(MQTTProvider._unpack_weights(_weights))

        if self._roundCounter <= ProjectConstants.FL_GLOBAL_EPOCHS:
            self._modelService.start_training(data_path=ProjectConstants.DATA_DIRECTORY)
            weights = self._modelService.get_weights()
            await self._send_weights(self.flRoundClientTopic, weights)
