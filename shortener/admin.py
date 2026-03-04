import os

from django.contrib import admin, messages
from django.utils.html import format_html
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.shortcuts import redirect

from blacklist.utils import is_black_host
from .models import ShortLink, UploadFile
from .utils.excel_processor import process_excel

url_validator = URLValidator()


class ShortLinkAdmin(admin.ModelAdmin):
    """Класс отображающий сокращённые ссылки в админке"""
    list_display = ["full_link", "host", "get_colour", "get_short_link", "get_qrcode", "redirect_count", "created_at", "updated_at"]
    list_display_links = ["full_link","host", "get_colour", "redirect_count", "created_at", "updated_at"]

    def get_colour(self, obj):
        return obj.colour
    get_colour.short_description = 'Цвет ссылки'

    def get_short_link(self, obj):
        domain = os.environ.get('DOMAIN')
        return format_html("<a target=blank href='{}/{}'>{}/{}</a>", domain, obj.short_link, domain, obj.short_link)
    get_short_link.short_description = 'Короткая ссылка'

    def get_qrcode(self, object):
        if object.qr_code.name:
            return format_html("<img src='{}' width=50>", object.qr_code.url)
        else:
            return "no image"
    get_qrcode.short_description = 'QR Код'

    fields = ("short_link", "full_link", "qr_code", "redirect_count", "created_at", "updated_at")
    readonly_fields = ("short_link", "qr_code", "redirect_count", "created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Фильтрация в зависимости от пользователя
        if request.user.is_superuser:
            return qs  # Суперпользователь видит всё
        else:
            return qs.filter(owner_user=request.user.username)
    
    def save_model(self, request, obj, form, change):
        # Автоматически заполняем owner_user перед сохранением
        obj.owner_user = request.user.username

        try:
            url_validator(obj.full_link)
        except ValidationError:
            messages.error(
                request, 
                f"Неверный url адрес: '{obj.full_link}'"
            )
            # Сохраняем флаг ошибки
            request._save_error = True
            # Возвращаем None и не вызываем super().save_model()
            return
        
        # Проверяем что хост не в чёрном списке

        is_black, reason_black = is_black_host(obj.full_link)

        if is_black:
            messages.error(
                request, 
                f"Не удалось сократить ссылку, хост находится в чёрном списке по причине: {reason_black}"
            )
            # Сохраняем флаг ошибки
            request._save_error = True
            # Возвращаем None и не вызываем super().save_model()
            return 
            
   
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        if getattr(request, '_save_error', False):
            # При ошибке редиректим на страницу списка
            return redirect('admin:shortener_shortlink_changelist')
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        if getattr(request, '_save_error', False):
            return redirect('admin:shortener_shortlink_changelist')
        return super().response_change(request, obj)
    
        
admin.site.register(ShortLink, ShortLinkAdmin)


class UploadFileAdmin(admin.ModelAdmin):
    """Класс отображающий файлы в админке"""
    list_display = ["id_link", "get_file_status", "get_input_file_link", "get_output_file_link", "task_id", "created_at", "updated_at"]
    list_display_links = ["id_link", "get_file_status", "created_at", "updated_at"]
    
  
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

    def get_input_file_link(self, obj):
        if obj.input_file.name:
            return format_html("<a href='{}' download class='badge text-bg-primary'>скачать</a>", obj.input_file.url)
        return 'no file'

    get_input_file_link.short_description = 'Скачать исходный файл'

    def get_output_file_link(self, obj):
        if obj.output_file.name:
            return format_html("<a href='{}' download class='badge text-bg-primary'>скачать</a>", obj.output_file.url)
        return 'no file'

    get_output_file_link.short_description = 'Скачать результирующий файл'

    fields = ("id_link", "file_status", "input_file", "output_file", "task_id", "created_at", "updated_at")
    readonly_fields = ("id_link", "file_status", "output_file", "task_id", "created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Фильтрация в зависимости от пользователя
        if request.user.is_superuser:
            return qs  # Суперпользователь видит всё
        else:
            return qs.filter(owner_user=request.user.username)

    
    def save_model(self, request, obj, form, change):
        # Автоматически заполняем owner_user перед сохранением
        obj.owner_user = request.user.username

        ext = obj.input_file.name.lower().split('.')[-1]

        if ext != "xlsx":
            messages.error(
                request, 
                f"Неверное расширение файла: '{ext}', должно быть xlsx"
            )
            # Сохраняем флаг ошибки
            request._save_error = True
            # Возвращаем None и не вызываем super().save_model()
            return
        super().save_model(request, obj, form, change)

        # вызовем celery для обработки

        process_excel.delay(obj.pk, request.user.username)
    
    def response_add(self, request, obj, post_url_continue=None):
        if getattr(request, '_save_error', False):
            # При ошибке редиректим на страницу списка
            return redirect('admin:shortener_uploadfile_changelist')
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        if getattr(request, '_save_error', False):
            return redirect('admin:shortener_uploadfile_changelist')
        return super().response_change(request, obj)


    class Media:
        css = {
            "all": ["css/status_styles.css"],
        }
    
        
admin.site.register(UploadFile, UploadFileAdmin)