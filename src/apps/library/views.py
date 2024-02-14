from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render


def home_page_view(request: WSGIRequest):
    return render(request, 'library/index.html')
