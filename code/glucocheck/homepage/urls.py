from django.urls import path

from .import views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('signup/', views.signup, name = 'signup'),
    path('login/', views.login, name = 'login'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('reset-password-email/', views.reset_password_email, name='reset_password_email'),
    path('tnc/', views.tnc, name='tnc'),
]
    

