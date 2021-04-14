"""glucocheck URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from django.urls import path, include

from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from rest_framework.permissions import AllowAny
from django.views.generic import TemplateView
#from rest_framework.authtoken.views  import obtain_auth_token
from rest_framework.authtoken import views
urlpatterns = [
    path('', include('homepage.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
    path('documentation/',include_docs_urls(title="API Documentation", public=True,permission_classes=[AllowAny, ])),
    path('schema',get_schema_view(
        title="API documentation",
        description="API",
        version="1.0.0",
        public=True),
        name="openapi-schema" ),
        
]


