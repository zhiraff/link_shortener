from django.core.validators import URLValidator

from blacklist.utils import is_black_host
from shortener.models import ShortLink
from .generators import generate_short_link
from django.core.exceptions import ValidationError

url_validator = URLValidator()

def create_short_link(original_url: str, usr_name: str='Anonymous')->tuple[int, str | tuple[ShortLink, bool]]:
    if not original_url:
        return 400, "Не передан URL."

    # валидируем что это норм ссылка
    try:
        url_validator(original_url)
    except ValidationError:
        return 400, "Некорректный URL."
    
    # Проверяем что хост не в чёрном списке
    is_black, reason_black = is_black_host(original_url)
    if is_black:
        return 400, f"Не удалось сократить ссылку, хост находится в чёрном списке по причине: {reason_black}"
    
    # Возьмём старую ссылку если есть, если нет то создадим новую
    short_tag, tag_created = ShortLink.objects.get_or_create(
    full_link=original_url,
    owner_user=usr_name,
    defaults={'short_link': generate_short_link(),
                    }
                        )
    return 200, (short_tag, tag_created)