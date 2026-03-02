from shortener.models import ShortLink

def host_to_black(host: str):
    # Добавляем хост в чёрный список
    ShortLink.objects.filter(host=host).update(colour='black')

def host_to_yellow(host: str):
    # Добавляем хост в жёлтый список
    ShortLink.objects.filter(host=host).update(colour='yellow')

def host_to_red(host: str):
    # Добавляем хост в красный список
    ShortLink.objects.filter(host=host).update(colour='red')

def host_to_green(host: str):
    # Добавляем хост в зелёный список
    ShortLink.objects.filter(host=host).update(colour='green')