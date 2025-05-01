from enum import Enum


class MQTTStatusEnum(Enum):
    SUCCESS = 0  # Connection successful
    UNACCEPTABLE_PROTOCOL = 1  # Protocol version not supported
    IDENTIFIER_REJECTED = 2  # Client ID not allowed
    SERVER_UNAVAILABLE = 3  # MQTT broker unavailable
    BAD_USERNAME_OR_PASSWORD = 4  # Authentication failed
    NOT_AUTHORIZED = 5  # Not authorized to connect
    DUPLICATE_CLIENT_ID = 7  # Device already logged in (some brokers use this)
    CONNECTION_LOST = 8  # Connection lost unexpectedly
    TIMEOUT = 9  # Timeout while connecting

    @staticmethod
    def get_status_message(code):
        status_messages = {
            MQTTStatusEnum.SUCCESS: "Connected successfully.",
            MQTTStatusEnum.UNACCEPTABLE_PROTOCOL: "Protocol version not supported.",
            MQTTStatusEnum.IDENTIFIER_REJECTED: "Client ID rejected by broker.",
            MQTTStatusEnum.SERVER_UNAVAILABLE: "MQTT broker unavailable.",
            MQTTStatusEnum.BAD_USERNAME_OR_PASSWORD: "Invalid username or password.",
            MQTTStatusEnum.NOT_AUTHORIZED: "Client is not authorized to connect.",
            MQTTStatusEnum.DUPLICATE_CLIENT_ID: "Client ID already in use. Device may be logged in elsewhere.",
            MQTTStatusEnum.CONNECTION_LOST: "Connection lost unexpectedly.",
            MQTTStatusEnum.TIMEOUT: "Connection timed out.",
        }
        return status_messages.get(code, "Unknown status code.")