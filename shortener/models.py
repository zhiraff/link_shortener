import os

from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.files.base import ContentFile

from .utils.generators import generate_short_link, generate_qr_svg

__all__ = ['ShortLink', 'UploadFile']

class ShortLink(models.Model):
    """Укороченные ссылки"""
    short_link = models.CharField(
        primary_key=True, 
        max_length=20, 
        verbose_name="Сокращённая ссылка", 
        default=generate_short_link, 
        editable=False, 
        unique=True)
    owner_user = models.CharField(max_length=256, verbose_name="Создано пользователем", default="Anonymous")
    full_link = models.CharField(max_length=512, verbose_name="Полная ссылка", db_index=True)
    qr_code = models.ImageField(upload_to="qr_codes/%Y", max_length=150, verbose_name="QR-код", null=True, blank=True)
    redirect_count = models.IntegerField(verbose_name='Количество переходов', default=0)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)
    
    def __str__(self):
        return f"{self.short_link}"
    
    def save(self, *args, **kwargs):
        # Генерируем QR-код при создании записи
        if not self.pk or self._state.adding:
            qr_code = generate_qr_svg(data=f"{os.environ.get('DOMAIN')}/{self.short_link}")
            filename = f'qr_{self.short_link}.png'
            self.qr_code.save(filename, ContentFile(qr_code.getvalue()), save=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Укороченная ссылка'
        verbose_name_plural = 'Укороченные ссылки'
        unique_together = ['full_link', 'owner_user']


class UploadFile(models.Model):
    """Загруженные файлы с ссылками"""
    statuses = (
        ('created', 'Создано'),
        ('processing', 'Обработка'),
        ('done', 'Обработано'),
        ('error', 'Ошибка'),
    )
    id_link = models.CharField(
        primary_key=True, 
        max_length=20, 
        verbose_name="ID файла",
        default=generate_short_link, 
        editable=False, 
        unique=True
        )
    owner_user = models.CharField(max_length=256, verbose_name="Создано пользователем", default="Anonymous")
    file_status = models.CharField(max_length=100, verbose_name='Статус файла', choices=statuses, default='created')
    input_file = models.FileField(upload_to="input_files/%Y", max_length=150, verbose_name="Файл для обработки",
                            validators=[FileExtensionValidator(allowed_extensions=['xlsx'])]
                            )
    output_file = models.FileField(upload_to="output_files/%Y", max_length=150, verbose_name="Файл для скачивания",
                            validators=[FileExtensionValidator(allowed_extensions=['xlsx'])],
                            null=True, blank=True
                            )
    task_id = models.CharField(max_length=255, null=True, blank=True)                  
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)
    
    def __str__(self):
        return f"{self.id_link}"

    class Meta:
        verbose_name = 'Файл с ссылками'
        verbose_name_plural = 'Файлы со ссылками'
