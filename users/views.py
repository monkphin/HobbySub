from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .forms import Register, AddAddressForm


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


@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('account')
    else:
        form = AddAddressForm(initial={
                            'recipient_f_name': request.user.first_name,
                            'recipient_l_name': request.user.last_name,
                            })

    return render(request, 'users/add_address.html', {'form':form})