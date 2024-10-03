from django.urls import path
from . import views

urlpatterns = [
    path('generate-playlist/', views.generate_playlist, name='generate_playlist'),
    path('about/', views.about, name='about')
]