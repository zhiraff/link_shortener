import ast
import uuid

from celery import current_task, shared_task

from .models import BlackHost, Reasons, UploadedFile
from shortener.utils.parsers import get_host_from_url


def is_black_host(url: str)->tuple[bool, str]:

    host = get_host_from_url(url)

    try:
        black_host = BlackHost.objects.select_related('reason').get(host=host)
        return True, black_host.reason
    except Exception as e:
        print(e)
        return False, ''


@shared_task
def update_blacklisst(uploaded_file_id: uuid, type_file: int=0)->None:
    """
    Загрузка доменов из файла в чёрный список
    type_file: тип файла: 0 - Питоновский список ['var1', 'var2', 'var3']; 
                          1 - просто список через запятую var1, var2, var3
    """
    # получим ID таски
    с_task = current_task

    try:
        # получим запись о файле
        upl_file = UploadedFile.objects.get(pk=uploaded_file_id)
        # сменим статус файлу
        upl_file.file_status = 'processing'

        if с_task:
            upl_file.task_id = с_task.request.id

        upl_file.save()
        count_h = upl_file.count_host
        added_h = upl_file.added_host

        my_list = []

        # f_reason = Reasons.objects.all(pk=7)
        with upl_file.input_file.open('r') as file:  # автоматически закроется после блока
            content = file.read()
            my_list = ast.literal_eval(content)
        
        # заполнение в таблицу
        for item in my_list:
            count_h += 1
            _, created = BlackHost.objects.get_or_create(host=item, reason=upl_file.reason)
            if created:
                added_h += 1

    except UploadedFile.DoesNotExist:
        print("файл для загрузки доменов не найден")
    
    except Exception as e:
        print(e)
        # сменим статус файлу
        upl_file.file_status = 'error'
        upl_file.save()
        raise
        # return
    
    upl_file.file_status = 'done'
    upl_file.count_host = count_h
    upl_file.added_host = added_h
    upl_file.save()

    print('ok')