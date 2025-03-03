import paho.mqtt.client as mqtt

class MQTTProvider:
    def __init__(self, broker, port=1883, username=None, password=None, tls_config=None):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()

        if username and password:
            self.client.username_pw_set(username, password)

        if tls_config:
            self.client.tls_set(tls_config.get("ca_cert"))

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] Connected with result code {rc}")

    def on_message(self, client, userdata, msg):
        print(f"[MQTT] Received message: {msg.payload.decode()} on topic {msg.topic}")

    def connect(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic, payload, qos=0, retain=False):
        self.client.publish(topic, payload, qos=qos, retain=retain)
