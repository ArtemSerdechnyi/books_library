from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('', views.Account.as_view(), name='user_account'),
]