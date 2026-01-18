from django.contrib import admin
from django.utils.html import format_html

from .models import ShortLink, UploadFile

class ShortLinkAdmin(admin.ModelAdmin):
    """Класс отображающий сокращённые ссылки в админке"""
    list_display = ["short_link", "full_link", "get_qrcode", "redirect_count", "created_at", "updated_at"]
    list_display_links = ["short_link", "full_link", "redirect_count", "created_at", "updated_at"]

    def get_qrcode(self, object):
        if object.qr_code.name:
            return format_html(f"<img src='{object.qr_code.url}' width=50")
        else:
            return "no image"
    get_qrcode.short_description = 'QR Код'

    fields = ("short_link", "full_link", "qr_code", "redirect_count", "created_at", "updated_at")
    readonly_fields = ("short_link", "qr_code", "redirect_count", "created_at", "updated_at")
    
        
admin.site.register(ShortLink, ShortLinkAdmin)


class UploadFileAdmin(admin.ModelAdmin):
    """Класс отображающий файлы в админке"""
    list_display = ["id_link", "get_file_status", "get_input_file_link", "get_output_file_link", "task_id", "created_at", "updated_at"]
    list_display_links = ["id_link", "get_file_status", "created_at", "updated_at"]
    
  
    def get_file_status(self, obj):
        if obj.file_status == 'created':
            return format_html(f"<span download class='badge text-bg-primary'>{obj.get_file_status_display()}</span>")
        elif obj.file_status == 'processing':
            return format_html(f"<span download class='badge text-bg-warning'>{obj.get_file_status_display()}</span>")
        elif obj.file_status == 'done':
            return format_html(f"<span download class='badge text-bg-success'>{obj.get_file_status_display()}</span>")
        elif obj.file_status == 'error':
            return format_html(f"<span download class='badge text-bg-danger'>{obj.get_file_status_display()}</span>")
        else:
            return format_html(f"<span download class='badge text-bg-secondary'>{obj.get_file_status_display()}</span>")

    get_file_status.short_description = 'Статус файла'

    def get_input_file_link(self, obj):
        if obj.input_file.name:
            return format_html(f"<a href='{obj.input_file.url}' download class='badge text-bg-primary'>скачать</a>")
        return 'no file'

    get_input_file_link.short_description = 'Скачать исходный файл'

    def get_output_file_link(self, obj):
        if obj.output_file.name:
            return format_html(f"<a href='{obj.output_file.url}' download class='badge text-bg-primary'>скачать</a>")
        return 'no file'

    get_output_file_link.short_description = 'Скачать результирующий файл'

    fields = ("id_link", "file_status", "input_file", "output_file", "task_id", "created_at", "updated_at")
    readonly_fields = ("id_link", "task_id", "created_at", "updated_at")

    class Media:
        css = {
            "all": ["css/status_styles.css"],
        }
    
        
admin.site.register(UploadFile, UploadFileAdmin)