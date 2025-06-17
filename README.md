# kehe-fl

A Proof of Concept (PoC) for Privacy-Preserving Federated Learning with IoT Devices, developed for the Bachelor’s thesis `Machbarkeitsanalyse von Federated Learning mit Internet of Things: Vergleich zentralisierter und dezentraler Trainingsansätze`.

This repository implements a minimal, research-focused federated learning system, demonstrating distributed ML model training on resource-constrained IoT clients, coordinated via an MQTT broker, with a central aggregation server.

## Features

- Federated Learning Protocol: Orchestrates distributed training rounds between a central server and multiple IoT clients.

- MQTT-based Communication: Efficient, lightweight message exchange suitable for IoT environments.

- Device and Server Reference Implementations: Both roles can be run for local or distributed experiments.

- Asyncio-based Concurrency: Enables scalable and non-blocking communication and control.

- Pluggable ML Logic: Simple linear regression for demonstration; can be extended for further experiments.

- Resource Monitoring: Optional metrics collection on devices and server (CPU, memory, network I/O) to support analysis of communication and computation overhead.

## Purpose

This codebase serves as a research PoC to empirically evaluate:

- The feasibility of federated learning on real IoT hardware (e.g., Raspberry Pi).

- The system-level overhead and requirements for PPML in practical settings.

- Tradeoffs between centralized and decentralized model training (scalability, communication cost, resource usage).

- The project is not a production-ready federated learning framework, but a minimal, transparent testbed for measuring and analyzing privacy-preserving ML on IoT devices.

## Quick Start

### Packages
- **FL Scenario (S1 | kehe_fl):** Individual models are trained on each edge device. The respective model updates are sent to the aggregation server (AS), aggregated there, and then redistributed to the edge devices.

- **Centralized Scenario (S2 | kehe_fl_s2):** Model training takes place only on the central server, which receives the raw data from each edge device.

- **Decentralized/Local Training without Aggregation (S3 | kehe_fl_s3):** Individual models are trained on each edge device, but model updates are not exchanged between edge devices or through the aggregation server.

### Installation (MacOS/Linux)
Start an MQTT broker (e.g., Mosquitto) on your local machine or server. The default broker address in the code is `localhost`, but you can change it to your broker's address. (You may need a config file for Mosquitto to allow anonymous access or set up user credentials.)

```bash
mosquitto -c /path/to/mosquitto.conf
```

```bash
pip install kehe-fl
```

### Usage Overview

#### 1. Device (Client)

Each IoT device runs a client that:

- Connects to the MQTT broker

- Receives training instructions and model weights

- Trains the model locally on its private data

- Sends model updates back to the aggregation server

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

#### 2. Aggregation Server

The aggregation server:

- Coordinates the global training process

- Sends commands to clients

- Receives, aggregates, and distributes model weights

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

#### 3. Customization

- Communication: Adapt MQTT topics and payloads in project_constants.py as needed.

- Machine Learning Logic: Replace or extend the model in ModelService with your own (e.g., scikit-learn, PyTorch, etc.).

- Sensor Data: Add your own sensor integration or data preprocessing in the common/ or service/ modules.

- Metrics: Extend resource monitoring for more detailed benchmarking and analysis.

### Documentation
For experimental methodology, data collection, and analysis, see the Bachelor’s Thesis.

### Disclaimer

This project is intended for research and educational purposes only.Not suitable for production use.
