import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple, Set, List, Any
import os

import glob



def load_data(file_path: str) -> dict:
    """Загружает данные из JSON-файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
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


def calculate_metrics_per_second(time_lane_intervals: Dict[datetime, Dict[int, Set[str]]],
                                 all_lanes: Set[int],
                                 red_time: float,
                                 car_length: float,
                                 green_time: float,
                                 cycle_time: float) -> List[Dict[str, Any]]:
    """
    Вычисляет метрики для каждой секунды и возвращает список результатов.
    """
    results = []
    saturation_flow = 0.25  # машин/сек
    sorted_times = sorted(time_lane_intervals.keys())

    for i, current_time in enumerate(sorted_times):
        # Собираем данные для текущей секунды
        current_data = time_lane_intervals[current_time]

        # Рассчитываем метрики для каждой полосы
        lane_metrics = {}
        for lane in all_lanes:
            cars_in_lane = len(current_data.get(lane, set()))

            # Рассчитываем метрики
            queue_cars = cars_in_lane
            queue_length_m = queue_cars * car_length
            queue_length_sec = queue_cars / saturation_flow
            queue_increase = cars_in_lane * car_length
            queue_delay = queue_cars / (2 * saturation_flow)

            lane_metrics[lane] = {
                "cars_in_lane": cars_in_lane,
                "queue_cars": queue_cars,
                "queue_length_m": queue_length_m,
                "queue_length_sec": queue_length_sec,
                "queue_increase": queue_increase,
                "queue_delay": queue_delay
            }

        # Рассчитываем общие метрики
        total_flow_intensity = sum(len(current_data.get(lane, set())) for lane in all_lanes)
        total_capacity = len(all_lanes) * saturation_flow * (green_time / cycle_time)

        # Формируем результат для текущей секунды
        result = {
            "timestamp": current_time.strftime('%Y-%m-%d %H:%M:%S'),
            "lane_metrics": lane_metrics,
            "total_flow_intensity": total_flow_intensity,
            "total_capacity": total_capacity
        }

        results.append(result)

    return results


def save_results_to_json(results: List[Dict[str, Any]], output_file: str) -> None:
    """Сохраняет результаты в JSON-файл."""
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)


def process_single_file(input_file: str, output_dir: str,
                        green_time: float, red_time: float,
                        car_length: float, cycle_time: float) -> None:
    """Обрабатывает один файл и сохраняет результаты."""
    # Создаем имя выходного файла
    base_name = os.path.basename(input_file)
    output_name = f"metrics_{base_name}"
    output_file = os.path.join(output_dir, output_name)


    # Загрузка и обработка данных
    data = load_data(input_file)
    time_lane_intervals, all_lanes = process_data(data)

    # Расчет метрик
    results = calculate_metrics_per_second(
        time_lane_intervals,
        all_lanes,
        red_time,
        car_length,
        green_time,
        cycle_time
    )

    # Сохранение результатов
    save_results_to_json(results, output_file)
    print(f"Результаты для {input_file} сохранены в {output_file}")



def main() -> None:
    # Параметры
    input_dir = 'MFOTS/json/'  # Папка с входными JSON-файлами
    output_dir = 'MFOTS/metrics_results/'  # Папка для сохранения результатов
    input_file = 'MFOTS/json/Олимпийский20_03_2025_17_35.json'
    output_file = 'metrics.json'
    
    green_time = 45  # T_g (сек)
    red_time = 30  # T_r (сек)
    car_length = 4.5  # L (м)
    cycle_time = green_time + red_time  # T_c (сек)

    # Создаем папку для результатов, если ее нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Находим все JSON-файлы в папке
    input_files = glob.glob(os.path.join(input_dir, '*.json'))

    if not input_files:
        print(f"Не найдено JSON-файлов в папке {input_dir}")
        return

    # Обрабатываем каждый файл
    for input_file in input_files:
        try:
            process_single_file(input_file, output_dir,
                                green_time, red_time,
                                car_length, cycle_time)
        except Exception as e:
            print(f"Ошибка при обработке файла {input_file}: {str(e)}")

    # Загрузка и обработка данных
    data = load_data(input_file)
    time_lane_intervals, all_lanes = process_data(data)

    # Расчет метрик для каждой секунды
    results = calculate_metrics_per_second(
        time_lane_intervals,
        all_lanes,
        red_time,
        car_length,
        green_time,
        cycle_time
    )

    # Сохранение результатов
    save_results_to_json(results, output_file)
    print(f"Результаты сохранены в {output_file}")



if __name__ == '__main__':
    main()