from django.urls import path

from .views import LeaderboardView, ScoreSubmitView

urlpatterns = [
    path("score/", ScoreSubmitView.as_view(), name="game-score"),
    path("leaderboard/", LeaderboardView.as_view(), name="game-leaderboard"),
]
