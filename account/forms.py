from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ['username','email', 'last_name', 'first_name']