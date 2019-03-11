from django.urls import path
from . import views

urlpatterns = [
   path('', views.main, name='main'),
   path('match/<int:no>', views.match, name='match'),
]
