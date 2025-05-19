"""
Tests for Dashboard Forms and Views:
- Validations for BoxForm creation and editing
- Automatic archival of past-dated Boxes
- File upload validation for image files
- Integration tests for Create, Edit, and Image Handling in the dashboard
"""

import json
from datetime import timedelta
from io import BytesIO
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.timezone import now
from PIL import Image

from boxes.models import Box
from dashboard.forms import BoxForm
from orders.models import Order, StripeSubscriptionMeta
from users.models import ShippingAddress

User = get_user_model()


# ============================
# Utility Functions
# ============================

def generate_test_image():
    """
    Generates a 100x100 red JPEG image for testing.
    """
    image = Image.new('RGB', (100, 100), color='red')
    image_file = BytesIO()
    image.save(image_file, 'JPEG')
    image_file.seek(0)
    return SimpleUploadedFile(
        "test_image.jpg",
        image_file.read(),
        content_type="image/jpeg"
    )


# ============================
# FORM TEST CASES
# ============================

@pytest.mark.django_db
def test_box_form_missing_fields():
    """
    Test form validation when required fields are missing.
    """
    form = BoxForm(data={})
    assert not form.is_valid()
    assert "name" in form.errors
    assert "shipping_date" in form.errors


@pytest.mark.django_db
def test_box_form_invalid_date():
    """
    Test form validation when the date format is invalid.
    """
    form = BoxForm(data={
        "name": "Invalid Date Box",
        "description": "This box has an invalid date",
        "shipping_date": "invalid-date"
    })
    assert not form.is_valid()
    assert "shipping_date" in form.errors


@pytest.mark.django_db
def test_box_form_valid_creation():
    """
    Test successful BoxForm creation with a valid date.
    """
    future_date = now().date() + timedelta(days=5)
    form = BoxForm(data={
        "name": "Future Box",
        "description": "This is a valid box",
        "shipping_date": future_date,
    })
    assert form.is_valid()
    box = form.save()
    assert not box.is_archived  # Future date should not be archived


@pytest.mark.django_db
def test_box_form_auto_archive():
    """
    Test auto-archiving of a box with a past date.
    """
    # Set the date to the previous month so it actually triggers the archive
    past_date = now().date().replace(day=1) - timedelta(days=1)
    form = BoxForm(data={
        "name": "Past Box",
        "description": "This is a past box",
        "shipping_date": past_date,
    })

    assert form.is_valid()
    box = form.save()
    box.refresh_from_db()
    assert box.is_archived


@pytest.mark.django_db
def test_box_form_editing():
    """
    Test updating a box and changing its shipping date.
    """
    initial_date = now().date() + timedelta(days=10)
    box = Box.objects.create(
        name="Editable Box",
        description="This is editable",
        shipping_date=initial_date
    )

    # Set it to the previous month to trigger auto-archive logic
    updated_date = now().date().replace(day=1) - timedelta(days=1)
    form = BoxForm(data={
        "name": "Updated Box",
        "description": "Updated description",
        "shipping_date": updated_date,
    }, instance=box)

    assert form.is_valid()
    updated_box = form.save()
    updated_box.refresh_from_db()
    assert updated_box.is_archived


@pytest.mark.django_db
def test_box_form_invalid_file():
    """
    Test BoxForm with a non-image file upload.
    """
    # Uploading a plain text file instead of an image
    invalid_file = SimpleUploadedFile(
        "test.txt",
        b"file content",
        content_type="text/plain"
    )
    form = BoxForm(data={
        "name": "File Box",
        "description": "Invalid file upload",
        "shipping_date": now().date(),
    }, files={"image": invalid_file})

    # Assert form is invalid and the error is caught
    assert not form.is_valid()
    assert "image" in form.errors
    assert form.errors["image"] == ["The uploaded file is not a valid image."]


# ============================
# INTEGRATION TEST CASES
# ============================

@pytest.mark.django_db
def test_create_box(client, admin_user):
    """
    Test creating a box with valid data.
    """
    client.force_login(admin_user)
    future_date = now().date() + timedelta(days=10)

    # Generate a real image for testing
    image = generate_test_image()

    response = client.post(reverse('add_box'), {
        "name": "Test Box",
        "description": "A box for testing",
        "shipping_date": future_date.strftime('%d/%m/%Y'),
        "image": image
    })

    assert response.status_code == 302

    # Verify the box was created correctly
    box = Box.objects.get(name="Test Box")
    assert box.description == "A box for testing"
    assert not box.is_archived
    assert box.image


@pytest.mark.django_db
def test_edit_box_image_update(client, admin_user):
    """
    Test editing a box to change its image.
    """
    client.force_login(admin_user)
    initial_date = now().date() + timedelta(days=10)
    box = Box.objects.create(name="Image Box", shipping_date=initial_date)

    # Generate a real image for testing
    new_image = generate_test_image()

    response = client.post(reverse('edit_box', args=[box.id]), {
        "name": "Image Box",
        "description": "New image",
        "shipping_date": initial_date.strftime('%d/%m/%Y'),
        "image": new_image
    })

    assert response.status_code == 302
    box.refresh_from_db()
    assert box.image

    # Check if the public ID (or URL) exists, not the original file name
    public_id = (
        str(box.image.public_id)
        if hasattr(box.image, 'public_id')
        else str(box.image)
    )
    assert len(public_id) > 0


@pytest.mark.django_db
def test_edit_box_date_forward(client, admin_user):
    """
    Test editing a box to move its date forward.
    """
    client.force_login(admin_user)
    initial_date = now().date() + timedelta(days=5)
    box = Box.objects.create(name="Forward Box", shipping_date=initial_date)

    new_date = now().date() + timedelta(days=15)
    response = client.post(reverse('edit_box', args=[box.id]), {
        "name": "Forward Box",
        "description": "Moved forward",
        "shipping_date": new_date.strftime('%d/%m/%Y'),
    })

    assert response.status_code == 302
    box.refresh_from_db()
    assert not box.is_archived
    assert box.shipping_date == new_date

# ============================
# USER ADMIN TEST CASES
# ============================


@pytest.mark.django_db
def test_user_admin_overview(client, admin_user):
    """
    Tests that the user admin overview page loads correctly.
    """
    client.force_login(admin_user)
    response = client.get(reverse('user_admin'))
    assert response.status_code == 200
    assert "users" in response.context
    assert isinstance(response.context["users"], QuerySet)


@pytest.mark.django_db
def test_toggle_user_state(client, admin_user):
    """
    Tests toggling the active state of a user.
    """
    # Explicitly set password
    admin_user.set_password("admin_password")
    admin_user.save()

    client.force_login(admin_user)
    user = User.objects.create(
        username="testuser",
        email="testuser@example.com",
        is_active=True
    )
    response = client.post(
        reverse('admin_toggle_user_state', args=[user.id]),
        data=json.dumps({"password": "admin_password"}),
        content_type="application/json"
    )
    user.refresh_from_db()
    assert not user.is_active
    assert response.status_code == 200


@pytest.mark.django_db
@patch("dashboard.views.send_password_reset_email")
def test_admin_password_reset(mock_send_email, client, admin_user):
    """
    Tests admin-triggered password reset for a user.
    """
    # Explicitly set password
    admin_user.set_password("admin_password")
    admin_user.save()

    client.force_login(admin_user)
    user = User.objects.create(
        username="testuser",
        email="testuser@example.com",
        is_active=True
    )
    user.set_password("admin_password")
    user.save()

    print("=== DEBUG === User setup completed and ready for password reset.")

    response = client.post(reverse('admin_password_reset', args=[user.id]),
                           data=json.dumps({"password": "admin_password"}),
                           content_type="application/json")

    print("=== DEBUG === Response status code:", response.status_code)
    print("=== DEBUG === Mock call count:", mock_send_email.call_count)

    assert response.status_code == 200
    mock_send_email.assert_called_once_with(user, domain='testserver')


# ============================
# ORDER MANAGEMENT TEST CASES
# ============================

@pytest.mark.django_db
def test_order_status_update(client, admin_user):
    """
    Tests that the order status can be updated correctly.
    """
    # Make admin_user a staff member
    admin_user.is_staff = True
    admin_user.save()

    # Force login and ensure session is flushed properly
    client.force_login(admin_user)
    session = client.session
    session['user_id'] = admin_user.id
    session.save()

    # Create the address and user
    address = ShippingAddress.objects.create(
        user=admin_user,
        recipient_f_name='John',
        recipient_l_name='Doe',
        address_line_1='123 Test Street',
        town_or_city='Test Town',
        postcode='TE5 5ST',
        country='GB',
        phone_number='0123456789',
        is_default=True
    )

    # Create the order
    order = Order.objects.create(
        user=admin_user,
        status='pending',
        stripe_subscription_id='sub_123456',
        stripe_payment_intent_id='pi_78910',
        shipping_address=address
    )

    response = client.post(
        reverse('update_order_status', args=[order.id]),
        data={'status': 'shipped'},
        follow=True
    )

    # Check the final page status
    assert response.status_code == 200


@pytest.mark.django_db
@patch("stripe.Subscription.modify")
def test_admin_cancel_subscription(mock_modify, client, admin_user):
    """
    Tests an admin cancelling a user's subscription.
    """
    # Make admin_user a staff member
    admin_user.is_staff = True
    admin_user.set_password('admin_password')
    admin_user.save()

    # Create the shipping address
    address = ShippingAddress.objects.create(
        user=admin_user,
        recipient_f_name='John',
        recipient_l_name='Doe',
        address_line_1='123 Test Street',
        town_or_city='Test Town',
        postcode='TE5 5ST',
        country='GB',
        phone_number='0123456789',
        is_default=True
    )

    # Now create the subscription with the address
    subscription = StripeSubscriptionMeta.objects.create(
        user=admin_user,
        stripe_subscription_id="sub_123456",
        stripe_price_id='price_abc',
        shipping_address=address,
        cancelled_at=None
    )

    client.force_login(admin_user)

    # Send the POST request with the correct URL, now including the user ID
    url = reverse('admin_cancel_subscription', args=[admin_user.id])
    response = client.post(url, data=json.dumps({
        'subscription_id': subscription.stripe_subscription_id,
        'password': 'admin_password'
    }), content_type='application/json')

    # Assert the mock was called
    mock_modify.assert_called_once_with(
        'sub_123456',
        cancel_at_period_end=True
    )

    # Check the response
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['success'] is True
    assert (
        response_json['message']
        == 'Subscription will cancel at period end.'
    )

    # Check that the subscription is marked as cancelled
    subscription.refresh_from_db()
    assert subscription.cancelled_at is not None
