from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),



    # site paths
    path('', views.home_page_view, name='home'),
]
