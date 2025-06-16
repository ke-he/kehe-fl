from enum import Enum


class MQTTCmdEnum(Enum):
    START_DATA_COLLECTION = 0
    CHECK_DATA_COUNT = 1
    START_TRAINING = 2
    CHECK_TRAINING_STATUS = 3
    SEND_UPDATE = 4
    REGISTER_DEVICE = 5
    STOP_DATA_COLLECTION = 6
    FL_ROUND = 7

    @staticmethod
    def get_command_message(code):
        command_messages = {
            MQTTCmdEnum.START_DATA_COLLECTION.value: "Advised edge devices to start data collection.",
            MQTTCmdEnum.CHECK_DATA_COUNT.value: "Requested edge devices to share data count.",
            MQTTCmdEnum.START_TRAINING.value: "Advised edge devices to start training.",
            MQTTCmdEnum.CHECK_TRAINING_STATUS.value: "Requested edge devices to share training status.",
            MQTTCmdEnum.SEND_UPDATE.value: "Requested edge devices to send update.",
            MQTTCmdEnum.REGISTER_DEVICE.value: "Advised edge devices to register.",
            MQTTCmdEnum.STOP_DATA_COLLECTION.value: "Advised edge devices to stop data collection.",
            MQTTCmdEnum.FL_ROUND.value: "Advised edge devices to start federated learning round.",
        }
        return command_messages.get(code, "Unknown command code.")
