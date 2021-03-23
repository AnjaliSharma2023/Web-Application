from django.urls import path

from .import views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('signup/', views.signup, name = 'signup'),
    path('login/', views.login, name = 'login'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('email-input/', views.email_input, name='email_input'),
    path('tnc/', views.tnc, name='tnc'),
    path('test/', views.test, name='test'),
    path('test-data/', views.test_data, name='test_data'),
    path('glucose-input/', views.glucose_input, name='glucose_input'),
    path('carbs-input/', views.carbs_input, name='carbs_input'),
    path('insulin-input/', views.insulin_input, name='insulin_input'),
    path('profile-page/', views.profile_page, name='profile_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
]
  
