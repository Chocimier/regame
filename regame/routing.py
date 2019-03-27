from django.urls import path

from .consumers import MatchMoveConsumer

websocket_urlpatterns = [
    path('ws/match/<int:no>', MatchMoveConsumer, name='match_notifications'),
]
