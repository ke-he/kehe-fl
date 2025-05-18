from enum import Enum


class MQTTStatusEnum(Enum):
    REGISTRATION_SUCCESSFUL = 's:r:s'
    REGISTRATION_NOT_SUCCESSFUL = 's:r:n:s'
    DATA_COLLECTION_ALREADY_RUNNING = 's:d:c:a:r'
    DATA_COLLECTION_STARTED = 's:d:c:s'
    DATA_COLLECTION_IN_PROCESS = 's:d:c:i:p'
    DATA_COLLECTION_NOT_RUNNING = 's:d:c:n:r'
    DATA_COLLECTION_STOPPED = 's:d:c:s:t'
    STARTED_TRAINING = 's:s:t'
    TRAINING_ALREADY_STARTED = 's:t:a:s'
    TRAINING_NOT_RUNNING = 's:t:n:r'
    TRAINING_IN_PROCESS = 's:t:i:p'
    UNKNOWN_CMD = 's:u:c'

    @staticmethod
    def get_status_message(code):
        status_messages = {
            MQTTStatusEnum.REGISTRATION_SUCCESSFUL.value: "Connected successfully.",
            MQTTStatusEnum.DATA_COLLECTION_ALREADY_RUNNING.value: "Data collection is already running.",
            MQTTStatusEnum.DATA_COLLECTION_STARTED.value: "Data collection has started.",
            MQTTStatusEnum.DATA_COLLECTION_IN_PROCESS.value: "Data collection is in process.",
            MQTTStatusEnum.DATA_COLLECTION_NOT_RUNNING.value: "Data collection is not running.",
            MQTTStatusEnum.DATA_COLLECTION_STOPPED.value: "Data collection has stopped.",
            MQTTStatusEnum.REGISTRATION_NOT_SUCCESSFUL.value: "Registration failed.",
            MQTTStatusEnum.STARTED_TRAINING.value: "Training has started.",
            MQTTStatusEnum.TRAINING_ALREADY_STARTED.value: "Training is already in progress.",
            MQTTStatusEnum.TRAINING_NOT_RUNNING.value: "Training is not running.",
            MQTTStatusEnum.TRAINING_IN_PROCESS.value: "Training is in process.",
            MQTTStatusEnum.UNKNOWN_CMD.value: "Unknown command.",
        }
        return status_messages.get(code, "Unknown status code.")