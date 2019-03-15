from django.urls import path
from . import views

urlpatterns = [
   path('', views.main, name='main'),
   path('match/new', views.newmatch, name='new_match'),
   path('match/<int:no>', views.match, name='match'),
   path('match/<int:no>/attack', views.attack, name='match_attack'),
   path('match/<int:no>/refill', views.refill, name='match_refill'),
]
