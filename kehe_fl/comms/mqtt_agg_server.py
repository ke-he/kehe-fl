import asyncio

from kehe_fl.comms.enum.mqtt_cmd_enum import MQTTCmdEnum
from kehe_fl.comms.mqtt_provider import MQTTProvider
from kehe_fl.comms.enum.mqtt_status_enum import MQTTStatusEnum
from kehe_fl.utils.common.project_constants import ProjectConstants
from kehe_fl.utils.service.model_service import ModelService
from kehe_fl.utils.service.monitoring_service import MonitoringService


class MQTTAggServer(MQTTProvider):
    LISTEN_TOPIC = f"{ProjectConstants.FEEDBACK_TOPIC}+"
    FL_ROUND_FEEDBACK_TOPIC = f"{ProjectConstants.FL_ROUND_TOPIC}+"
    clientIds = set()
    commandClientIds = set()
    lastCommand = None
    working = False
    messageQueue = []
    deviceErrorOccurred = False
    weightsArray = []
    newWeights = None

    def __init__(self, broker, port=1883, username=None, password=None):
        super().__init__(broker, port, username, password)
        self.topics = [self.LISTEN_TOPIC, self.FL_ROUND_FEEDBACK_TOPIC]
        self.modelService = ModelService(agg=True)
        self._monitoringService = None
        self._monitoringTask = None
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

            self.__after_queue_job_done()

    async def on_message(self, topic: str, payload: str):
        if topic.startswith(ProjectConstants.FL_ROUND_TOPIC[:-1]):
            deviceId = self.__get_device_id_from_topic(topic)
            if deviceId not in self.clientIds:
                return
            if not (payload == "" or payload is None):
                self.weightsArray.append(MQTTProvider._unpack_weights(payload))
                print(f"[MQTTAggServer] Received FL round update from {deviceId}")
            else:
                self.deviceErrorOccurred = True
                print(f"[MQTTAggServer] Received empty FL round update from {deviceId}")
        elif topic.startswith(ProjectConstants.FEEDBACK_TOPIC[:-1]):
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

        self.lastCommand = numCommand
        self.working = True
        if self.lastCommand == MQTTCmdEnum.FL_ROUND.value:
            self._monitoringService = MonitoringService()
            self._monitoringTask = asyncio.create_task(asyncio.to_thread(self._monitoringService.start))
            await self.start_federated_training()
            self._monitoringService.stop()
            await self._monitoringTask
            self._monitoringService = None
            self._monitoringTask = None
            self.working = False
            return

        print(f"[MQTTAggServer] Sending command to {ProjectConstants.CMD_TOPIC}: {command}")
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
            MQTTAggServer.__printStatus(deviceId, data)
        elif self.lastCommand == MQTTCmdEnum.CHECK_DATA_COUNT.value:
            if data.isnumeric():
                print(f"[MQTTAggServer] Device {deviceId}: Data count {data}")
            else:
                MQTTAggServer.__printStatus(deviceId, data)
        elif self.lastCommand == MQTTCmdEnum.STOP_DATA_COLLECTION.value:
            MQTTAggServer.__printStatus(deviceId, data)
        elif self.lastCommand == MQTTCmdEnum.START_TRAINING.value:
            MQTTAggServer.__printStatus(deviceId, data)
        elif self.lastCommand == MQTTCmdEnum.CHECK_TRAINING_STATUS.value:
            iterationCount, weights = ModelService.unpack_training_status(data)
            if iterationCount is not None and weights is not None:
                print(
                    f"[MQTTAggServer] Device {deviceId}: Training status - Iteration count: {iterationCount}, Weights: {weights}")
            else:
                MQTTAggServer.__printStatus(deviceId, data)
        elif self.lastCommand == MQTTCmdEnum.SEND_UPDATE.value:
            if data.isnumeric():
                print(f"[MQTTAggServer] Device {deviceId}: Update count {data}")
                self.weightsArray.append(data)
            else:
                MQTTAggServer.__printStatus(deviceId, data)

    def __handle_register(self, deviceId):
        if deviceId not in self.clientIds:
            self.clientIds.add(deviceId)
        return

    def __after_queue_job_done(self):
        if self.deviceErrorOccurred:
            self.__handle_clear_worker()
        elif self.lastCommand == MQTTCmdEnum.REGISTER_DEVICE.value and ProjectConstants.CLIENT_DEVICES == len(
                self.clientIds):
            print(f"[MQTTAggServer] All devices registered: {self.clientIds}")
            self.__handle_clear_worker()
        elif self.lastCommand == MQTTCmdEnum.SEND_UPDATE.value and len(
                self.weightsArray) == ProjectConstants.CLIENT_DEVICES:
            print(f"[MQTTAggServer] All devices have sent updates: {self.weightsArray}")
            self.__handle_model_aggregation()
            self.__handle_clear_worker()
        elif self.lastCommand != MQTTCmdEnum.REGISTER_DEVICE.value and len(self.commandClientIds) == len(
                self.clientIds):
            print(f"[MQTTAggServer] All devices have responded to command {self.lastCommand}")
            self.__handle_clear_worker()

    def __handle_clear_worker(self):
        self.deviceErrorOccurred = False
        self.commandClientIds.clear()
        self.lastCommand = None
        self.working = False

    def __handle_model_aggregation(self):
        self.newWeights = self.modelService.aggregate_weights(weights=self.weightsArray)
        self.weightsArray.clear()
        self.modelService.set_weights(self.newWeights)

    async def start_federated_training(self):
        for round_num in range(ProjectConstants.FL_GLOBAL_EPOCHS):
            print(f"[MQTTAggServer] Starting round {round_num + 1}/{ProjectConstants.FL_GLOBAL_EPOCHS}")

            await self.send_fl_round(self.newWeights)

            self.weightsArray.clear()
            self.commandClientIds.clear()

            while len(self.weightsArray) < ProjectConstants.CLIENT_DEVICES:
                if self.deviceErrorOccurred:
                    self.deviceErrorOccurred = False
                    return
                await asyncio.sleep(0.5)  # polling, not elegant but simple

            print(f"[MQTTAggServer] Aggregating weights for round {round_num + 1}")
            self.__handle_model_aggregation()

            if round_num == ProjectConstants.FL_GLOBAL_EPOCHS - 1:
                print("[MQTTAggServer] Finalizing FL round, sending aggregated weights to clients.")
                await self.send_fl_round(self.modelService.get_weights())
            else:
                print(f"[MQTTAggServer] Round {round_num + 1} complete, waiting for next round.")
                self.modelService.set_weights(None)

        print("[MQTTAggServer] Federated training complete.")

    async def send_fl_round(self, weights=None):
        topic = ProjectConstants.FL_ROUND_HANDLE
        print(f"[MQTTAggServer] Starting FL round, sending weights: {weights}")
        await self._send_weights(topic, weights)

    @staticmethod
    def __get_device_id_from_topic(topic):
        return topic.split("/")[-1]

    @staticmethod
    def __printStatus(deviceId, data):
        print(f"[MQTTAggServer] Device {deviceId}: {MQTTStatusEnum.get_status_message(data)}")
