from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from .processes import channelgroupname

class MatchMoveConsumer(JsonWebsocketConsumer):
    def connect(self):
        matchno = self.scope['url_route']['kwargs']['no']
        self.channelgroup_name = channelgroupname(matchno)
        async_to_sync(self.channel_layer.group_add)(
            self.channelgroup_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.channelgroup_name,
            self.channel_name
        )

    def notify_move(self, event):
        player = event['player']
        if self.scope['user'].username == player:
            return
        content = {
            'event': 'move',
            'player': player,
        }
        self.send_json(content)
