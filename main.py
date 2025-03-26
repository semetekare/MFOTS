import json
from datetime import datetime
from collections import defaultdict

# Загрузка данных
with open('JSON\Олимпийский20_03_2025_17_35.json', 'r') as f:
    data = json.load(f)

# Словарь для подсчета уникальных машин по секундам
#time_intervals = defaultdict(set)

# Словарь для подсчета уникальных машин по секундам и линиям
# Структура: {время: {lane: set(uuids)}}
time_lane_intervals = defaultdict(lambda: defaultdict(set))

'''
# Обработка данных
for obj in data['objects']:
    if obj['name'] == 'OBJECTS':
        for row in obj['rows_data']:
            time_str = row['time']
            uuid = row['uuid']
            time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
            interval = time.replace(microsecond=0)  # Группировка по секундам
            time_intervals[interval].add(uuid)
            
# Вывод результатов
print("Интенсивность потока (машин/сек):")
for interval, uuids in sorted(time_intervals.items()):
    print(f"{interval}: {len(uuids)}")
'''

# Собираем все номера линий для корректного расчёта (если для какого-то временного интервала линия отсутствует)
all_lanes = set()

# Обработка данных
for obj in data['objects']:
    if obj['name'] == 'OBJECTS':
        for row in obj['rows_data']:
            time_str = row['time']
            lane = row['lane']
            uuid = row['uuid']
            time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
            time_interval = time_obj.replace(microsecond=0)  # Группировка по секундам
            time_lane_intervals[time_interval][lane].add(uuid)
            all_lanes.add(lane)

# Вывод результатов: сначала по времени, затем по lane
print("Интенсивность потока (машин/сек по линиям):")
for time_interval in sorted(time_lane_intervals):
    print(f"{time_interval}:")
    for lane in sorted(time_lane_intervals[time_interval]):
        count = len(time_lane_intervals[time_interval][lane])
        print(f"   Линия {lane}: {count} машин")

'''
# Расчет пропускной способности
total_cars = sum(len(uuids) for uuids in time_intervals.values())
total_seconds = len(time_intervals)
average_per_second = total_cars / total_seconds if total_seconds > 0 else 0
'''

# Расчёт пропускной способности по каждой линии
lane_capacities = {}

# Для каждого lane посчитаем общее количество машин и количество секунд, учитывая, что если для какого-то секунды нет данных по линии – считаем 0.
# Количество секунд определяется как общее число временных интервалов (так как анализ проводился с одинаковой разбиением по времени)
total_time_intervals = len(time_lane_intervals)

for lane in all_lanes:
    total_cars_lane = 0
    # Для каждого временного интервала получаем количество машин на данной линии (если данных нет – 0)
    for time_interval in time_lane_intervals:
        total_cars_lane += len(time_lane_intervals[time_interval].get(lane, set()))
    # Среднее количество машин в секунду для линии
    average_per_second_lane = total_cars_lane / total_time_intervals if total_time_intervals > 0 else 0
    # Пропускная способность линии в час (экстраполяция)
    capacity_per_hour_lane = average_per_second_lane * 3600
    lane_capacities[lane] = average_per_second_lane

# Вывод результатов по линиям
print("\nПропускная способность по линиям (машин/сек):")
for lane in sorted(lane_capacities):
    print(f"Линия {lane}: ~{int(lane_capacities[lane])} машин/сек")

# Расчёт общей пропускной способности (сумма по всем линиям)
total_capacity = sum(lane_capacities.values())
print(f"\nОбщая пропускная способность: ~{int(total_capacity)} машин/сек")

'''
# Расчет пропускной способности
total_cars = sum(len(uuids) for uuids in time_lane_intervals.values())
total_seconds = len(time_lane_intervals)
average_per_second = total_cars / total_seconds if total_seconds > 0 else 0

print(f"\nПропускная способность: ~{int(average_per_second)} машин/сек")

capacity_per_hour = average_per_second * 3600

print(f"\nПропускная способность: ~{int(capacity_per_hour)} машин/час")
'''