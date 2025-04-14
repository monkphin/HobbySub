from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import login, logout, update_session_auth_hash

from .models import ShippingAddress
from .forms import Register, AddAddressForm, ChangePassword


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
def edit_account(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        form = UserChangeForm(instance=request.user)
    
    return render(request, 'users/edit_account.html', {'form':form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePassword(request.POST)
        if form.is_valid():
            form.save(request.user)
            update_session_auth_hash(request, request.user)
            return redirect('account')
    else:
        form = ChangePassword()

    return render(request, 'users/change_password.html', {'form': form})


@login_required
def delete_account(request):
    user = request.user
    logout(request)
    user.delete()
    return redirect('account')

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


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)

    if request.method == 'POST':
        form = AddAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('account')
        
    else:
        form = AddAddressForm(instance=address)

    return render(request, 'users/add_address.html', {'form':form})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    return redirect('account')
