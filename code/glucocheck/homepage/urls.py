from django.urls import path
from .import views
from rest_framework.authtoken import views as authviews



urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('signup/', views.signup, name = 'signup'),
    path('login/', views.login, name = 'login'),
    path('logout-request/', views.logout_request, name = 'logout_request'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('email-input/', views.email_input, name='email_input'),
    path('tnc/', views.tnc, name='tnc'),
    path('glucose-input/', views.glucose_input, name='glucose_input'),
    path('carbs-input/', views.carbs_input, name='carbs_input'),
    path('insulin-input/', views.insulin_input, name='insulin_input'),
    path('profile-page/', views.profile_page, name='profile_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard-data/<start_date>/<end_date>/', views.dashboard_data, name='dashboard_data'),   
    path('api-glucose/', views.GlucoseView.as_view(), name='GlucoseView'),
    path('api-carbs/', views.CarbsView.as_view(), name='CarbsView'),
    path('api-insulin/', views.InsulinAPIView.as_view(), name='InsulinAPIView'),
    path('analytics-data/<start_date>/<end_date>/', views.analytics_data, name='analytics_data'),
    path('analytics', views.analytics, name='analytics'),
    path('glossary/', views.glossary, name='glossary'),
    path('analytics-trend-data/<day>/<glucose_bool>/', views.analytics_trend_data, name='analytics_trend_data'),
]
