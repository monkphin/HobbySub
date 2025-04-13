from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .forms import Register


def register_user(request):
    if request.method == 'POST':
        form = Register(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto login on registration
            return redirect('home')
    else:
        form = Register()
        
    return render(request, 'users/register.html', {'form': form})

@login_required
def account_view(request):
    return render(request, 'users/account.html')


