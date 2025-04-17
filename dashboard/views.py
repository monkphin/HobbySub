from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model


from boxes.models import Box, BoxProduct
from .forms import BoxForm, ProductForm, UserEditForm
from orders.models import Order, StripeSubscriptionMeta

User = get_user_model()

@staff_member_required
def box_admin(request):
    boxes = Box.objects.all().order_by('-shipping_date')
    orphaned_products = BoxProduct.objects.filter(box__isnull=True).order_by('name')
    return render(request, 'dashboard/box_manager.html', {'boxes':boxes, 'orphaned_products':orphaned_products, 'editing': False})


@staff_member_required
def add_box(request):
    if request.method == 'POST':
        form = BoxForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('box_admin')
    else:
        form = BoxForm()
    return render(request, 'dashboard/box.html', {'form':form})


@staff_member_required
def edit_box(request, box_id):
    box = get_object_or_404(Box, pk=box_id)
    if request.method == 'POST':
        form = BoxForm(request.POST, instance=box)
        if form.is_valid():
            form.save()
            return redirect('box_admin')
    else:
        form = BoxForm(instance=box)
    return render(request, 'dashboard/box.html', {'form': form, 'box_id': box_id, 'editing': True})


@staff_member_required
def delete_box(request, box_id):
    box = get_object_or_404(Box, pk=box_id)
    if request.method == 'POST':
        box.delete()
        return redirect('box_admin')
    return render(request, 'dashboard/delete_box.html', {'box_id': box_id})


@staff_member_required
def add_products(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('box_admin')
    else:
        form = ProductForm()
    return render(request, 'dashboard/box.html', {'form':form})

from boxes.models import BoxProduct  # you need this import


@staff_member_required
def edit_product(request, product_id):
    product = get_object_or_404(BoxProduct, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('edit_box_products', box_id=product.box.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'dashboard/product_form.html', {'form': form, 'product': product, 'editing':True})


@staff_member_required
def delete_product(request, product_id):
    product = get_object_or_404(BoxProduct, pk=product_id)
    box_id = product.box_id
    if request.method == 'POST':
        product.delete()
        return redirect('edit_box_products', box_id=box_id)
    return render(request, 'dashboard/delete_product.html', {'product': product})


@staff_member_required
def add_product_to_box(request, box_id):
    box = get_object_or_404(Box, pk=box_id)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.box = box
            product.save()
            return redirect('edit_box_products', box_id=box.id)
    else:
        form = ProductForm()

    return render(request, 'dashboard/product_form.html', {'form': form, 'box': box})


@staff_member_required
def edit_box_products(request, box_id):
    box = get_object_or_404(Box, pk=box_id)
    products = box.products.all()
    return render(request, 'dashboard/box_products.html', {'box': box, 'products': products})


@staff_member_required
def remove_product_from_box(request, product_id):
    product = get_object_or_404(BoxProduct, pk=product_id)
    box_id = request.GET.get('box_id') or product.box_id
    if request.method == 'POST':
        product.box = None
        product.save()
        return redirect('edit_box_products', box_id=box_id)
    return render(request, 'dashboard/remove_product.html', {'product': product})


@staff_member_required
def user_admin(request):
    users = User.objects.all().order_by('username')
    return render(request, 'dashboard/user_admin.html', {'users':users})


@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_admin')
    else:
        form = UserEditForm(instance=user)

    return render(request, 'dashboard/edit_user.html', {'form': form, 'user': user})


@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        user.is_active = False
        user.save()
        messages.success(request, f"{user.username}'s account has been deactivated.")
        return redirect('user_admin')

    return render(request, 'dashboard/delete_user.html', {'user': user})


@staff_member_required
def user_orders(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    orders = Order.objects.filter(user=user).order_by('-order_date')
    subs = StripeSubscriptionMeta.objects.filter(user=user).order_by('-created_at')
    active_sub = subs.filter(cancelled_at__isnull=True).first()
    cancelled_subs = subs.filter(cancelled_at__isnull=False)

    return render(request, 'dashboard/user_orders.html', {
        'user': user,
        'orders': orders,
        'active_sub': active_sub,
        'cancelled_subs': cancelled_subs,
    })
