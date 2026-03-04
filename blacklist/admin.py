from django.contrib import admin

from .models import Reasons, BlackHost


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
