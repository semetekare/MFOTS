import time
import json

# Класс для представления светофора
class TrafficLight:
    def __init__(self, direction):
        self.direction = direction
        self.state = "red"  # Начальное состояние

    def switch_to_green(self):
        self.state = "green"

    def switch_to_red(self):
        self.state = "red"

    def __repr__(self):
        return f"{self.direction}: {self.state}"


# Функция для загрузки данных с датчиков из JSON-файла
def load_sensor_data(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data


# Функция оптимизации переключения светофоров с учетом данных датчиков
def optimize_traffic_lights(traffic_lights, sensor_data):
    sensors = sensor_data["sensors"]
    params = sensor_data["parameters"]
    min_green_duration = params.get("min_green_duration", 5)
    max_green_duration = params.get("max_green_duration", 30)
    cycle_duration = params.get("cycle_duration", 60)

    # Суммарное количество транспортных средств на всех направлениях
    total_vehicle_count = sum(sensor["vehicle_count"] for sensor in sensors)

    # Если машин нет, выбираем первое направление по умолчанию
    if total_vehicle_count == 0:
        selected_direction = traffic_lights[0].direction
        green_time = min_green_duration
    else:
        # Вычисляем долю для каждого направления
        proportions = {sensor["direction"]: sensor["vehicle_count"] / total_vehicle_count for sensor in sensors}
        # Выбираем направление с наибольшей нагрузкой
        selected_direction = max(proportions, key=proportions.get)
        # Расчет длительности зеленого сигнала пропорционально нагрузке
        green_time = min_green_duration + proportions[selected_direction] * (max_green_duration - min_green_duration)

    # Переключаем светофоры: выбранному направлению даем зеленый, остальные – красный
    for light in traffic_lights:
        if light.direction.lower() == selected_direction.lower():
            light.switch_to_green()
        else:
            light.switch_to_red()

    print(f"Выбрано направление: {selected_direction}, зеленый свет на {green_time:.1f} секунд")
    for light in traffic_lights:
        print(light)

    # Держим зеленый свет на рассчитанное время
    time.sleep(green_time)

    # По окончании цикла сбрасываем состояние светофоров
    print("Цикл завершен. Сброс состояния светофоров.")
    for light in traffic_lights:
        light.switch_to_red()

    # Оставшееся время цикла (если green_time меньше общего времени цикла)
    remaining = max(0, cycle_duration - green_time)
    if remaining > 0:
        time.sleep(remaining)


def main():
    # Загружаем данные с датчиков из файла sensor_data.json
    sensor_data = load_sensor_data("sensor_data.json")
    # Инициализируем светофоры для 4 направлений
    directions = ["North", "South", "East", "West"]
    traffic_lights = [TrafficLight(direction) for direction in directions]

    # Запускаем алгоритм переключения светофоров в бесконечном цикле
    while True:
        optimize_traffic_lights(traffic_lights, sensor_data)
        print("-" * 40)
        # Краткая задержка перед началом нового цикла
        time.sleep(1)


if __name__ == "__main__":
    main()
