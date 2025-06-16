# kehe-fl

A federated learning package for IoT devices and aggregation server communication using MQTT.

## Features

- Distributed, federated learning orchestration using MQTT
- Device-side and server-side reference implementations
- Asyncio-based for efficient concurrency
- Modular design for custom ML or IoT projects

## Quick Start

### Installation

```bash
pip install kehe-fl
```

### Example Usage
#### Device Side
```python
import asyncio
from kehe_fl.comms.mqtt_device import MQTTDevice

mqttConnection: MQTTDevice | None = None

async def main():
    global mqttConnection

    mqttConnection = MQTTDevice(broker="192.168.1.193", deviceId="device123")

    mqtt_task = asyncio.create_task(mqttConnection.connect_and_listen())

    await asyncio.gather(mqtt_task)

asyncio.run(main())
```

#### Aggregation Server Side
```python
import asyncio
from kehe_fl.comms.mqtt_agg_server import MQTTAggServer

mqttConnection: MQTTAggServer | None = None

async def handleMessaging():
    global mqttConnection
    loop = asyncio.get_running_loop()

    while True:
        if mqttConnection.is_connected and not mqttConnection.working:
            message = await loop.run_in_executor(None, input, "Enter a command to send to the clients: ")
            await mqttConnection.send_command(message)
        else:
            await asyncio.sleep(2)

async def main():
    global mqttConnection

    mqttConnection = MQTTAggServer(broker="localhost")

    mqtt_task = asyncio.create_task(mqttConnection.connect_and_listen())
    input_task = asyncio.create_task(handleMessaging())

    await asyncio.gather(mqtt_task, input_task)

asyncio.run(main())
```

### Adapt
#### Communication
You can adapt the device and server code to your specific ML or IoT project needs by modifying the `MQTTDevice` and `MQTTAggServer` or even `MQTTProvider` classes. These classes provide a foundation for communication and can be extended with custom logic for model training, data handling, and more.

#### Machine Learning
You can integrate your preferred machine learning libraries (like TensorFlow, PyTorch, etc.) into the device and server implementations with modifying `ModelService`. The provided classes can be used to send model updates, receive commands, and manage the training process across devices.

#### Data Collection
You can implement custom sensor classes in `common/<your sensor>.py`and also modify the `DataCollectionService` for your needs. This allows you to collect and process data from various IoT sensors and devices, which can then be used for training machine learning models.

#### Project Constants
You can modify the `project_constants.py` file to change the MQTT topic structure, message formats, and other constants used throughout the package. This allows you to tailor the communication protocol to your specific requirements.
