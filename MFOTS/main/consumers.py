from channels.generic.websocket import WebsocketConsumer
import json

class TestConsumer(WebsocketConsumer):
    def connect(self):
        # Вызывается при подключении клиента
        self.accept()  # Принимаем соединение
        self.send(text_data=json.dumps({
            'message': 'WebSocket подключен!'
        }))

    def disconnect(self, close_code):
        # Вызывается при отключении клиента
        pass

    def receive(self, text_data):
        # Вызывается при получении сообщения от клиента
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Отправляем сообщение обратно клиенту
        self.send(text_data=json.dumps({
            'message': f'Эхо: {message}'
        }))