from io import BytesIO
import pandas as pd
from django.core.files.base import ContentFile
import re
from urllib.parse import urlparse
import os

from celery import current_task, shared_task


from shortener.models import ShortLink, UploadFile
from .generators import generate_short_link


@shared_task
def process_excel(_id: str, use_numeric: bool=True, length: int=6) -> None:
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
    
    # Функция для проверки URL
    def is_valid_url(text):
        if not isinstance(text, str):
            return False
        
        # Простая проверка URL
        url_pattern = re.compile(
            r'^(https?://)?'  # протокол
            r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'  # домен
            r'(:[0-9]+)?'  # порт
            r'(/[^\s]*)?$'  # путь
        )
        
        try:
            result = urlparse(text)
            # Проверяем, что есть домен
            return all([result.scheme in ['http', 'https', ''], 
                       result.netloc or (result.path and '.' in result.path)])
        except:
            return False
    
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
            
        # Проверяем, является ли значение URL
        if is_valid_url(str(cell_value)):
            url = str(cell_value)

            # Возьмём старую ссылку если есть, если нет то созхдадим новую
            short_tag = ShortLink.objects.get_or_create(
            full_link=url,
            defaults={'short_link': generate_short_link(use_numeric=use_numeric, length=length),
                          }
            )
            short_url = f"{os.environ.get('DOMAIN')}/{short_tag[0]}"

            # Добавляем укороченную ссылку
            df.iat[idx, status_col] = short_url

            # Добавляем ссылку на QR-код
            df.iat[idx, qr_col] = f"{os.environ.get('DOMAIN')}{short_tag[0].qr_code.url}" 

        else:
            # Если не URL, ставим пустые значения
            df.iat[idx, status_col] = ""
            df.iat[idx, qr_col] = ""
    
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
