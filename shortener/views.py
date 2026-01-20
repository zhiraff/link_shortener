import os

from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse, FileResponse
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import generics, status

from .models import ShortLink, UploadFile

from .forms import SingleURLForm, BatchProcessForm
from .utils.generators import generate_short_link
from .utils.excel_processor import process_excel

from .serializers import LinkSerializer


def index_view(request):
    """Главная страница"""

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



class CreateSingleLinkView(generics.GenericAPIView):
    serializer_class = LinkSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.validate(request.data)
        if serializer.is_valid():
            # serializer.data['password1']
            # Возьмём старую ссылку если есть, если нет то созхдадим новую
            short_tag = ShortLink.objects.get_or_create(
            full_link=serializer.data['link'],
            defaults={'short_link': generate_short_link(use_numeric=serializer.data['use_numeric'], length=serializer.data['length']),
                          }
        )
        short_url = f"{os.environ.get('DOMAIN')}/{short_tag[0]}" 
        #print("11111111111")
        #print(*args)
        #print(**kwargs)
        #print(request.data)
        #version = os.getenv('version', "TEST BUILD 0.1")
        return JsonResponse({'short_link': short_url}, status=status.HTTP_200_OK)


class GetSingleLinkView(generics.GenericAPIView):
    # serializer_class = LinkSerializer

    def get(self, request, *args, **kwargs):
        try:
            slug = kwargs.get('slug')
            short_record = ShortLink.objects.get(short_link=slug)
            short_record.redirect_count += 1
            short_record.save()
            return JsonResponse({'original_link': short_record.full_link}, status=status.HTTP_200_OK)
        except:
            return JsonResponse({'error': "No link found"}, status=status.HTTP_404_NOT_FOUND)
