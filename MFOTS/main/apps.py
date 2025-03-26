import os
import threading
from django.apps import AppConfig
from .utils import read_json_and_store_in_redis, update_redis_periodically
from .consumers import start_background_task


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        # Читаем JSON и сохраняем в Redis при старте
        read_json_and_store_in_redis('json.json')
        print("Json прочитан")
        # Запускаем поток для периодического обновления данных в Redis
        threading.Thread(target=update_redis_periodically, args=('json.json',), daemon=True).start()
        # Запускаем фоновую задачу для отправки вычислений через WebSocket
        start_background_task()