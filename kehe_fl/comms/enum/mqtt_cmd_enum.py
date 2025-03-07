from enum import Enum


class MQTTCmdEnum(Enum):
    START_DATA_COLLECTION = 0
    CHECK_DATA_COUNT = 1
    SEND_DATA = 2
    START_TRAINING = 3
    CHECK_TRAINING_STATUS = 4
    SEND_UPDATE = 5
    CHECK_FOR_UPDATES = 6

    @staticmethod
    def get_command_message(code):
        command_messages = {
            MQTTCmdEnum.START_DATA_COLLECTION: "Advised edge devices to start data collection.",
            MQTTCmdEnum.CHECK_DATA_COUNT: "Requested edge devices to share data count.",
            MQTTCmdEnum.SEND_DATA: "Requested edge devices to send data.",
            MQTTCmdEnum.START_TRAINING: "Advised edge devices to start training.",
            MQTTCmdEnum.CHECK_TRAINING_STATUS: "Requested edge devices to share training status.",
            MQTTCmdEnum.SEND_UPDATE: "Requested edge devices to send update.",
            MQTTCmdEnum.CHECK_FOR_UPDATES: "Requested edge devices to check for updates.",
        }
        return command_messages.get(code, "Unknown command code.")
