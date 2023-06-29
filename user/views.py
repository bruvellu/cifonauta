from django.shortcuts import render
from .forms import UserCifonautaCreationForm
from django.contrib import messages
# Create your views here.

def user_creation(request):
    form = UserCifonautaCreationForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Your user is created, please log in.')
    return render(request, 'users/user_creation.html', {'form': form})