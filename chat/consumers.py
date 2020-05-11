# chat/consumers.py

from asgiref.sync import async_to_sync

from channels.generic.websocket import WebsocketConsumer
import json

import time


class ChatConsumer(WebsocketConsumer):
    # websocket 연결 시 실행
    def connect(self):
      	# chat/routing.py 에 있는
        # url(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
        # 에서 room_name 을 가져옵니다.
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # 그룹에 join
        # send 등 과 같은 동기적인 함수를 비동기적으로 사용하기 위해서는 async_to_sync 로 감싸줘야한다.
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # WebSocket 연결
        self.accept()

    # websocket 연결 종료 시 실행
    def disconnect(self, close_code):
        # 그룹에서 Leave
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # 클라이언트로부터 메세지를 받을 시 실행
    # def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']

    #     print("message=",end=""), print(message)

    #     self.send(text_data=json.dumps({
    #         'message': message
    #     }))

    # WebSocket 에게 메세지 receive
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print("received msg = ",end=""), print(message)

        # room group 에게 메세지 send
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # room group 에서 메세지 receive
    def chat_message(self, event):
        message = event['message']
        print("event msg = ",end=""), print(message)
        # WebSocket 에게 메세지 전송
        # self.send(text_data=json.dumps({
        #     'message': message
        # }))

        i = 0
        while i < 10:
            self.send(text_data=json.dumps({
                'message': message
            }))
            
            i+= 1

            time.sleep(1)

