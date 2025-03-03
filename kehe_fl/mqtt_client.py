import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker, port=1883, topic="kehe/fl", username=None, password=None, tls_config=None):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()

        if username and password:
            self.client.username_pw_set(username, password)

        # If TLS is needed, tls_config could be a dictionary containing relevant paths/config.
        if tls_config:
            self.client.tls_set(tls_config.get("ca_cert"))

        # Define event callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # Subscribe to the topic to receive messages from the AS.
        self.client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print(f"Message received: {msg.payload.decode()} on topic {msg.topic}")

    def connect(self):
        """Establish connection to the Aggregation Server."""
        self.client.connect(self.broker, self.port, 60)
        # Start a background loop to process network traffic.
        self.client.loop_start()

    def disconnect(self):
        """Disconnect from the Aggregation Server."""
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, payload, qos=0, retain=False):
        """Publish a message to the Aggregation Server."""
        self.client.publish(self.topic, payload, qos=qos, retain=retain)
