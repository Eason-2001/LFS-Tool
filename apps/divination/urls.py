from django.urls import path

from .views import BaziView, HistoryView, HoroscopeView

urlpatterns = [
    path("bazi/", BaziView.as_view(), name="divination-bazi"),
    path("horoscope/", HoroscopeView.as_view(), name="divination-horoscope"),
    path("history/", HistoryView.as_view(), name="divination-history"),
]
