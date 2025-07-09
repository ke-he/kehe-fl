from enum import Enum


class MQTTCmdEnum(Enum):
    START_DATA_COLLECTION = 0
    CHECK_DATA_COUNT = 1
    REGISTER_DEVICE = 2
    STOP_DATA_COLLECTION = 3
    START_TRAINING = 4

    @staticmethod
    def get_command_message(code):
        command_messages = {
            MQTTCmdEnum.START_DATA_COLLECTION.value: "Advised edge devices to start data collection.",
            MQTTCmdEnum.CHECK_DATA_COUNT.value: "Requested edge devices to share data count.",
            MQTTCmdEnum.REGISTER_DEVICE.value: "Advised edge devices to register.",
            MQTTCmdEnum.STOP_DATA_COLLECTION.value: "Advised edge devices to stop data collection.",
        }
        return command_messages.get(code, "Unknown command code.")
