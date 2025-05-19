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

import json
import logging

import stripe
from cloudinary.uploader import destroy
# Django/External Imports
from django.contrib.auth import authenticate, get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from boxes.models import Box, BoxProduct
from hobbyhub.mail import (send_auto_archive_notification,
                           send_order_status_update_email,
                           send_password_reset_email,
                           send_shipping_confirmation_email)
# Local Imports
from hobbyhub.utils import (alert, get_subscription_duration_display,
                            get_subscription_status)
from orders.models import Order, Payment, StripeSubscriptionMeta

from .decorators import custom_staff_required
from .forms import BoxForm, ProductForm, UserEditForm

logger = logging.getLogger(__name__)

User = get_user_model()


@custom_staff_required
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


@custom_staff_required
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
            try:
                new_box = form.save(commit=False)  # Do not commit yet

                # Save to DB
                new_box.save()
                alert(request, "success", "Box successfully created.")
                logger.info(
                    f"Admin {request.user} created box: {new_box.name}"
                )

                # Send the email
                if new_box.is_archived:
                    send_auto_archive_notification(new_box)

                return redirect('edit_box_products', box_id=new_box.id)

            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                logger.error(f"Failed to create box: {e}\nTraceback:\n{tb}")
                alert(
                    request,
                    "error",
                    f"There was a problem creating the box: {e}"
                )
        else:
            # If the form is not valid, we should log the errors for clarity
            logger.error(f"Form is not valid: {form.errors}")
            alert(
                request,
                "error",
                (
                    "There was a problem creating the box. "
                    "Please check the form inputs."
                )
            )
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


@custom_staff_required
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
            try:
                updated_box = form.save(commit=False)

                # Save the box
                updated_box.save()

                logger.info(
                    f"Admin {request.user} edited box: "
                    f"{updated_box.name} (ID: {updated_box.id})"
                )
                alert(request, "success", "Box successfully edited.")

                # Email notification if auto-archived
                if updated_box.is_archived:
                    send_auto_archive_notification(updated_box)

                return redirect('box_admin')

            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                logger.error(f"Failed to edit box: {e}\nTraceback:\n{tb}")
                alert(request, "error", "There was a problem editing the box.")
        else:
            alert(request, "error", "There was a problem editing the box.")
            logger.info(f"Admin {request.user} error editing box.")
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


@custom_staff_required
def delete_box(request, box_id):
    """
    Deletes a box after confirmation, checks password first.
    """
    if request.method == 'POST':
        # Check the content type
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            password = data.get('password')
        else:
            password = request.POST.get('password')

        # Validate the password
        user = authenticate(username=request.user.username, password=password)
        if not user:
            return JsonResponse({
                "success": False,
                "error": "Password is incorrect."
            }, status=403)

        box = get_object_or_404(Box, pk=box_id)

        try:
            if box.image:
                result = destroy(box.image.public_id)
                if result.get('result') == 'ok':
                    logger.info(
                        f"Cloudinary image deleted for box: {box.name}"
                    )

            box.delete()
            alert(
                request,
                "success",
                f"Box '{box.name}' successfully deleted."
            )
            logger.info(
                f"Admin {request.user} deleted box: {box.name} (ID: {box_id})"
            )
            return JsonResponse({"success": True})

        except Exception as e:
            logger.error(f"Failed to delete box: {e}")
            return JsonResponse({
                "success": False,
                "error": "An error occurred during deletion."
            }, status=500)


@custom_staff_required
def edit_box_products(request, box_id):
    """
    Displays and manages products linked to a specific box.

    - Shows all products currently assigned to the box.
    - Provides links to edit or remove each product.
    - Lists orphaned products for bulk add.
    """
    box = get_object_or_404(Box, pk=box_id)
    products = box.products.all()
    orphaned_products = BoxProduct.objects.filter(box__isnull=True)

    if request.method == 'POST':
        selected_products = request.POST.getlist('orphaned_products')
        if selected_products:
            # Update the selected orphaned products to this box
            BoxProduct.objects.filter(id__in=selected_products).update(box=box)
            alert(
                request,
                "success",
                f"Successfully added {len(selected_products)} "
                f"orphaned products to '{box.name}'."
            )
            return redirect('edit_box_products', box_id=box_id)
        else:
            alert(request, "error", "No orphaned products were selected.")

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
            'orphaned_products': orphaned_products,  # Add this to the context
        }
    )


@custom_staff_required
def assign_orphaned_to_box(request, box_id):
    """
    Reassigns selected orphaned products to the specified box.
    """
    box = get_object_or_404(Box, pk=box_id)
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        if product_ids:
            products = BoxProduct.objects.filter(
                id__in=product_ids, box__isnull=True
            )
            products.update(box=box)
            alert(
                request,
                "success",
                f"{products.count()} products "
                f"successfully added to '{box.name}'."
            )
        else:
            alert(request, "error", "No products selected.")
    return redirect('edit_box_products', box_id=box_id)


@custom_staff_required
def add_product_to_box(request, box_id):
    """
    Adds a new product directly to a specific box.

    - On GET: displays a product form.
    - On POST: creates a new BoxProduct and links it to the given box.
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


@custom_staff_required
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


@custom_staff_required
def edit_product(request, product_id):
    """
    Allows an admin to edit a product’s name, quantity, or box assignment.

    - Supports both box-linked and orphaned products.
    - Redirects to the related box’s product editor after saving.
    """
    product = get_object_or_404(BoxProduct, pk=product_id)

    # Track the original state before editing
    was_orphaned = product.box is None

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            logger.info(
                f"Admin {request.user} edited product "
                f"'{product.name}' (ID: {product.id})"
            )
            alert(request, "success", "Products successfully edited.")

            # If it has a box, redirect back to the box view
            if product.box:
                return redirect('edit_box_products', box_id=product.box.id)

            # If it is now orphaned, but was not orphaned before,
            # show the message
            if not was_orphaned:
                alert(
                    request,
                    "warning",
                    "Product is now orphaned (no box linked)."
                )

            return redirect('box_admin')
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


@custom_staff_required
def delete_product(request, product_id):
    """
    Deletes a product after confirmation, checks password first.
    """
    if request.method == 'POST':
        # Check the content type
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            password = data.get('password')
        else:
            password = request.POST.get('password')

        # Validate the password
        user = authenticate(username=request.user.username, password=password)
        if not user:
            return JsonResponse({
                "success": False,
                "error": "Password is incorrect."
            }, status=403)

        # Get the product
        product = get_object_or_404(BoxProduct, pk=product_id)

        try:
            # Delete the product
            product.delete()
            alert(
                request,
                "success",
                f"Product '{product.name}' successfully deleted."
            )
            logger.info(
                f"Admin {request.user} "
                f"deleted product: {product.name} (ID: {product_id})"
            )
            return JsonResponse({"success": True})

        except Exception as e:
            logger.error(f"Failed to delete product: {e}")
            return JsonResponse({
                "success": False,
                "error": "An error occurred during deletion."
            }, status=500)


@custom_staff_required
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


@custom_staff_required
def manage_orphaned_products(request):
    """
    Handles batch reassignment or deletion of orphaned products.
    """
    # === DEBUGGING OUTPUT ===
    print("=== DEBUGGING: Entering manage_orphaned_products ===")
    print(f"Request method: {request.method}")
    print(f"POST Data: {request.POST}")

    action = request.POST.get('action')
    product_ids = request.POST.getlist('product_ids')

    # Log the action and product IDs
    print(f"=== DEBUGGING: Action received -> {action}")
    print(f"=== DEBUGGING: Product IDs received -> {product_ids}")

    if action not in ['reassign', 'delete']:
        alert(request, "error", "Invalid action.")
        print(
            "=== DEBUGGING: Invalid action encountered, "
            "redirecting to box_admin ==="
        )
        return redirect('box_admin')

    if not product_ids:
        alert(request, "error", "No products selected.")
        print(
            "=== DEBUGGING: No products selected, "
            "redirecting to box_admin ==="
        )
        return redirect('box_admin')

    if action == 'reassign':
        print(
            f"=== DEBUGGING: Redirecting to reassign_orphaned_products "
            f"with IDs: {product_ids} ==="
        )
        # Redirect to reassign page
        return redirect(
            'reassign_orphaned_products',
            product_ids=",".join(product_ids)
        )

    elif action == 'delete':
        print(f"=== DEBUGGING: Deleting products with IDs: {product_ids} ===")
        # Batch delete
        BoxProduct.objects.filter(id__in=product_ids).delete()
        alert(
            request,
            "success",
            f"Deleted {len(product_ids)} orphaned products."
        )
        return redirect('box_admin')


@custom_staff_required
def reassign_orphaned_products(request, product_ids):
    """
    Reassigns multiple orphaned products to a selected box.
    """
    product_ids = product_ids.split(',')
    products = BoxProduct.objects.filter(id__in=product_ids)

    if request.method == 'POST':
        box_id = request.POST.get('box_id')
        box = get_object_or_404(Box, pk=box_id)
        products.update(box=box)
        alert(
            request,
            "success",
            f"{products.count()} products reassigned to '{box.name}'."
        )
        return redirect('box_admin')

    boxes = Box.objects.all()
    return render(request, 'dashboard/reassign_products.html', {
        'products': products,
        'boxes': boxes
    })


@custom_staff_required
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


@custom_staff_required
def edit_user(request, user_id):
    """
    Allows an admin to update a user's details.

    - Supports changing username, email, and admin status.
    - Displays Last Login and Date Joined as context.
    """
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        # If it's AJAX, handle the JSON request
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            password = data.get('password')
            form_data = {
                'username': data.get('username'),
                'email': data.get('email'),
                'is_staff': data.get('is_staff')
            }

            print(f"Received form data: {form_data}")

            # Authenticate admin user
            admin_user = authenticate(
                username=request.user.username,
                password=password
            )
            if not admin_user:
                logger.warning(
                    f"Password attempt failed for {request.user.username}"
                )
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Password is incorrect."
                    },
                    status=403
                )

            # Update the form data
            form = UserEditForm(form_data, instance=user)
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
                return JsonResponse({
                    "success": True,
                    "message": f"User '{user.username}' updated successfully."
                })
            else:
                logger.error(f"Form errors: {form.errors}")
                return JsonResponse(
                    {"success": False,
                     "error": "Form data is invalid."},
                    status=400
                )

    # Regular GET request
    form = UserEditForm(instance=user)
    return render(
        request,
        'dashboard/edit_user.html',
        {
            'form': form,
            'user': user,
            'last_login': user.last_login,
            'date_joined': user.date_joined
        }
    )


@custom_staff_required
def admin_initiated_password_reset(request, user_id):
    """
    Admin triggers a password reset email for the selected user.
    """
    if request.method != 'POST':
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid request method."
            },
            status=405
        )

    # Extract password from the JSON payload
    data = json.loads(request.body)
    password = data.get('password')

    # Authenticate the admin
    admin_user = authenticate(
        username=request.user.username,
        password=password
    )

    if not admin_user:
        logger.warning(
            f"Password reset attempt "
            f"with incorrect password by {request.user.username}"
        )
        return JsonResponse({
            "success": False,
            "error": "Incorrect password."
        }, status=403)

    try:
        # Fetch the user or return a 404 if not found
        user = get_object_or_404(User, pk=user_id)
    except Exception as e:
        logger.error(f"Failed to find user {user_id}: {e}")
        return JsonResponse({
            "success": False,
            "error": "User not found."
        }, status=404)

    # Check if the user is active
    if not user.is_active:
        logger.warning(
            f"Attempted password reset for deactivated user: {user.username}"
        )
        return JsonResponse({
            "success": False,
            "error": "User account is deactivated."
        }, status=403)

    # Proceed with the password reset logic
    send_password_reset_email(user, domain=request.get_host())

    # Log the action for auditing
    logger.info(
        f"Admin {request.user.username} "
        f"initiated password reset for user {user.username}"
    )

    return JsonResponse({
        "success": True,
        "message": f"Password reset email sent to {user.email}."
    })


@custom_staff_required
def admin_toggle_user_state(request, user_id):
    """
    Admin toggles the user's active state.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        password = data.get('password')

        # Authenticate the admin
        admin_user = authenticate(
            username=request.user.username,
            password=password
        )
        if not admin_user:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Password is incorrect."
                },
                status=403
            )

        # Get the user and toggle the state
        user = get_object_or_404(User, pk=user_id)
        user.is_active = not user.is_active
        user.save()

        # Log the action
        state = "activated" if user.is_active else "deactivated"
        logger.info(
            f"Admin {request.user.username} {state} user {user.username}"
        )

        alert(request, "success", f"User '{user.username}' has been {state}.")
        return JsonResponse({
            "success": True,
            "message": f"User '{user.username}' has been {state}."
        })


@custom_staff_required
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

    sub_map = {
        sub.stripe_subscription_id: {
            'sub': sub,
            'label': get_subscription_duration_display(sub),
            'status': get_subscription_status(sub),
        } for sub in subs
    }

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
            'sub_map': sub_map
        }
    )


@custom_staff_required
def update_order_status(request, order_id):
    """
    Allows an admin to update the status of an order from the dashboard.
    """
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status == 'cancelled' and order.stripe_subscription_id:
            # Call Stripe to cancel
            try:
                stripe.Subscription.modify(
                    order.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                order.status = 'cancelled'
                order.save()
                alert(
                    request,
                    "success",
                    "Subscription successfully marked as cancelled."
                )

                # Send email notification for cancellation
                send_order_status_update_email(
                    order.user,
                    order.id,
                    'cancelled'
                )

                # Fire a toast notification
                alert(
                    request,
                    "success",
                    "Subscription has been cancelled and email "
                    "notification sent."
                )

            except Exception as e:
                logger.error(f"Failed to cancel subscription: {e}")
                alert(request, "error", "Failed to cancel the subscription.")

        elif new_status == 'shipped':
            order.status = 'shipped'
            order.save()
            alert(
                request,
                "success",
                f"Order #{order.id} status updated to Shipped."
            )

            # 🎯 Send the shipping confirmation email here
            send_shipping_confirmation_email(order.user, order.box)

            # Log the email event
            logger.info(
                f"Shipping confirmation email sent for order #{order.id} "
                f"to user {order.user.email}."
            )

        elif new_status == 'cancelled':
            # If it's just a plain order, mark as cancelled
            order.status = 'cancelled'
            order.save()
            alert(request, "success", f"Order #{order.id} has been cancelled.")

            # Send email notification for cancellation
            send_order_status_update_email(order.user, order.id, 'cancelled')

            # Fire a toast notification
            alert(
                request, "success",
                "Order has been cancelled and email notification sent.")

        elif new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            alert(
                request,
                "success",
                f"Order #{order.id} status updated to {new_status.title()}."
            )

            # Send email notification for status change
            send_order_status_update_email(order.user, order.id, new_status)

            # Fire a toast notification
            alert(
                request,
                "success",
                f"Order status updated to {new_status.title()} and email sent."
            )

        else:
            alert(request, "error", "Invalid status selected.")

    return redirect('user_orders', user_id=order.user.id)


@custom_staff_required
@require_POST
def admin_cancel_subscription(request, user_id):
    """
    Allows an admin to securely cancel a user's subscription.
    """
    data = json.loads(request.body)
    password = data.get('password')
    subscription_id = data.get('subscription_id')

    if not subscription_id:
        return JsonResponse({
            'success': False,
            'error': 'Subscription ID not provided.'
        })

    if authenticate(username=request.user.username, password=password):
        try:
            sub = StripeSubscriptionMeta.objects.get(
                user_id=user_id,
                stripe_subscription_id=subscription_id,
                cancelled_at__isnull=True
            )

            stripe.Subscription.modify(
                sub.stripe_subscription_id,
                cancel_at_period_end=True
            )

            sub.cancelled_at = timezone.now()
            sub.save()

            # Log and alert
            logger.info(
                f"Admin {request.user} "
                f"cancelled subscription {subscription_id} "
                f"for user ID {user_id}"
            )
            return JsonResponse({
                'success': True,
                'message': 'Subscription will cancel at period end.'
            })

        except StripeSubscriptionMeta.DoesNotExist:
            logger.warning(
                f"Attempted to cancel subscription {subscription_id} "
                f"for user ID {user_id}, but it was not found."
            )
            return JsonResponse({
                'success': False,
                'error': 'No active subscription found to cancel.'
            })

    else:
        return JsonResponse({'success': False, 'error': 'Incorrect password'})
