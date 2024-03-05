from datetime import datetime
from django.utils import timezone
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.db.models import Count, Q

import plotly.express as px

from .utils import render_genre_statistic_view


def home_page_view(request: WSGIRequest):
    return render(request, 'statistic/statistic.html')


def genres_statistic_view(request: WSGIRequest):
    return render_genre_statistic_view(request, 'statistic/genres_statistic.html')


def fig_genres_statistic_view(request: WSGIRequest):
    return render_genre_statistic_view(request, 'statistic/fig_genres_statistic.html')
