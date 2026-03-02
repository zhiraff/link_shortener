from .models import BlackHost
from shortener.utils.parsers import get_host_from_url


def is_black_host(url: str)->tuple[bool, str]:

    host = get_host_from_url(url)

    try:
        black_host = BlackHost.objects.select_related('reason').get(host=host)
        return True, black_host.reason
    except Exception as e:
        print(e)
        return False, ''