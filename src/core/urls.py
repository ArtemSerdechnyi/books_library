from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),

    # site paths
    path('account/', include('apps.account.urls', namespace='account')),
    path('', include('apps.library.urls', namespace='library')),
]
