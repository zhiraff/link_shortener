from django.urls import path
from .views import index_view, resolve_slug_view, download_file_view


app_name = "shortener"

urlpatterns = [
    path('', index_view, name='index'),
    path('f/<slug:slug>/', download_file_view, name='download_file'),
    path('<slug:slug>/', resolve_slug_view, name='resolve_slug'),
]