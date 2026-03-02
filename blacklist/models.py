from django.db import models
from shortener.utils.manage_colour_host import host_to_black#, host_to_yellow, host_to_red, host_to_green

__all__ = ['Reasons', 'BlackHost']

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

