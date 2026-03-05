import uuid

from django.db import models
from django.core.validators import FileExtensionValidator

from shortener.utils.manage_colour_host import host_to_black#, host_to_yellow, host_to_red, host_to_green
from shortener.enums import host_colour, file_statuses


__all__ = ['Reasons', 'BlackHost', 'UploadedFile']

class Reasons(models.Model):
    """Причины добавления хоста в чёрный список"""
    id = models.BigAutoField(primary_key=True)
    reason_description = models.CharField(max_length=100, verbose_name="Описание причины попадания в чёрный список")
    def __str__(self):
        return f"{self.reason_description[:50]}"

    class Meta:
        verbose_name = "Причина"
        verbose_name_plural = "Причины"


class BlackHost(models.Model):
    """Запрещённые хосты"""

    host = models.CharField(
        primary_key=True, 
        max_length=256, 
        verbose_name="Хост", 
        editable=True, 
        unique=True)
    # host = models.CharField(max_length=256, verbose_name="Хост", unique=True, db_index=True)
    reason = models.ForeignKey(Reasons, on_delete=models.SET_NULL, blank=True, null=True,
                             verbose_name="Причина")
    created_at = models.DateTimeField(verbose_name="Дата попадания в ЧС", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата изменения записи", auto_now=True)
    
    def __str__(self):
        return f"{self.host}"
    
    def save(self, *args, **kwargs):
        host_to_black(self.host)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Запрещённый домен'
        verbose_name_plural = 'Запрещённые домены'


class UploadedFile(models.Model):
    """Загруженные файлы с доменами"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner_user = models.CharField(max_length=256, verbose_name="Создано пользователем", default="Anonymous")
    file_status = models.CharField(max_length=100, verbose_name='Статус файла', choices=file_statuses, default='created')
    input_file = models.FileField(upload_to="host_list_files/%Y", max_length=150, verbose_name="Файл для обработки",
                            validators=[FileExtensionValidator(allowed_extensions=['txt'])]
                            )
    reason = models.ForeignKey(Reasons, on_delete=models.SET_NULL, blank=True, null=True,
                             verbose_name="Группа хостов")
    count_host = models.IntegerField(verbose_name='Распознано хостов', default=0)
    added_host = models.IntegerField(verbose_name='Хостов добавлено', default=0)
    task_id = models.CharField(max_length=255, null=True, blank=True)                  
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)
    
    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Файл список доменов'
        verbose_name_plural = 'Файлы списков доменов'
