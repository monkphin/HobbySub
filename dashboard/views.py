"""
dashboard/views.py

Custom admin dashboard views for managing:
- Subscription boxes (create, edit, delete, assign products).
- Products (CRUD, orphan management).
- Users (admin-only edit/deactivation).
- Orders and subscriptions (view history per user).

All views are protected with @staff_member_required.
Uses MaterializeCSS-compatible forms and a custom `alert()` utility for
messaging.
"""

# Django/External Imports
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
import logging

# Local Imports
from hobbyhub.utils import alert
from boxes.models import Box, BoxProduct
from .forms import BoxForm, ProductForm, UserEditForm
from hobbyhub.mail import send_shipping_confirmation_email
from orders.models import Order, Payment, StripeSubscriptionMeta

logger = logging.getLogger(__name__)

User = get_user_model()


@staff_member_required
def box_admin(request):
    """
    Displays the admin dashboard for box management.

    - Lists all boxes ordered by shipping date.
    - Also displays orphaned products (not assigned to any box).
    """
    boxes = Box.objects.all().order_by('-shipping_date')
    orphaned_products = (
        BoxProduct.objects
        .filter(box__isnull=True)
        .order_by('name')
    )
    return render(
        request,
        'dashboard/box_manager.html',
        {
            'boxes': boxes,
            'orphaned_products': orphaned_products,
            'editing': False,
        }
    )


@staff_member_required
def add_box(request):
    """
    Allows an admin to create a new subscription box.

    - On GET: displays an empty BoxForm.
    - On POST: saves the new box and redirects to its product management page.
    - Uses alerts to indicate success or form errors.
    """
    box = None
    if request.method == 'POST':
        form = BoxForm(request.POST, request.FILES)
        if form.is_valid():
            new_box = form.save()
            alert(request, "success", "Box successfully created.")
            logger.info(f"Admin {request.user} created box: {new_box.name}")
            return redirect('edit_box_products', box_id=new_box.id)
        else:
            alert(request, "error", "There was a problem creating the box.")
            logger.info(f"Admin {request.user} error creating box.")
    else:
        form = BoxForm()
    return render(
        request,
        'dashboard/box.html',
        {
            'form': form,
            'box': box,
        }
    )


@staff_member_required
def edit_box(request, box_id):
    """
    Allows an admin to update an existing box.

    - Pre-populates the form with current box data.
    - On success, redirects back to the box admin overview.
    - Displays error messages on invalid submissions.
    """
    box = get_object_or_404(Box, pk=box_id)
    if request.method == 'POST':
        form = BoxForm(request.POST, request.FILES, instance=box)
        if form.is_valid():
            form.save()
            logger.info(
                f"Admin {request.user} edited box: {box.name} (ID: {box.id})"
            )
            alert(request, "success", "Box successfully edited.")
            return redirect('box_admin')
        else:
            alert(request, "error", "There was a problem editing the box.")
    else:
        form = BoxForm(instance=box)
    return render(
        request,
        'dashboard/box.html',
        {
            'form': form,
            'box_id': box_id,
            'editing': True,
            'box': box,
        }
    )


@staff_member_required
def delete_box(request, box_id):
    """
    Deletes a box after confirmation.

    - Only performs deletion on POST.
    - Redirects back to box admin on success.
    """
    box = get_object_or_404(Box, pk=box_id)
    if request.method == 'POST':
        box.delete()
        alert(request, "success", "Box successfully deleted.")
        logger.info(
            f"Admin {request.user} deleted box: {box.name} (ID: {box.id})"
        )
        return redirect('box_admin')

    return render(
        request,
        'dashboard/delete_box.html',
        {
            'box_id': box_id,
        }
    )


@staff_member_required
def edit_box_products(request, box_id):
    """
    Displays and manages products linked to a specific box.

    - Shows all products currently assigned to the box.
    - Provides links to edit or remove each product.
    """
    box = get_object_or_404(Box, pk=box_id)
    products = box.products.all()
    logger.info(
        f"Admin {request.user} is editing products in box "
        f"'{box.name}' (ID: {box.id})"
    )
    return render(
        request,
        'dashboard/box_products.html',
        {
            'box': box,
            'products': products,
        }
    )


@staff_member_required
def add_product_to_box(request, box_id):
    """
    Adds a new product directly to a specific box.

    - On GET: displays a product form.
    - On POST: creates a new BoxProduct and links it to the given box.
    - Redirects back to the box’s product editor with a success
      or error message.
    """
    box = get_object_or_404(Box, pk=box_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.box = box
            product.save()
            logger.info(
                f"Admin {request.user} added product '{product.name}' "
                f"to box '{box.name}' (ID: {box.id})"
            )
            alert(
                request,
                "success",
                f"Product '{product.name}' successfully added "
                f"to the box: {box.name}."
            )
            return redirect('edit_box_products', box_id=box.id)
        else:
            alert(
                request,
                "error",
                "There was a problem adding the products to the box."
            )
    else:
        form = ProductForm()

    return render(
        request,
        'dashboard/product_form.html',
        {
            'form': form,
            'box': box,
        }
    )


@staff_member_required
def add_products(request):
    """
    Adds a new product without assigning it to a box (orphaned product).

    - Useful for creating products ahead of time.
    - Appears in the orphaned list until assigned to a box.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            logger.info(
                f"Admin {request.user} "
                f"added orphan product '{product.name}'"
            )
            alert(request, "success", "Product successfully added.")
            return redirect('box_admin')
        else:
            alert(request, "error", "There was a problem adding the products.")
    else:
        form = ProductForm()

    return render(
        request,
        'dashboard/product_form.html',
        {
            'form': form,
            'editing': False,
        }
    )


@staff_member_required
def edit_product(request, product_id):
    """
    Allows an admin to edit a product’s name, quantity, or box assignment.

    - Supports both box-linked and orphaned products.
    - Redirects to the related box’s product editor after saving.
    """
    product = get_object_or_404(BoxProduct, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            logger.info(
                f"Admin {request.user} edited product "
                f"'{product.name}' (ID: {product.id})"
            )
            alert(request, "success", "Products successfully edited.")
            return redirect('edit_box_products', box_id=product.box.id)
        else:
            alert(
                request,
                "error",
                "There was a problem editing the products."
            )
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        'dashboard/product_form.html',
        {
            'form': form,
            'product': product,
            'editing': True,
        }
    )


@staff_member_required
def delete_product(request, product_id):
    """
    Permanently deletes a product from the system.

    - Handles both box-linked and orphaned products.
    - On success: redirects to the relevant box product page or box admin.
    """
    product = get_object_or_404(BoxProduct, pk=product_id)
    box_id = product.box_id

    if request.method == 'POST':
        try:
            product.delete()
            alert(request, "success", "Product permanently deleted.")
        except Exception as e:
            logger.error(f"Deletion error: {e}")
            alert(
                request,
                "error",
                "There was a problem deleting the product."
            )

        if box_id:
            return redirect('edit_box_products', box_id=box_id)
        else:
            return redirect('box_admin')

    return render(
        request,
        'dashboard/delete_product.html',
        {
            'product': product,
            'box_id': box_id,
        }
    )


@staff_member_required
def remove_product_from_box(request, product_id):
    """
    Unassigns a product from its box (makes it orphaned).

    - Does not delete the product.
    - Product will remain visible in the orphaned list until reassigned or
    deleted.
    """
    product = get_object_or_404(BoxProduct, pk=product_id)
    box_id = request.GET.get('box_id') or product.box_id
    box = get_object_or_404(Box, pk=box_id)

    if request.method == 'POST':
        try:
            product.box = None
            product.save()
            logger.info(
                f"Admin {request.user} removed product "
                f"'{product.name}' from box '{box.name}'"
            )
            alert(
                request,
                "success",
                f"Product successfully removed from box: {box.name}."
            )
        except Exception as e:
            logger.error(
                f"Admin {request.user} failed to remove product "
                f"'{product.name}' from box '{box.name}': {e}",
                exc_info=True
            )
            alert(
                request,
                "error",
                "There was a problem removing the product from the box."
            )
        return redirect('edit_box_products', box_id=box_id)

    return render(
        request,
        'dashboard/remove_product.html',
        {
            'product': product,
            'box': box,
        }
    )


@staff_member_required
def user_admin(request):
    """
    Admin overview of all users.

    - Displays a list of users ordered by username.
    - Provides links to edit, deactivate, or view order history.
    """
    users = User.objects.all().order_by('username')
    return render(
        request,
        'dashboard/user_admin.html',
        {
            'users': users,
        }
    )


@staff_member_required
def edit_user(request, user_id):
    """
    Allows an admin to update a user's details.

    - Supports changing username, email, and admin status.
    - Uses a Materialize-compatible form for inline editing.
    """
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            logger.info(
                f"Admin {request.user} "
                f"updated user: {user.username} (ID: {user.id})"
            )
            alert(
                request,
                "success",
                f"User '{user.username}' updated successfully."
            )
            return redirect('user_admin')
        else:
            alert(
                request,
                "error",
                f"Unable to update User '{user.username}'."
            )
    else:
        form = UserEditForm(instance=user)

    return render(
        request,
        'dashboard/edit_user.html',
        {
            'form': form,
            'user': user,
        }
    )


@staff_member_required
def delete_user(request, user_id):
    """
    Deactivates a user account instead of deleting it.

    - Sets is_active to False on POST.
    - Prevents accidental loss of related data (orders, addresses, etc.).
    """
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        user.is_active = False
        user.save()
        logger.warning(
            f"Admin {request.user} "
            f"deactivated user: {user.username} (ID: {user.id})"
        )
        alert(
            request,
            "success",
            f"User '{user.username}' has been deactivated."
        )
        return redirect('user_admin')

    return render(
        request,
        'dashboard/delete_user.html',
        {
            'user': user,
        }
    )


@staff_member_required
def user_orders(request, user_id):
    """
    Displays a user's order and subscription history in the admin dashboard.

    - Shows active and cancelled subscriptions.
    - Annotates each order with its payment info.
    """
    user = get_object_or_404(User, pk=user_id)
    orders = Order.objects.filter(user=user).order_by('-order_date')
    subs = (
        StripeSubscriptionMeta.objects
        .filter(user=user)
        .order_by('-created_at')
    )
    active_sub = subs.filter(cancelled_at__isnull=True).first()
    cancelled_subs = subs.filter(cancelled_at__isnull=False)

    for order in orders:
        order.payment = Payment.objects.filter(order=order).first()

    return render(
        request,
        'dashboard/user_orders.html',
        {
            'user': user,
            'orders': orders,
            'active_sub': active_sub,
            'cancelled_subs': cancelled_subs,
        }
    )


@staff_member_required
def update_order_status(request, order_id):
    """
    Allows an admin to update the status of an order from the dashboard.

    - Sends a shipping confirmation email if marked as 'shipped'.
    """
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            if new_status == "shipped":
                send_shipping_confirmation_email(order.user, order.box)
                logger.info(
                    f"Shipping confirmation email sent to {order.user.email} "
                    f"for box {order.box}"
                )
            alert(
                request,
                "success",
                f"Order #{order.id} status updated to {new_status.title()}."
            )
        else:
            alert(request, "error", "Invalid status selected.")

    return redirect('user_orders', user_id=order.user.id)
