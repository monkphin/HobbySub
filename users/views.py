from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .models import ShippingAddress
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