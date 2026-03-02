from io import BytesIO
import pandas as pd
from django.core.files.base import ContentFile
import re
from urllib.parse import urlparse
import os

from celery import current_task, shared_task


from shortener.models import ShortLink, UploadFile
from .generators import generate_short_link
from .create_short_link import create_short_link


@shared_task
def process_excel(_id: str, usr_name: str="Anonymous") -> None:
    """
    Обрабатывает Excel файл, ищет URL и добавляет укороченные url и ссылку на qr, сохраняет как новый файл и добавляет его к модели.
    
    """

    # получим ID таски
    с_task = current_task

    # получим запись о файле

    upl_file = UploadFile.objects.get(pk=_id)
    
    # сменим статус файлу
    upl_file.file_status = 'processing'

    if с_task:
        upl_file.task_id = с_task.request.id

    upl_file.save()

    # Открываем файл из модели
    excel_file = upl_file.input_file
    
    # Загружаем Excel файл
    try:
        df = pd.read_excel(excel_file.open('rb'), header=None)
    except Exception as e:
        raise ValueError(f"Ошибка чтения Excel файла: {e}")
    
    # Определяем, в каком столбце искать URL (первый непустой)
    url_column_index = None
    for col in range(df.shape[1]):
        if not df[col].isna().all():  # Если столбец не полностью пустой
            url_column_index = col
            break
    
    if url_column_index is None:
        upl_file.file_status = 'error'
        upl_file.save()
        raise ValueError("В файле нет данных")
    
    print(f"Ищем URL в столбце {url_column_index}")
    
    # Создаем колонки для результатов если их нет
    status_col = url_column_index + 1
    qr_col = url_column_index + 2
    
    # Добавляем заголовки если нужно
    if df.shape[1] <= status_col:
        for i in range(df.shape[1], qr_col + 1):
            df[i] = None
    
    # Проходим по строкам
    for idx in range(len(df)):
        cell_value = df.iat[idx, url_column_index]
        
        if pd.isna(cell_value):
            continue
        
        result = create_short_link(str(cell_value))

        if result[0] != 200:
            df.iat[idx, status_col] = result[1]
            df.iat[idx, qr_col] = ""
        else:
            short_tag, tag_created = result[1]

        # Добавляем укороченную ссылку
            df.iat[idx, status_col] = f"{os.environ.get('DOMAIN')}/{short_tag}"
        
        # Добавляем ссылку на QR-код
            df.iat[idx, qr_col] = f"{os.environ.get('DOMAIN')}{short_tag.qr_code.url}" 
            
    # Сохраняем результат в BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, header=False)
    
    output.seek(0)
    # Сохраняем байты в файл
    try:
        original_name = upl_file.input_file.name
        processed_name = f"processed_{original_name}"
        upl_file.output_file.save(
                processed_name,
                ContentFile(output.getvalue()),
                save=True
            )
        upl_file.file_status = "done"
        upl_file.save()
        return True
    except:
        upl_file.file_status ="error"
        upl_file.save()
        return False
