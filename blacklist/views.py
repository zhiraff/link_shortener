from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.urls import reverse

from .models import UploadedFile, Reasons
from .utils import update_blacklisst


@permission_required('blacklist.add_uploadedfile')
def malware_file_upload(request):
    """
    view для загрузки списка хостов, которые являюся malware
    Загружается файл .txt в котором хосты перечислены как в списке: ['host1', 'host2', 'host3']
    обязательно скобки и ковычки
    """
    if request.method == 'POST' and request.FILES.get('uploaded_file'):
        uploaded_file = request.FILES['uploaded_file']
        
        # uploaded_file содержит загруженный файл
        # Можно прочитать содержимое: uploaded_file.read()
        # Или сохранить временно: uploaded_file.temporary_file_path()
        
        # Пример: чтение содержимого как текст
        # file_content = uploaded_file.read().decode('utf-8')

        # найдём причину malware
        malware_reason = Reasons.objects.filter(reason_description__icontains='malware')[0]

        #запишем файл в таблицу
        upl_file = UploadedFile.objects.create(owner_user=request.user, 
                                                input_file=uploaded_file,
                                                reason=malware_reason)

        # отправить файл на обработку в celery

        update_blacklisst.delay(upl_file.id)
        
        messages.success(request, f'Файл {uploaded_file.name} успешно загружен и отправлен в обработку')
        return redirect('admin:index')
    
    return render(request, 'admin/custom_file_upload.html')
