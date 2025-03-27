import pygame
import json
import time
import random
from colors import COLORS

# Инициализация Pygame
pygame.init()

# Константы экрана
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
BACKGROUND_COLOR = (33, 33, 33)

# Настройки экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Перекресток")

# Параметры отображения машин
CAR_RADIUS = 25
FONT_SIZE = 25
END_FONT_SIZE = 60

# Параметры полос дороги
LANE_COUNT = 6
# Для отрисовки разделительных линий между полосами (всего 5 межполосных линий)
# Центральной считается линия между полосами 2 и 3.
SOLID_DIVIDER_INDEX = 3  # нумерация разделителей от 1 до NUM_LANES-1 (т.е. 1,2,3,4,5)
LANE_LINE_COLOR = (255, 255, 255)
SOLID_LINE_WIDTH = 4           # толщина сплошной линии
DASHED_LINE_WIDTH = 2          # толщина пунктирной линии
DASH_LENGTH = 20
SPACE_LENGTH = 20
LANE_HEIGHT = SCREEN_HEIGHT / LANE_COUNT

# Создаем словарь с координатами Y для каждой полосы
lane_positions = {i: (i + 1) * LANE_HEIGHT for i in range(LANE_COUNT)}

# Параметры перекрестка (отрисовывается слева)
INTERSECTION_WIDTH = 200
INTERSECTION_COLOR = (200, 200, 200)

# Инициализация шрифта
font = pygame.font.SysFont(None, FONT_SIZE)
end_font = pygame.font.SysFont(None, END_FONT_SIZE)
intersection_font = pygame.font.SysFont(None, 30)


# Функция загрузки данных из JSON
def load_json(filename):
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            data = json.load(file)
            return data.get('objects', [])  # Извлекаем список объектов
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка загрузки JSON: {e}")
        return []


# Функция группировки данных по временным меткам
def group_by_time(objects):
    time_dict = {}
    min_x = float('inf')

    for obj in objects:
        for row in obj.get('rows_data', []):
            # Проверяем наличие необходимых ключей
            if 'point_x' in row and 'obj_id' in row and 'lane' in row:
                obj_id = row['obj_id']
                x = row.get('point_x', 0)
                lane = row.get('lane', 0)
                min_x = min(min_x, x)
                time_str = row.get('time')
                if time_str:
                    if time_str not in time_dict:
                        time_dict[time_str] = []
                    time_dict[time_str].append((obj_id, lane, x))
    return sorted(time_dict.items()), min_x  # Сортируем по времени и возвращаем минимальные координаты


# Основной цикл программы
def main():
    filename = 'JSON/Олимпийский20_03_2025_17_35.json'
    objects = load_json(filename)
    time_frames, min_x = group_by_time(objects)

    if not time_frames:
        print("Нет данных для отображения.")
        return

    # Смещение по x для центрирования дорожной оси (масштаб по x – коэффициент 6 подобран экспериментально)
    scale_x = 10
    margin = 10  # отступ от перекрестка
    offset_x = INTERSECTION_WIDTH + margin - int(min_x * scale_x)

    # Словарь для закрепления цвета за obj_id
    id_to_color = {}

    clock = pygame.time.Clock()
    running = True
    frame_index = 0

    # Для плавной анимации храним текущие позиции для каждого объекта: {obj_id: (x, y)}
    current_positions = {}

    # Начальная продолжительность анимации
    duration = 0.1  # продолжительность анимации в секундах

    while running:
        if frame_index  >= len(time_frames):
            screen.fill(BACKGROUND_COLOR)
            draw_lanes()  # рисуем полосы
            draw_intersection()  # рисуем перекресток
            pygame.display.update()
            print("Все временные метки обработаны. Программа закроется через 1.5 секунды.")
            pygame.time.delay(1500)
            break

        # Берём данные для следующего кадра
        current_time, frame_data = time_frames[frame_index]
        # Вычисляем целевые позиции: для каждого машины определяем (target_x, target_y)
        target_positions = {}
        for obj_id, lane, x in frame_data:
            if obj_id not in id_to_color:
                id_to_color[obj_id] = random.choice(COLORS)
            target_x = int(x * scale_x + offset_x)
            # Позиция по y определяется как центр полосы, вычисляем по lane
            target_y = int(lane * LANE_HEIGHT + LANE_HEIGHT / 2)
            target_positions[obj_id] = (target_x, target_y)

        # Если для какого-то объекта нет предыдущей позиции, используем целевую
        for obj_id in target_positions:
            if obj_id not in current_positions:
                current_positions[obj_id] = target_positions[obj_id]

        # Анимация перехода между кадрами за duration секунд
        elapsed = 0.0
        while elapsed < duration:
            dt = clock.tick(60) / 1000.0  # время в секундах
            elapsed += dt
            alpha = min(elapsed / duration, 1.0)

            # Интерполируем позиции для каждого машины
            interpolated_positions = {}
            for obj_id, target in target_positions.items():
                start = current_positions.get(obj_id, target)
                interp_x = int(start[0] + (target[0] - start[0]) * alpha)
                interp_y = int(start[1] + (target[1] - start[1]) * alpha)
                interpolated_positions[obj_id] = (interp_x, interp_y)

            # Отрисовка кадра
            screen.fill(BACKGROUND_COLOR)
            draw_lanes()
            draw_intersection()

            # Выводим время кадра
            time_text = font.render(f"Время: {current_time}", True, (255, 255, 255))
            screen.blit(time_text, (220, 20))
            frame_text = font.render(f"Отображается кадр {frame_index + 1}/{len(time_frames)}", True, (255, 255, 255))
            screen.blit(frame_text, (SCREEN_WIDTH / 2, 20))

            # Отображаем значение duration
            duration_text = font.render(f"Скорость анимации: {duration:.2f} сек", True, (255, 255, 255))
            screen.blit(duration_text, (SCREEN_WIDTH - 250, 20))  # Рисуем текст на экране

            # Отрисовка стрелок направления движения
            left_arrow_pos = (lane_positions[0] + lane_positions[1]) / 2
            draw_arrow(screen, SCREEN_WIDTH / 2, left_arrow_pos, "left")  # Стрелки влево на 1-й полосе
            right_arrow_pos = (lane_positions[3] + lane_positions[4]) / 2
            draw_arrow(screen, SCREEN_WIDTH / 2, right_arrow_pos, "right")  # Стрелки вправо на 4-й полосе

            # Отрисовка машин
            for obj_id, pos in interpolated_positions.items():
                color = id_to_color[obj_id]
                pygame.draw.circle(screen, color, pos, CAR_RADIUS)
                id_text = font.render(str(obj_id), True, (0, 0, 0))
                text_rect = id_text.get_rect(center=(pos[0], pos[1]))
                screen.blit(id_text, text_rect)

            pygame.display.update()

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_EQUALS:  # Клавиша "+" на клавиатуре
                        duration = max(0.01, duration - 0.02)  # Уменьшаем продолжительность анимации
                    elif event.key == pygame.K_MINUS:  # Клавиша "-" на клавиатуре
                        duration = min(0.5, duration + 0.02)  # Увеличиваем продолжительность анимации

        # После анимации обновляем текущие позиции
        current_positions = target_positions.copy()
        frame_index += 1

    pygame.quit()


# Функция для отрисовки полос
def draw_lanes():
    # Отрисовываем горизонтальные линии, разделяющие полосы
    # Для разделителей между полосами (индексы 1..(NUM_LANES-1)):
    for divider in range(1, LANE_COUNT):
        y = int(divider * LANE_HEIGHT)
        # Центральный разделитель (между полосами 2 и 3) отрисовывается сплошной
        if divider == SOLID_DIVIDER_INDEX:
            pygame.draw.line(screen, LANE_LINE_COLOR, (0, y), (SCREEN_WIDTH, y), SOLID_LINE_WIDTH)
        else:
            draw_dashed_line(screen, LANE_LINE_COLOR, (0, y), (SCREEN_WIDTH, y), DASHED_LINE_WIDTH, DASH_LENGTH, SPACE_LENGTH)
    # Можно также отрисовать внешние границы дороги (сплошные)
    pygame.draw.line(screen, LANE_LINE_COLOR, (0, 0), (SCREEN_WIDTH, 0), SOLID_LINE_WIDTH)
    pygame.draw.line(screen, LANE_LINE_COLOR, (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), SOLID_LINE_WIDTH)


# Функция для отрисовки пунктирной линии (горизонтальной)
def draw_dashed_line(surface, color, start_pos, end_pos, width, dash_length, space_length):
    x1, y1 = start_pos
    x2, y2 = end_pos
    total_length = x2 - x1
    num_dashes = total_length // (dash_length + space_length)
    for i in range(int(num_dashes) + 1):
        start_x = x1 + i * (dash_length + space_length)
        end_x = min(start_x + dash_length, x2)
        pygame.draw.line(surface, color, (start_x, y1), (end_x, y1), width)


# Функция для отрисовки перекрестка слева
def draw_intersection():
    # Рисуем прямоугольник перекрестка
    intersection_rect = pygame.Rect(0, 0, INTERSECTION_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, INTERSECTION_COLOR, intersection_rect)
    # Рисуем рамку для перекрестка
    pygame.draw.rect(screen, (100, 100, 100), intersection_rect, 4)
    # Выводим надпись "Перекресток" внутри прямоугольника
    text = intersection_font.render("Перекресток", True, (0, 0, 0))
    text_rect = text.get_rect(center=(INTERSECTION_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)


def draw_arrow(screen, x, y, direction="left", length=125, arrow_size=60):
    """ Рисует стрелку с палкой (как дорожную разметку) """
    if direction == "left":
        line_start = (x + arrow_size, y)  # Начало линии
        line_end = (x + length, y)  # Конец линии
        arrow_points = [(x, y),
                        (x + arrow_size, y - arrow_size // 2),
                        (x + arrow_size, y + arrow_size // 2)]
    else:  # "right"
        line_start = (x + arrow_size, y)
        line_end = (x + length, y)
        arrow_points = [(line_end[0] + arrow_size, y),
                        (line_end[0], y - arrow_size // 2),
                        (line_end[0], y + arrow_size // 2)]

    pygame.draw.line(screen, (255, 255, 255), line_start, line_end, 20)  # Рисуем линию
    pygame.draw.polygon(screen, (255, 255, 255), arrow_points)  # Рисуем треугольник


if __name__ == "__main__":
    main()
