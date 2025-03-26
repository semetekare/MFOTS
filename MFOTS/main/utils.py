import json
import time
from MFOTS.env_config import CONFIG
import redis

redis_client = redis.Redis(host=CONFIG.REDIS_HOST, port=CONFIG.REDIS_PORT, db=0)
def read_json_and_store_in_redis(file_path):
    """Читает JSON-файл и сохраняет данные в Redis."""
    with open(file_path, 'r') as f:
        data = json.load(f)
        for item in data:
            # Предполагаем, что 'id' — уникальный идентификатор; замените на 'uuid', если нужно
            redis_client.set(f"item:{item['id']}", json.dumps(item))

def update_redis_periodically(file_path):
    """Периодически обновляет данные в Redis из JSON-файла."""
    while True:
        read_json_and_store_in_redis(file_path)
        time.sleep(5)  # Обновляем каждые 5 секунд

def calculate_formulas():
    """Вычисляет среднюю скорость объектов из данных в Redis."""
    keys = redis_client.keys("item:*")
    total_speed = 0
    count = 0
    for key in keys:
        item = json.loads(redis_client.get(key))
        total_speed += item.get('obj_speed', 0)  # Используем 'obj_speed' вместо 'value'
        count += 1
    if count > 0:
        average_speed = total_speed / count
        return {'average_speed': average_speed}
    return {'average_speed': 0}