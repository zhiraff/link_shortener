import os

from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse, FileResponse

from .models import ShortLink, UploadFile

from .forms import SingleURLForm, BatchProcessForm
from .utils.generators import generate_short_link
from .utils.excel_processor import process_excel
from .tasks import test_task

def index_view(request):
    """Главная страница"""
    t = test_task.delay()
    context = {
        'single_form': SingleURLForm(),
        'batch_form': BatchProcessForm(),
    }
    return render(request=request, template_name='shortener/index.html', context=context)


@require_POST
def shorten_single_view(request):
    """Обработка одиночной ссылки"""
    form = SingleURLForm(request.POST)
    
    if form.is_valid():

        original_url = form.cleaned_data['original_url']
        short_length = form.cleaned_data['short_length']
        use_digits = form.cleaned_data['use_digits']

        # Возьмём старую ссылку если есть, если нет то созхдадим новую
        short_tag = ShortLink.objects.get_or_create(
            full_link=original_url,
            defaults={'short_link': generate_short_link(use_numeric=use_digits, length=short_length),
                          }
        )
        short_url = f"{os.environ.get('DOMAIN')}/{short_tag[0]}"            
        
        return render(request, 'shortener/index.html', {
            'single_form': form,
            'short_url': short_url,
            'show_single_result': True,
            'qr_code_url': short_tag[0].qr_code.url,
            'clicks': short_tag[0].redirect_count,
            'created': "только что" if short_tag[1] else short_tag[0].created_at,
        })
    
    # Если форма не валидна
    
    return render(request, 'base.html', {
        'single_form': form,
        'batch_form': BatchProcessForm(),
    })


@require_POST
def process_batch_view(request):
    """Обработка Excel файла"""
    form = BatchProcessForm(request.POST, request.FILES)
    
    if form.is_valid():
        excel_file = form.cleaned_data['excel_file']
        batch_length = int(form.cleaned_data['batch_length'])
        use_digits = form.cleaned_data['batch_use_digits']

        short_tag = generate_short_link(use_numeric=use_digits, length=batch_length)
        upl_file = UploadFile.objects.create(
            id_link=short_tag,
            input_file=excel_file
        )

        # отправить файл на обработку в celery

        process_excel.delay(upl_file.pk, use_digits, batch_length)

        return render(request=request, template_name='shortener/index.html', 
        context={
            'batch_form': form,
            'show_batch_result': True,
            'batch_link': f"{os.environ.get('DOMAIN')}/f/{short_tag}"
            })
    
    # Если форма не валидна
    
    return render(request, 'base.html', {
        'single_form': SingleURLForm(),
        'batch_form': form,
    })


def resolve_slug_view(request, slug):
    try:
        short_record = ShortLink.objects.get(short_link=slug)
        short_record.redirect_count += 1
        short_record.save()
        return redirect(short_record.full_link)
    except:
        return render(request=request, template_name='shortener/error.html', context={"error_text": f"Ссылка { slug } не найдена в базе"})


def download_file_view(request, slug):
    try:
        upl_file = UploadFile.objects.get(id_link=slug)
        if upl_file.file_status == 'done' and upl_file.output_file.name:
            response = FileResponse(
                upl_file.output_file.open('rb'),
                as_attachment=True,
                filename=f"processed_{upl_file.output_file.name}"
            )
            return response
        else:
            return render(request=request, template_name='shortener/error.html', context={"error_text": f"Файл { slug } не найден или ещё не готов. Попробуйте позже!"})
    except:
        return render(request=request, template_name='shortener/error.html', context={"error_text": f"Файл { slug } не найден или ещё не готов. Попробуйте позже!"})