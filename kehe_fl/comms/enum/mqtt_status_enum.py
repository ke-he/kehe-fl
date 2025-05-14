from enum import Enum


class MQTTStatusEnum(Enum):
    REGISTRATION_SUCCESSFUL = 's:r:s'
    REGISTRATION_NOT_SUCCESSFUL = 's:r:n:s'
    DATA_COLLECTION_ALREADY_RUNNING = 's:d:c:a:r'
    DATA_COLLECTION_STARTED = 's:d:c:s'
    UNKNOWN_CMD = 's:u:c'

    @staticmethod
    def get_status_message(code):
        status_messages = {
            MQTTStatusEnum.REGISTRATION_SUCCESSFUL.value: "Connected successfully.",
            MQTTStatusEnum.DATA_COLLECTION_ALREADY_RUNNING.value: "Data collection is already running.",
            MQTTStatusEnum.DATA_COLLECTION_STARTED.value: "Data collection has started.",
            MQTTStatusEnum.REGISTRATION_NOT_SUCCESSFUL.value: "Registration failed.",
            MQTTStatusEnum.UNKNOWN_CMD.value: "Unknown command.",
        }
        return status_messages.get(code, "Unknown status code.")