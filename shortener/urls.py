from django.urls import path
from .views import index_view, shorten_single_view, process_batch_view, resolve_slug_view, download_file_view

urlpatterns = [
    path('', index_view, name='index'),
    path('shorten_single/', shorten_single_view, name='shorten_single'),
    path('process_batch/', process_batch_view, name='process_batch'),
    path('f/<slug:slug>/', download_file_view, name='download_file'),
    path('<slug:slug>/', resolve_slug_view, name='resolve_slug'),
]