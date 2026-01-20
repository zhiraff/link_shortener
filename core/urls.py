"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
import os

from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.views import serve
from django.views.static import serve as media_serve
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions

# Возможность выбирать схему (http/https) в сваггере
class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
    # url='https://192.168.1.8:8080/',
   public=True,
   generator_class=BothHttpAndHttpsSchemaGenerator,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/link/", include("shortener.urls_api")),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include('shortener.urls')),
]

# обработка статики и медиа
urlpatterns.append(path('static/<path:path>', serve, {'insecure': True}))

urlpatterns.append(path('media/<path:path>', media_serve, {'document_root': settings.MEDIA_ROOT}))

# страница сваггера и редок
# urlpatterns.append(path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),)
# urlpatterns.append(path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'))
# urlpatterns.append(path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'))

# немного кастомизации админки не помешает
admin.site.site_title = f"Сокращатель ссылок"
admin.site.site_header = f"Сокращатель ссылок"
admin.site.index_title = f"Сокращатель ссылок | Версия ПО: {os.getenv('version', '0.0.1')}"
