import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, Tuple, Set


def load_data(file_path: str) -> dict:
    """Загружает данные из JSON-файла."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def process_data(data: dict) -> Tuple[Dict[datetime, Dict[int, Set[str]]], Set[int]]:
    """
    Группирует данные по временным интервалам (с точностью до секунды)
    и линиям. Возвращает словарь группировок и множество всех линий.
    """
    time_lane_intervals = defaultdict(lambda: defaultdict(set))
    all_lanes = set()

    for obj in data['objects']:
        if obj['name'] == 'OBJECTS':
            for row in obj['rows_data']:
                time_str = row['time']
                lane = row['lane']
                uuid = row['uuid']
                time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
                time_interval = time_obj.replace(microsecond=0)
                time_lane_intervals[time_interval][lane].add(uuid)
                all_lanes.add(lane)

    return time_lane_intervals, all_lanes


def calculate_flow_intensity_per_lane(time_lane_intervals: Dict[datetime, Dict[int, Set[str]]],
                                      all_lanes: Set[int]) -> Dict[int, float]:
    """
    Вычисляет среднюю интенсивность потока (машин/сек) для каждой полосы.
    """
    lane_flow = {}
    total_time_intervals = len(time_lane_intervals)

    for lane in all_lanes:
        total_cars_lane = sum(len(time_lane_intervals[ti].get(lane, set())) for ti in time_lane_intervals)
        lane_flow[lane] = total_cars_lane / total_time_intervals if total_time_intervals > 0 else 0.0

    return lane_flow


def calculate_capacity(all_lanes: Set[int], total_flow_intensity: float, green_time: float) -> float:
    """
    Рассчитывает общую пропускную способность (машин/сек) перекрестка.
    """
    return len(all_lanes) * total_flow_intensity / green_time


def calculate_queue_length_per_lane(lane_flow: Dict[int, float],
                                    red_time: float, car_length: float
                                    ) -> Tuple[Dict[int, float], Dict[int, float], Dict[int, float]]:
    """
    Вычисляет длину очереди по каждой полосе в метрах и секундах, а также скорость увеличения очереди.
    """
    queue_lengths_m = {}
    queue_lengths_sec = {}
    queue_increases = {}

    for lane, flow in lane_flow.items():
        queue_lengths_m[lane] = flow * red_time * car_length
        queue_lengths_sec[lane] = flow * red_time
        queue_increases[lane] = flow * car_length

    return queue_lengths_m, queue_lengths_sec, queue_increases


def calculate_queue_delay_per_lane(queue_lengths_m: Dict[int, float],
                                   lane_flow: Dict[int, float],
                                   red_time: float) -> Dict[int, float]:
    """
    Вычисляет задержку очереди для каждой полосы.
    Формула: delay = L_q / (2 * λ)
    """
    queue_delays = {}
    for lane in lane_flow:
        # Для отладки выводим промежуточные значения:
        #print(f"Линия {lane}:")
        #print(f"  Длина очереди (L_q) в метрах: {queue_lengths_m[lane]}")
        #print(f"  Пропускная способность (λ): {lane_flow[lane]}")
        #print(f"  Время красного сигнала (T_r): {red_time}")
        delay = queue_lengths_m[lane] / (2 * lane_flow[lane]) if lane_flow[lane] else 0.0
        queue_delays[lane] = delay
    return queue_delays


def print_all_results(time_lane_intervals: Dict[datetime, Dict[int, Set[str]]],
                      lane_flow: Dict[int, float],
                      total_flow_intensity: float,
                      capacity: float,
                      queue_lengths_m: Dict[int, float],
                      queue_lengths_sec: Dict[int, float],
                      queue_increases: Dict[int, float],
                      queue_delays: Dict[int, float]) -> None:
    """Выводит все результаты вычислений в удобном формате."""
    print("Интенсивность потока (машин/сек по временным интервалам и линиям):")
    for ti in sorted(time_lane_intervals):
        print(f"{ti}:")
        for lane in sorted(time_lane_intervals[ti]):
            count = len(time_lane_intervals[ti][lane])
            print(f"   Линия {lane}: {count} машин")

    print("\nИнтенсивность потока по линиям (машин/сек):")
    for lane in sorted(lane_flow):
        print(f"Линия {lane}: ~{lane_flow[lane]:.2f} машин/сек")

    print(f"\nОбщая интенсивность потока (λ): ~{total_flow_intensity:.2f} машин/сек")
    print(f"\nПропускная способность (μ): ~{capacity:.2f} машин/сек")

    print("\nДлина очереди по полосам:")
    for lane in sorted(queue_lengths_m):
        print(f"Линия {lane}:")
        print(f"  Длина очереди (L_q) в метрах: ~{queue_lengths_m[lane]:.2f} м")
        print(f"  Длина очереди (L_q) в секундах: ~{queue_lengths_sec[lane]:.2f} сек")
        print(f"  Скорость увеличения очереди (V_q): ~{queue_increases[lane]:.2f} м/с")

    print("\nЗадержка очереди по полосам:")
    for lane in sorted(queue_delays):
        print(f"  Линия {lane}: ~{queue_delays[lane]:.2f} сек")


def main() -> None:
    file_path = 'JSON/Олимпийский20_03_2025_17_35.json'
    green_time = 30  # T_g
    red_time = 30  # T_r
    car_length = 4.5  # L

    data = load_data(file_path)
    time_lane_intervals, all_lanes = process_data(data)

    lane_flow = calculate_flow_intensity_per_lane(time_lane_intervals, all_lanes)
    total_flow_intensity = sum(lane_flow.values())
    capacity = calculate_capacity(all_lanes, total_flow_intensity, green_time)

    queue_lengths_m, queue_lengths_sec, queue_increases = calculate_queue_length_per_lane(lane_flow, red_time,
                                                                                          car_length)
    queue_delays = calculate_queue_delay_per_lane(queue_lengths_m, lane_flow, red_time)

    print_all_results(time_lane_intervals, lane_flow, total_flow_intensity, capacity,
                      queue_lengths_m, queue_lengths_sec, queue_increases, queue_delays)


if __name__ == '__main__':
    main()
