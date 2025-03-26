import pygame
import time
import json
from datetime import datetime

# Инициализация Pygame
pygame.init()

# Константы для экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (255, 255, 255)  # Белый фон

# Цвета объектов
RED_COLOR = (255, 0, 0)
GREEN_COLOR = (0, 255, 0)
BLUE_COLOR = (0, 0, 255)

# Установки экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Перекресток")


# Пример объекта
class Vehicle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, 40, 20))


# Функция для преобразования строки времени в datetime
def parse_time(time_str):
    return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")


# Функция для чтения объектов из JSON-файла
def read_objects_from_json(filename):
    vehicles = []
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            for obj in data['objects']:
                for row_data in obj['rows_data']:
                    x = int(row_data['point_x'])
                    y = int(row_data['point_y'])
                    color = "blue"  # Пример: просто указываем цвет как "blue"
                    if color == "red":
                        color = RED_COLOR
                    elif color == "green":
                        color = GREEN_COLOR
                    elif color == "blue":
                        color = BLUE_COLOR
                    vehicles.append(Vehicle(x, y, color))
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
    except json.JSONDecodeError:
        print(f"Ошибка чтения JSON в файле {filename}.")
    return vehicles


# Основной цикл программы
def main():
    clock = pygame.time.Clock()
    running = True
    filename = 'JSON\Олимпийский20_03_2025_17_35.json'  # Имя JSON-файла

    while running:
        screen.fill(BACKGROUND_COLOR)

        # Чтение объектов из JSON-файла каждую секунду
        vehicles = read_objects_from_json(filename)

        for vehicle in vehicles:
            vehicle.draw()

        pygame.display.update()

        # Ожидание 1 секунду
        time.sleep(1)

        # Проверка на закрытие окна
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(60)  # Ограничение кадров в секунду

    pygame.quit()


if __name__ == "__main__":
    main()
