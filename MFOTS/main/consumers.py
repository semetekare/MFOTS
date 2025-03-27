from .utils import calculate_formulas
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
import threading
import asyncio
import time
import json

class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Подключает клиента к группе 'calculations'."""
        await self.accept()
        await self.channel_layer.group_add("calculations", self.channel_name)

    async def disconnect(self, close_code):
        """Отключает клиента от группы."""
        await self.channel_layer.group_discard("calculations", self.channel_name)

    async def send_calculation(self, event):
        """Отправляет вычисления клиенту."""
        calculation = event['calculation']
        await self.send(text_data=json.dumps(calculation))

def start_background_task():
    print("Запуск фоновой задачи при старте Django.")
    channel_layer = get_channel_layer()
    loop = asyncio.get_event_loop()
    loop.create_task(background_calculations(channel_layer))

async def background_calculations(channel_layer):
    print("Глобальная фоновая задача для всех клиентов.")
    while True:
        try:
            # Вычисляем среднюю скорость
            calculation = await sync_to_async(calculate_formulas)()
            # Отправляем через Channel Layer
            print(f"Отправка данных: {calculation}")
            await channel_layer.group_send(
                "calculations",
                {
                    "type": "send_calculation",  # Должно совпадать с методом в консьюмере
                    "calculation": calculation
                }
            )
            print(f"Отправлено вычисление: {calculation}")
            await asyncio.sleep(1)  # Отправка каждую секунду
        except Exception as e:
            print(f"Ошибка фоновой задачи: {str(e)}")