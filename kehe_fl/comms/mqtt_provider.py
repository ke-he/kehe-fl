import asyncio
import aiomqtt
from typing import Optional

from aiomqtt import Message


class MQTTProvider:
    __is_connected = False
    def __init__(self, broker: str, port=1883, username: Optional[str]=None, password: Optional[str]=None):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password

    async def connect_and_listen(self):
        config = { "hostname": self.broker, "port": self.port }

        if self.username and self.password:
            config["username"] = self.username
            config["password"] = self.password

        async with aiomqtt.Client(**config) as self.client:
            print(f"[MQTT] Connected to {self.broker}:{self.port}")
            await self.subscribe_topics()

            self.__is_connected = True

            async for message in self.client.messages:
                await self.on_message(message)

    async def subscribe(self, topic):
        await self.client.subscribe(topic)
        print(f"[MQTT] Subscribed to {topic}")

    async def subscribe_topics(self):
        pass

    async def on_message(self, message: Message):
        pass

    async def publish(self, topic, payload, qos=0, retain=False):
        await self.client.publish(topic, payload, qos=qos, retain=retain)
        pass

    @property
    def is_connected(self):
        return self.__is_connected
