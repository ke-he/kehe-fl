import json

import aiomqtt
import asyncio
from typing import Optional, Union

import numpy as np
from aiomqtt import Message

class MQTTProvider:
    def __init__(self, broker: str, port=1883, username: Optional[str] = None, password: Optional[str] = None):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self._is_connected = False
        self._lock = asyncio.Lock()

    async def connect_and_listen(self):
        config = {"hostname": self.broker, "port": self.port}
        if self.username and self.password:
            config["username"] = self.username
            config["password"] = self.password

        async with aiomqtt.Client(**config) as self.client:
            print(f"[MQTT] Connected to {self.broker}:{self.port}")
            await self.subscribe_topics()
            self._is_connected = True

            async for message in self.client.messages:
                async with self._lock:
                    topic, payload = self.__decode_message(message)
                    await self.on_message(topic, payload)

    async def subscribe(self, topic: str) -> None:
        await self.client.subscribe(topic)
        print(f"[MQTT] Subscribed to {topic}")

    async def subscribe_topics(self) -> None:
        pass

    async def on_message(self, topic: str, payload: Union[str, int]) -> None:
        pass

    async def publish(self, topic: str, payload: Union[str, int, list, None]=None, qos=0, retain=False) -> None:
        await self.client.publish(topic, payload, qos=qos, retain=retain)

    @staticmethod
    def __decode_message(message: Message) -> tuple[str, Union[str, int]]:
        return message.topic.value, MQTTProvider.__parse_payload(message.payload.decode())

    @staticmethod
    def __parse_payload(payload: str) -> Union[str, int]:
        return int(payload) if payload.isnumeric() else payload

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    async def _send_weights(self, topic, weights):
        if weights is not None and len(weights) > 0:
            await self.publish(topic, json.dumps(weights.tolist()))
        else:
            await self.publish(topic, None)

    @staticmethod
    def _unpack_weights(weights):
        weights_list = json.loads(weights)
        return np.array(weights_list)
