from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
from .forms import CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    """Класс отображающий пользователей в админке"""
    model = CustomUser
    add_form = CustomUserCreationForm

    add_fieldsets = (
       (None, {
        'classes': ('wide,'),
        'fields': ('username', 'email', 'password1', 'password2', 'is_staff')
       }), 
    )

    fieldsets = (
        ('Персональная информация',
         {
             'fields': (
                 'last_name',
                 'first_name',
             )
         }),
        (
            'Служебная информация',
            {
                'fields': (
                    'password',
                    'username',
                    'email',
                    'is_active',
                    'is_staff',
                    'groups',
                    'date_joined',
                    'last_login'
                )
            },
        ),
    )
    readonly_fields = ['last_login', 'date_joined']

    list_display = ["username", "email", "is_active", "is_staff", "is_superuser"]
    list_display_links = ["username", "email"]


admin.site.register(CustomUser, CustomUserAdmin)
