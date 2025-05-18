from enum import Enum


class MQTTCmdEnum(Enum):
    START_DATA_COLLECTION = 0
    CHECK_DATA_COUNT = 1
    START_TRAINING = 2
    CHECK_TRAINING_STATUS = 3
    SEND_UPDATE = 4
    REGISTER_DEVICE = 5
    STOP_DATA_COLLECTION = 6

    @staticmethod
    def get_command_message(code):
        command_messages = {
            MQTTCmdEnum.START_DATA_COLLECTION: "Advised edge devices to start data collection.",
            MQTTCmdEnum.CHECK_DATA_COUNT: "Requested edge devices to share data count.",
            MQTTCmdEnum.START_TRAINING: "Advised edge devices to start training.",
            MQTTCmdEnum.CHECK_TRAINING_STATUS: "Requested edge devices to share training status.",
            MQTTCmdEnum.SEND_UPDATE: "Requested edge devices to send update.",
            MQTTCmdEnum.REGISTER_DEVICE: "Advised edge devices to register.",
        }
        return command_messages.get(code, "Unknown command code.")
