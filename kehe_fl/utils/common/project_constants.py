class ProjectConstants:
    CSV_FIELDS = ["timestamp", "co2", "temperature", "humidity"]
    DATA_DIRECTORY = "./data"
    MONITORING_DIRECTORY = "./monitoring"
    CMD_TOPIC = "sys/cmd/"
    FEEDBACK_TOPIC = "sys/feedback/"
    DATA_TOPIC = "sys/data/"
    FL_ROUND_TOPIC = "sys/fl_round/"
    FL_ROUND_HANDLE = "sys/fl_round_handle/"
    COLLECTION_INTERVAL = 2  # seconds
    FL_ALPHA = 1e-7
    FL_EPOCHS = 3
    FL_GLOBAL_EPOCHS = 20
    MONITORING_INTERVAL = 1  # seconds
    CLIENT_DEVICES = 2
