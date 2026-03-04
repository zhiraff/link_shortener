from django.contrib.auth.models import Group
from django.conf import settings

def add_to_guest_group_and_staff(backend, user, response, *args, **kwargs):
    """
    Добавляет нового пользователя в группу 'Гости' и устанавливает is_staff=True
    """
    # Проверяем, что пользователь был только что создан
    # kwargs содержит параметры, включая 'is_new'
    if kwargs.get('is_new'):
        try:
            # Получаем или создаем группу "Гости"
            guest_group, created = Group.objects.get_or_create(name=settings.GUEST_GROUP)
            
            # Добавляем пользователя в группу
            user.groups.add(guest_group)
            
            # Устанавливаем is_staff
            user.is_staff = True
            
            # Сохраняем изменения
            user.save()

            # Дополнительная логика в зависимости от провайдера
            # provider = backend.name
            # if provider == 'vk':
            #     # Сохраняем ID VK, если нужно
            #     user.vk_id = response.get('id')
            # elif provider == 'google':
            #     # Сохраняем дополнительную информацию от Google
            #     user.google_picture = response.get('picture')
            # elif provider == 'github':
            #     # Логика для GitHub
            #     user.github_login = response.get('login')
            
            print(f"Пользователь {user.username} добавлен в группу 'Гости' и получил is_staff=True")
            
        except Exception as e:
            # Логируем ошибку, но не прерываем процесс аутентификации
            print(f"Ошибка при добавлении пользователя в группу: {e}")
    
    # Важно: функция должна возвращать словарь или None
    return None