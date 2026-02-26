import os

from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse, FileResponse, HttpRequest
from rest_framework.views import APIView
from rest_framework import generics, status
from django.core.validators import URLValidator
from django.urls import reverse
from django.core.exceptions import ValidationError

from .models import ShortLink, UploadFile

from .forms import SingleURLForm, BatchProcessForm
from .utils.generators import generate_short_link
from .utils.excel_processor import process_excel

from .serializers import LinkSerializer


def _is_ajax(request: HttpRequest) -> bool:
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

url_validator = URLValidator()

def index_view(request):
    """Главная страница

    Обрабатывает:
    - GET, POST, Other: отдаёт страницу с формами.
    - POST + AJAX + поле url: сокращение одной ссылки.
    - POST + AJAX + файл xlsx_file: пакетная обработка XLSX.
    """
    
    if request.method == "POST" and _is_ajax(request):
        # user
        usr_name = "Anonymous" if request.user.is_anonymous else request.user.username

        if "xlsx_file" in request.FILES:
            # отправили файл
            # получим файл из формы
            uploaded = request.FILES.get("xlsx_file")

            # проверка что файл есть
            if not uploaded:
                return JsonResponse({"error": "Файл не передан."}, status=400)

            # првоерка что он xlsx
            if not uploaded.name.lower().endswith(".xlsx"):
                return JsonResponse({"error": "Нужен файл в формате .xlsx."}, status=400)
            
            # создадим тэг
            short_tag = generate_short_link()

            # сохраним файл исходный
            upl_file = UploadFile.objects.create(
            id_link=short_tag,
            input_file=uploaded,
            owner_user=usr_name,
            )

            # отправить файл на обработку в celery

            process_excel.delay(upl_file.pk, usr_name)

            # сгененрируем ссылку на скачивание файла
            download_url = request.build_absolute_uri(
                reverse("shortener:download_file", args=[short_tag])
            )

            return JsonResponse({"download_url": download_url})

        else:
            # отправили форму с ссылкой
            # получим данные из AJAX запроса
            original_url = (request.POST.get("url") or "").strip()
            if not original_url:
                return JsonResponse({"error": "Не передан URL."}, status=400)

            # валидируем что это норм ссылка
            try:
                url_validator(original_url)
            except ValidationError:
                return JsonResponse({"error": "Некорректный URL."}, status=400)
            
            # Возьмём старую ссылку если есть, если нет то создадим новую
            short_tag, tag_created = ShortLink.objects.get_or_create(
            full_link=original_url,
            owner_user=usr_name,
            defaults={'short_link': generate_short_link(),
                          }
                                )

            # сгененрируем нормальную короткую ссылку
            short_url = request.build_absolute_uri(
                reverse("shortener:resolve_slug", args=[short_tag.short_link])
            )

            # подготовим и отправим ответ для AJAX
            data = {
                "short_url": short_url,
                "created_at": "только что" if tag_created else short_tag.created_at.strftime("%Y-%m-%d %H:%M"),
                "clicks": short_tag.redirect_count,
                "qr_code_url": (
                    short_tag.qr_code.url if getattr(short_tag, "qr_code", None) else ""
                ),
            }

            return JsonResponse(data)
            # short_url = f"{os.environ.get('DOMAIN')}/{short_tag[0]}"        

    context = {
        'single_form': SingleURLForm(),
        'batch_form': BatchProcessForm(),
    }
    return render(request=request, template_name='shortener/index.html', context=context)


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
            try:
                url_validator(serializer.data['link'])
            except ValidationError:
                return JsonResponse({'error': f"Не верный url: '{serializer.data['link']}'"}, status=status.HTTP_400_BAD_REQUEST)

            # Возьмём старую ссылку если есть, если нет то созхдадим новую
            short_tag = ShortLink.objects.get_or_create(
            full_link=serializer.data['link'],
            defaults={'short_link': generate_short_link(),
                          }
        )
        short_url = f"{os.environ.get('DOMAIN')}/{short_tag[0]}" 
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
