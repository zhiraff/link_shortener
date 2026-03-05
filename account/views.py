from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.conf import settings

from .forms import CustomUserCaptchaCreationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCaptchaCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            user.is_staff = True 
            guest_group, created = Group.objects.get_or_create(name=settings.GUEST_GROUP)
            user.groups.add(guest_group)
            user.save()
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect('shortener:index') 

    else:
        form = CustomUserCaptchaCreationForm()
    return render(request, 'account/register.html', {'form': form})

