from django.urls import path

from .import views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('signup/', views.signup, name = 'signup'),
    path('login/', views.login, name = 'login'),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    #path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    #path('activate/(?P<uidb64>[-a-zA-Z0-9_]+)/(?P<token>[-a-zA-Z0-9_]+)/$',
     #  views.activate, name='activate'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
]
    

