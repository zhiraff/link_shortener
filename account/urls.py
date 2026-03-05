from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings

from .views import register
from .forms import CustomUserLoginCaptchaForm

login_context = {
    'google_oauth': True if settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY else False,
    'vk_oauth': True if settings.SOCIAL_AUTH_VK_OAUTH2_KEY else False,
    'github_oauth': True if settings.SOCIAL_AUTH_GITHUB_KEY else False,
    'yandex_oauth': True if settings.SOCIAL_AUTH_YANDEX_OAUTH2_KEY else False,
}


app_name = "account"

urlpatterns = [
    path('login/', LoginView.as_view(template_name='account/login.html', extra_context=login_context, form_class=CustomUserLoginCaptchaForm), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),

]