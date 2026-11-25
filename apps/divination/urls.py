from django.urls import path

from .views import (
    BaziView,
    HistoryView,
    HoroscopeView,
    TarotCardView,
    TarotView,
)

urlpatterns = [
    path("bazi/", BaziView.as_view(), name="divination-bazi"),
    path("horoscope/", HoroscopeView.as_view(), name="divination-horoscope"),
    path("tarot/", TarotView.as_view(), name="divination-tarot"),
    path("tarot/card/", TarotCardView.as_view(), name="divination-tarot-card"),
    path("history/", HistoryView.as_view(), name="divination-history"),
]
