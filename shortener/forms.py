# forms.py
from django import forms
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class SingleURLForm(forms.Form):
    """Форма для одиночной ссылки"""
    
    original_url = forms.URLField(
        label='Оригинальная ссылка',
        max_length=500,
        widget=forms.URLInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'https://example.com/very-long-url-path',
            'required': True,
        })
    )
    
    short_length = forms.IntegerField(
        label='Длина короткой ссылки',
        initial=12,
        min_value=6,
        max_value=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'range',
            'id': 'short_length',
            'min': '6',
            'max': '20',
        })
    )
    
    use_digits = forms.BooleanField(
        label='Использовать цифры в короткой ссылке',
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'use_digits',
        })
    )
    
    def clean_original_url(self):
        """Валидация URL"""
        url = self.cleaned_data.get('original_url')
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise forms.ValidationError('Пожалуйста, введите корректный URL')
        return url
    
    def clean_short_length(self):
        """Валидация длины короткой ссылки"""
        length = self.cleaned_data.get('short_length')
        if length < 6 or length > 20:
            raise forms.ValidationError('Длина должна быть от 6 до 20 символов')
        return length


class BatchProcessForm(forms.Form):
    """Форма для пакетной обработки Excel файла"""
    
    excel_file = forms.FileField(
        label='Файл Excel (.xlsx)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls',
            'id': 'excel_file',
            'required': True,
        })
    )
    
    batch_length = forms.ChoiceField(
        label='Длина коротких ссылок',
        choices=[
            ('8', '8 символов'),
            ('10', '10 символов'),
            ('12', '12 символов'),
            ('15', '15 символов'),
        ],
        initial='10',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'batch_length',
        })
    )
    
    batch_use_digits = forms.BooleanField(
        label='Использовать цифры',
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'batch_use_digits',
        })
    )
    
    def clean_excel_file(self):
        """Валидация загружаемого файла"""
        excel_file = self.cleaned_data.get('excel_file')
        
        if not excel_file:
            raise forms.ValidationError('Пожалуйста, выберите файл')
        
        # Проверка расширения файла
        allowed_extensions = ['.xlsx', '.xls']
        import os
        ext = os.path.splitext(excel_file.name)[1].lower()
        
        if ext not in allowed_extensions:
            raise forms.ValidationError(
                'Поддерживаются только файлы Excel (.xlsx, .xls)'
            )
        
        # Проверка размера файла (максимум 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if excel_file.size > max_size:
            raise forms.ValidationError(
                f'Размер файла не должен превышать 10MB. '
                f'Текущий размер: {excel_file.size // 1024 // 1024}MB'
            )
        
        return excel_file