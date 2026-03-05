from django.contrib import admin
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import redirect
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html

from .models import Reasons, BlackHost, UploadedFile
from .views import malware_file_upload

class BlackHostAdmin(admin.ModelAdmin):
    """Класс отображающий чёрный список url в админке"""
    list_display = ["host", "reason", "created_at", "updated_at"]
    list_display_links = ["host","reason", "created_at", "updated_at"]

    fields = ("host", "reason", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    search_fields = ['host']

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
        
    #     # Фильтрация в зависимости от пользователя
    #     if request.user.is_superuser:
    #         return qs  # Суперпользователь видит всё
    #     else:
    #         return qs.filter(owner_user=request.user.username)
        
        
admin.site.register(BlackHost, BlackHostAdmin)

admin.site.register(Reasons)

class UploadedFileAdmin(admin.ModelAdmin):
    """Класс отображающий загруженные файлы с плохими хостами в админке"""
    list_display = ["input_file", "get_file_status", "reason", "count_host", "added_host", "owner_user", "created_at", "updated_at"]
    list_display_links = ["input_file", "get_file_status", "reason", "count_host", "added_host", "owner_user", "created_at", "updated_at"]

    fields = ("input_file", "reason", "file_status", "owner_user", "task_id", "created_at", "updated_at")
    readonly_fields = ("file_status", "owner_user", "task_id", "created_at", "updated_at")

    def get_file_status(self, obj):
        if obj.file_status == 'created':
            return format_html("<span download class='badge text-bg-primary'>{}</span>", obj.get_file_status_display())
        elif obj.file_status == 'processing':
            return format_html("<span download class='badge text-bg-warning'>{}</span>", obj.get_file_status_display())
        elif obj.file_status == 'done':
            return format_html("<span download class='badge text-bg-success'>{}</span>", obj.get_file_status_display())
        elif obj.file_status == 'error':
            return format_html("<span download class='badge text-bg-danger'>{}</span>", obj.get_file_status_display())
        else:
            return format_html("<span download class='badge text-bg-secondary'>{}</span>", obj.get_file_status_display())

    get_file_status.short_description = 'Статус файла'

    def get_urls(self):
        
        urls = super().get_urls()
        custom_urls = [
            path('malware-upload/', self.admin_site.admin_view(self.custom_upload_view), name='malware_file_upload'),
        ]
        return custom_urls + urls
    
    def custom_upload_view(self, request):
        # Этот метод будет обрабатывать запросы к /admin/app/model/custom-upload/
        if request.method == 'POST' and request.FILES.get('uploaded_file'):
            # Здесь ваша обработка файла
            # вызовем функцию из views.py чем написать логику здесь
                        
            return malware_file_upload(request)
        
        return render(request, 'admin/custom_file_upload.html', {
            'title': 'Загрузка файла',
            'opts': self.model._meta,
        })
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_upload_url'] = reverse('admin:malware_file_upload')
        return super().changelist_view(request, extra_context=extra_context)
    
    class Media:
        css = {
            "all": ["css/status_styles.css"],
        }

admin.site.register(UploadedFile, UploadedFileAdmin)