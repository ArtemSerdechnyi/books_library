from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.AccountView.as_view(), name='user_account'),
]