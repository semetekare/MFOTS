# Используем легковесную версию Python 3.11 с базовым образом Alpine Linux 3.18
FROM python:3.11.11-alpine3.21

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /ub

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Копируем только файл requirements.txt сначала, чтобы использовать кэш Docker
COPY requirements.txt .
RUN pip install --upgrade pip && python -m pip install -U channels["daphne"] && pip install --no-cache-dir -r requirements.txt

#RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories && apk update && apk add postgresql-client
run apk add postgresql-client

# Копируем остальной код приложения в текущую директорию в контейнере
COPY . .
# Копируем скрипт entrypoint.sh в текущую директорию в контейнере
#COPY script/entrypoint.sh .
RUN sed -i 's/\r$//g' script/entrypoint.sh

# Проверка прав до установки прав на выполнение
RUN ls -l script/entrypoint.sh

# Установка прав на выполнение скрипта
RUN chmod +x script/entrypoint.sh

# Проверка прав после установки прав на выполнение
RUN ls -l script/entrypoint.sh

ENTRYPOINT ["/bin/sh","/ub/script/entrypoint.sh"]

