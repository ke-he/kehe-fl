class ProjectConstants:
    CSV_FIELDS = ["timestamp", "co2", "temperature", "humidity"]
    DATA_DIRECTORY = "./logs"
    CMD_TOPIC = "sys/cmd/"
    FEEDBACK_TOPIC = "sys/feedback/"
    COLLECTION_INTERVAL = 2  # seconds