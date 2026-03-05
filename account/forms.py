from django.contrib.auth.forms import UserCreationForm
from captcha.fields import CaptchaField
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .models import CustomUser


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ['username','email', 'last_name', 'first_name']


class CustomUserCaptchaCreationForm(UserCreationForm):
    captcha = CaptchaField(label='Введите текст с картинки')
    class Meta:
        model = User
        # fields = '__all__'
        fields = ['username','email', 'last_name', 'first_name', 'captcha']


class CustomUserLoginCaptchaForm(AuthenticationForm):
    captcha = CaptchaField(label='Введите текст с картинки')