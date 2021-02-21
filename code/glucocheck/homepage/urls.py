from django.urls import path

from .import views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('signup/', views.signup, name = 'signup'),
    path('login/', views.login, name = 'login'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
    

