from django.urls import path
from .views import malware_file_upload

urlpatterns = [
    # ... другие URLы
    path('admin/malware-upload/', malware_file_upload, name='malware_file_upload'),
]