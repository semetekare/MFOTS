import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, Tuple, Set, Any


def load_data(file_path: str) -> dict:
    """Загружает данные из JSON-файла."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def process_data(data: dict) -> Tuple[Dict[datetime, Dict[int, Set[str]]], Set[int]]:
    """
    Группирует данные по временным интервалам (с точностью до секунды)
    и полосам. Возвращает словарь группировок и множество всех полос.
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
                                      all_lanes: Set[int]) -> Tuple[Dict[int, int], Dict[int, float]]:
    """
    Вычисляет среднюю интенсивность потока (машин/сек) для каждой полосы.
    """
    lane_flow = {}
    total_cars = {}
    total_time_intervals = len(time_lane_intervals)

    for lane in all_lanes:
        total_cars[lane] = sum(len(time_lane_intervals[ti].get(lane, set())) for ti in time_lane_intervals)
        lane_flow[lane] = total_cars[lane] / total_time_intervals if total_time_intervals > 0 else 0.0

    return total_cars, lane_flow


def calculate_capacity(all_lanes: Set[int], green_time: float, cycle_time: float, saturation_flow: float = 0.25) -> float:
    """
    Рассчитывает общую пропускную способность (машин/сек) перекрёстка.
    """
    # (len(all_lanes) * total_flow_intensity) / green_time
    # total_flow_intensity * green_time
    return len(all_lanes) * saturation_flow * (green_time / cycle_time)


def calculate_queue_length_per_lane(lane_flow: Dict[int, float],
                                    red_time: float, car_length: float, capacity: float
                                    ) -> Tuple[Dict[int, float], Dict[int, float], Dict[int, float], Dict[int, float], Dict[int, float]]:
    """
    Вычисляет длину очереди по каждой полосе в метрах и секундах, а также скорость увеличения очереди и задержку очереди.
    """
    queue_cars = {}
    queue_lengths_m = {}
    queue_lengths_sec = {}
    queue_increases = {}
    queue_delays = {}

    saturation_flow = 0.25 # насыщенный поток = 0.25 машин/сек

    for lane, flow in lane_flow.items():
        queue_cars[lane] = flow * red_time
        queue_lengths_m[lane] = flow * red_time * car_length
        queue_lengths_sec[lane] = (flow * red_time) / saturation_flow
        queue_increases[lane] = flow * car_length
        queue_delays[lane] = (flow * red_time) / (2 * saturation_flow)

    return queue_cars, queue_lengths_m, queue_lengths_sec, queue_increases, queue_delays


def print_all_results(time_lane_intervals: Dict[datetime, Dict[int, Set[str]]],
                      total_cars: Dict[int, int],
                      lane_flow: Dict[int, float],
                      total_flow_intensity: float,
                      total_capacity: float,
                      queue_cars: Dict[int, float],
                      queue_lengths_m: Dict[int, float],
                      queue_lengths_sec: Dict[int, float],
                      queue_increases: Dict[int, float],
                      queue_delays: Dict[int, float]) -> None:
    """Выводит все результаты вычислений в удобном формате."""
    print("Интенсивность потока (машин/сек по временным интервалам и полосам):")
    for ti in sorted(time_lane_intervals):
        print(f"{ti}:")
        for lane in sorted(time_lane_intervals[ti]):
            count = len(time_lane_intervals[ti][lane])
            print(f"   Полоса {lane}: {count} машин")

    print("\nИнформация по полосам:")
    for lane in sorted(queue_lengths_m):
        print(f"Полоса {lane}:")
        print(f"  Период наблюдения (T): {len(time_lane_intervals)} сек")
        print(f"  Общее число машин (N): {total_cars[lane]} машин")
        print(f"  Средняя интенсивность потока (λ): ~{lane_flow[lane]:.2f} машин/сек\n")

        print(f"  Число машин в очереди: ~{queue_cars[lane]:.2f} машин")
        print(f"  Длина очереди (L_qm) в метрах: ~{queue_lengths_m[lane]:.2f} м")
        print(f"  Длина очереди (L_qs) в секундах: ~{queue_lengths_sec[lane]:.2f} сек")
        print(f"  Скорость увеличения очереди (V_q): ~{queue_increases[lane]:.2f} м/с")
        print(f"  Задержка в очереди (D): ~{queue_delays[lane]:.2f} сек\n")

    print(f"\nОбщая интенсивность потока (λ): ~{total_flow_intensity:.2f} машин/сек")
    print(f"\nОбщая пропускная способность перекрёстка (μ): ~{total_capacity:.2f} машин/сек")


def main() -> None:
    file_path = 'JSON/Олимпийский20_03_2025_17_35.json'
    green_time = 45  # T_g
    red_time = 30  # T_r
    car_length = 4.5  # L

    cycle_time = green_time + red_time

    data = load_data(file_path)
    time_lane_intervals, all_lanes = process_data(data)
    total_cars, lane_flow = calculate_flow_intensity_per_lane(time_lane_intervals, all_lanes)
    total_flow_intensity = sum(lane_flow.values())
    total_capacity = calculate_capacity(all_lanes, green_time, cycle_time)

    queue_cars, queue_lengths_m, queue_lengths_sec, queue_increases, queue_delays = calculate_queue_length_per_lane(lane_flow, red_time, car_length, total_capacity)

    print_all_results(time_lane_intervals, total_cars, lane_flow, total_flow_intensity, total_capacity,
                      queue_cars, queue_lengths_m, queue_lengths_sec, queue_increases, queue_delays)


if __name__ == '__main__':
    main()
