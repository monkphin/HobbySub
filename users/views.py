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

            if address.is_default:
                ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)

            if address.is_billing:
                ShippingAddress.objects.filter(user=request.user, is_billing=True).update(is_billing=False)

            address.save()
            return redirect('account')
    else:
        form = AddAddressForm(initial={
            'recipient_f_name': request.user.first_name,
            'recipient_l_name': request.user.last_name,
        })

    return render(request, 'users/add_address.html', {'form': form})


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)

    if request.method == 'POST':
        form = AddAddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)

            if updated_address.is_default:
                ShippingAddress.objects.filter(user=request.user, is_default=True).exclude(id=address.id).update(is_default=False)

            if updated_address.is_billing:
                ShippingAddress.objects.filter(user=request.user, is_billing=True).exclude(id=address.id).update(is_billing=False)

            updated_address.save()
            return redirect('account')
    else:
        form = AddAddressForm(instance=address)

    return render(request, 'users/add_address.html', {'form': form})



@login_required
def set_default_address(request, address_id):
    user = request.user
    address = get_object_or_404(ShippingAddress, id=address_id, user=user)

    # Unset existing default
    ShippingAddress.objects.filter(user=user, is_default=True).update(is_default=False)

    # Set the new default address
    address.is_default=True
    address.save()

    return redirect('account')


@login_required
def set_billing_address(request, address_id):
    user = request.user
    ShippingAddress.objects.filter(user=user, is_billing=True).update(is_billing=False)
    ShippingAddress.objects.filter(user=user, id=address_id).update(is_billing=True)
    return redirect('account')


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    return redirect('account')
