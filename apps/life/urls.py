# apps/life/urls.py
from django.urls import path
from .views import WeatherView

urlpatterns = [
    path("weather/", WeatherView.as_view(), name="life-weather"),
]
