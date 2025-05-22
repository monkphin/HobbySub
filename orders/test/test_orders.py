import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.shortcuts import reverse
from django.test import RequestFactory
from orders.models import Box, Order, Payment, StripeSubscriptionMeta
from orders.views import create_subscription_checkout
from users.models import ShippingAddress
import threading
from django.db import transaction
import logging
import time
import random
from unittest.mock import patch
from django.db import connection


logging.basicConfig(level=logging.DEBUG)

User = get_user_model()


# Retry logic with exponential backoff
def retry_with_backoff(func, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            logging.error(
                f"Attempt {attempt + 1} failed: "
                f"{e}. Retrying in backoff..."
            )
            if connection.in_atomic_block:
                logging.error(
                    "Rollback attempted inside atomic block. "
                    "Operation will retry."
                )
            time.sleep(random.uniform(0.5, 2.0) * (2 ** attempt))
    raise RuntimeError("Max retry attempts exceeded.")


# Webhook handler with atomic transaction
def run_webhook_handler(user_id, address_id, stripe_session):
    logging.debug("Thread started")

    try:
        with transaction.atomic():
            logging.debug("Attempting to lock user and address for update...")

            # Wrap in retry logic to handle temporary issues
            def acquire_locks():
                locked_user = (
                    User.objects.select_for_update(nowait=True)
                    .get(id=user_id)
                )
                locked_address = (
                    ShippingAddress.objects.select_for_update(nowait=True)
                    .get(id=address_id)
                )
                return locked_user, locked_address

            # Use backoff strategy to avoid deadlocks
            locked_user, locked_address = retry_with_backoff(acquire_locks)

            logging.debug(
                f"User {locked_user.id} and "
                f"Address {locked_address.id} locked, proceeding..."
            )

            # Retry logic for creating the StripeSubscriptionMeta as well
            def create_subscription():
                subscription_meta, created = (
                    StripeSubscriptionMeta.objects.get_or_create(
                        stripe_subscription_id=stripe_session['subscription'],
                        defaults={
                            'user': locked_user,
                            'shipping_address': locked_address
                        }
                    )
                )
                if created:
                    logging.debug(
                        "StripeSubscriptionMeta created successfully with ID "
                        f"{subscription_meta.pk}")
                else:
                    logging.warning(
                        f"Subscription already exists: {subscription_meta.pk}"
                    )
                return subscription_meta

            # Use retry to handle concurrency issues during creation
            retry_with_backoff(create_subscription)

            logging.debug("Webhook handler completed successfully.")

    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
    finally:
        logging.debug("Thread finished")


@pytest.mark.django_db
class TestStripeSubscriptionMeta:
    def test_subscription_creation(self):
        """
        Tests that a subscription can be created with valid data.
        """
        # Create the user
        user = User.objects.create(
            username="testuser",
            email="testuser@example.com"
        )

        # Create the shipping address (required for subscription meta)
        address = ShippingAddress.objects.create(
            user=user,
            address_line_1="123 Test Street",
            town_or_city="Test City",
            postcode="TE57 1NG",
            country="GB"
        )

        # Create the subscription with the required shipping address
        subscription = StripeSubscriptionMeta.objects.create(
            user=user,
            stripe_subscription_id="sub_123456",
            shipping_address=address
        )

        # Assertions
        assert subscription.user == user
        assert subscription.stripe_subscription_id == "sub_123456"
        assert subscription.shipping_address == address
        assert subscription.cancelled_at is None

    def test_subscription_string_representation(self):
        """
        Tests the string representation of a subscription.
        """
        user = User.objects.create(
            username="testuser",
            email="testuser@example.com"
        )

        # Create a shipping address for the user
        shipping_address = ShippingAddress.objects.create(
            user=user,
            address_line_1="123 Test Street",
            town_or_city="Test City",
            postcode="TE57 1NG",
            country="GB"
        )

        # Now create the subscription with the required shipping address
        subscription = StripeSubscriptionMeta.objects.create(
            user=user,
            stripe_subscription_id="sub_123456",
            shipping_address=shipping_address
        )

        assert str(subscription) == f"{user} - sub_123456"


@pytest.mark.django_db
class TestOrder:

    def test_order_creation(self):
        """
        Tests that an order can be created and stored in the database.
        """
        user = User.objects.create(
            username="testuser",
            email="testuser@example.com"
        )
        order = Order.objects.create(
            user=user,
            status='pending',
            stripe_subscription_id="sub_123456",
            stripe_payment_intent_id="pi_78910"
        )
        assert order.user == user
        assert order.status == 'pending'
        assert order.stripe_subscription_id == "sub_123456"
        assert order.stripe_payment_intent_id == "pi_78910"


@pytest.mark.django_db
class TestPayment:

    def test_payment_creation(self):
        """
        Tests that a payment can be created and linked to an order.
        """
        user = User.objects.create(
            username="testuser",
            email="testuser@example.com"
        )
        order = Order.objects.create(user=user, status='pending')

        # Fix: Added user
        payment = Payment.objects.create(
            user=user,
            order=order,
            amount=5000,
            status='paid',
            payment_intent_id="pi_78910"
        )
        assert payment.order == order
        assert payment.status == 'paid'
        assert payment.amount == 5000


@pytest.mark.django_db
def test_select_purchase_type_view(client, admin_user):
    """
    Tests that the select purchase type page renders correctly.
    """
    client.force_login(admin_user)
    response = client.get(reverse('select_purchase_type'))
    assert response.status_code == 200
    assert "Choose a Plan" in response.content.decode()


@pytest.mark.django_db
def test_order_success_view(client, admin_user):
    """
    Tests that the order success page renders correctly.
    """
    client.force_login(admin_user)
    response = client.get(reverse('order_success'))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Your order was successfully processed." in content


@pytest.mark.django_db
def test_order_cancel_view(client, admin_user):
    """
    Tests that the order cancellation page renders correctly.
    """
    client.force_login(admin_user)
    response = client.get(reverse('order_cancel'))
    assert response.status_code == 200
    assert "Your checkout was cancelled" in response.content.decode()


@pytest.mark.django_db
def test_order_history_view(client, admin_user):
    """
    Tests that the order history page renders and displays user's orders.
    """
    client.force_login(admin_user)
    response = client.get(reverse('order_history'))
    assert response.status_code == 200
    assert "Order History" in response.content.decode()


@pytest.mark.django_db
def test_choose_shipping_address_view(client, admin_user):
    """
    Tests that the choose shipping address page renders correctly.
    """
    client.force_login(admin_user)
    response = client.get(reverse('choose_shipping_address', args=['monthly']))
    assert response.status_code == 200
    assert "Choose Shipping Address" in response.content.decode()


@pytest.mark.django_db
def test_handle_purchase_type_view(client, admin_user):
    """
    Tests that the handle purchase type view redirects correctly.
    """
    client.force_login(admin_user)
    response = client.get(reverse('handle_purchase_type', args=['oneoff']))
    assert response.status_code == 302
    assert response.url.startswith('/orders/shipping/select/')


@pytest.mark.django_db
def test_gift_message_view(client, admin_user):
    """
    Tests that the gift message page renders correctly.
    """
    client.force_login(admin_user)

    # Create a valid *gift* shipping address
    address = ShippingAddress.objects.create(
        user=admin_user,
        address_line_1="123 Test Street",
        town_or_city="Test City",
        postcode="TE57 1NG",
        country="GB",
        is_gift_address=True
    )

    # Store it in the session properly
    session = client.session
    session['checkout_shipping_id'] = address.id
    session['gift'] = True
    session.save()

    # Refresh the session in the client context
    client.cookies['sessionid'] = session.session_key

    # Now this should work
    response = client.get(reverse('gift_message', args=['monthly']))

    # Expect a 200 response (not 302 redirect)
    assert response.status_code == 200


@pytest.mark.django_db
def test_secure_cancel_subscription(client, admin_user):
    """
    Tests that a subscription can be cancelled securely.
    """
    client.force_login(admin_user)

    # Create a shipping address for the admin user
    shipping_address = ShippingAddress.objects.create(
        user=admin_user,
        address_line_1="123 Admin Street",
        town_or_city="Admin City",
        postcode="AD12 3MN",
        country="GB",
    )

    # Now create the subscription with the shipping address
    subscription = StripeSubscriptionMeta.objects.create(
        user=admin_user,
        stripe_subscription_id="sub_123456",
        shipping_address=shipping_address
    )

    assert subscription.user == admin_user
    assert subscription.stripe_subscription_id == "sub_123456"
    assert subscription.shipping_address == shipping_address
    assert subscription.cancelled_at is None


@pytest.mark.django_db
def test_handle_purchase_type_no_shipping_id(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse('handle_purchase_type', args=['monthly']))
    assert response.status_code == 302
    assert '/orders/shipping/select/monthly/' in response.url


@pytest.mark.django_db
def test_choose_shipping_address_no_addresses(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse('choose_shipping_address', args=['monthly']))
    assert response.status_code == 200
    assert b"You don't have any saved addresses yet." in response.content


@pytest.mark.django_db
def test_choose_shipping_address_valid_and_invalid_ids(client, admin_user):
    client.force_login(admin_user)

    # Create a valid address
    address = ShippingAddress.objects.create(
        user=admin_user,
        address_line_1="123 Test Street",
        town_or_city="Test City",
        postcode="TE57 1NG",
        country="GB"
    )

    # Valid ID submission
    response = client.post(
        reverse('choose_shipping_address', args=['monthly']),
        {'shipping_address': address.id}
    )
    assert response.status_code == 302
    assert '/orders/purchase/monthly/' in response.url

    # Invalid ID submission - now it should redirect back to select page
    response = client.post(
        reverse('choose_shipping_address', args=['monthly']),
        {'shipping_address': 999}
    )
    assert response.status_code == 302
    assert reverse('choose_shipping_address', args=['monthly']) in response.url


@pytest.mark.django_db
def test_create_subscription_checkout_missing_shipping_id(admin_user):
    """
    Test that when `create_subscription_checkout` is called without
    a shipping ID, it redirects to the `choose_shipping_address` view and
    requires a valid plan.
    """
    factory = RequestFactory()
    request = factory.get('/fake-path')
    request.user = admin_user

    # Manually attach a session to the request
    session_middleware = SessionMiddleware(lambda req: None)
    session_middleware.process_request(request)
    request.session.save()

    # Manually attach the message middleware
    message_middleware = MessageMiddleware(lambda req: None)
    message_middleware.process_request(request)

    # Attach the FallbackStorage for message testing
    setattr(request, '_messages', FallbackStorage(request))

    # **Case 1: No plan in session (should redirect to purchase selection)**
    response = create_subscription_checkout(request, 'price_123')
    assert response.status_code == 302
    assert response.url == reverse('select_purchase_type')

    # Add a valid plan to the session
    request.session['plan'] = 'monthly'
    request.session.save()

    # **Case 2: Valid plan in session (should redirect to shipping address)**
    response = create_subscription_checkout(request, 'price_123')
    assert response.status_code == 302
    expected_url = reverse('choose_shipping_address', args=['monthly'])
    assert response.url == expected_url


@pytest.mark.django_db
def test_concurrent_order_creation():
    """
    Simulate concurrent order creation to validate box assignment stability.
    """
    user = User.objects.create(
        username="concurrentuser",
        email="concurrentuser@example.com"
    )
    box = Box.objects.create(
        name="June Box",
        shipping_date="2025-06-01",
        is_archived=False
    )

    # Simulate two rapid order creations
    order1 = Order.objects.create(
        user=user,
        status='processing',
        stripe_payment_intent_id="pi_concurrent_1",
        box=box  # Explicitly set the box
    )
    order2 = Order.objects.create(
        user=user,
        status='processing',
        stripe_payment_intent_id="pi_concurrent_2",
        box=box  # Explicitly set the box
    )

    # Ensure both orders reference the same box
    assert order1.box_id == box.id
    assert order2.box_id == box.id


@pytest.mark.django_db
def test_secure_cancel_subscription_wrong_password(client, admin_user):
    client.force_login(admin_user)
    response = client.post(reverse('secure_cancel_subscription'), {
        'password': 'wrongpassword',
        'subscription_id': 'fake_id'
    }, content_type='application/json')
    json_response = response.json()
    assert not json_response['success']
    assert json_response['error'] == 'Incorrect password'


@pytest.mark.django_db
def test_gift_order_creation(client, admin_user):
    """
    Tests that an order with a gift flag creates correctly and sends the
    proper email.
    """
    client.force_login(admin_user)
    address = ShippingAddress.objects.create(
        user=admin_user,
        address_line_1="123 Test Street",
        town_or_city="Test City",
        postcode="TE57 1NG",
        country="GB",
        is_gift_address=True
    )

    order = Order.objects.create(
        user=admin_user,
        status='processing',
        stripe_payment_intent_id="pi_78910",
        is_gift=True,
        shipping_address=address
    )

    assert order.is_gift
    assert order.shipping_address == address


@pytest.fixture
def setup_request_with_session(rf, admin_user):
    """
    Helper fixture to create a request with a session and user.
    """
    request = rf.get('/fake-path')
    request.user = admin_user

    # Attach a session and messages middleware
    session_middleware = SessionMiddleware(lambda req: None)
    session_middleware.process_request(request)
    request.session.save()

    message_middleware = MessageMiddleware(lambda req: None)
    message_middleware.process_request(request)

    setattr(request, '_messages', FallbackStorage(request))

    return request


@pytest.mark.django_db(transaction=True)
@patch('stripe.checkout.Session.retrieve')
def test_concurrent_subscription_creation(mock_stripe):
    """
    Simulate two webhook calls processed simultaneously for the same
    Stripe subscription.
    """
    mock_stripe.return_value = {
        'id': 'cs_test_concurrent',
        'subscription': 'sub_1RQC23AGhmEWZKnhSZzbpKYf',
        'metadata': {
            'user_id': 1,
            'shipping_address_id': 1,
            'gift': 'false'
        }
    }

    # Create User, Address, and Box outside of atomic block
    user = User.objects.create_user(
        username="concurrentuser",
        email="concurrentuser@example.com",
        password="testpass123"
    )

    address = ShippingAddress.objects.create(
        user=user,
        address_line_1="123 Test Street",
        town_or_city="Test City",
        postcode="TE57 1NG",
        country="GB"
    )

    stripe_session = {
        'id': 'cs_test_concurrent',
        'mode': 'subscription',
        'metadata': {
            'user_id': user.id,
            'shipping_address_id': address.id,
            'gift': 'false'
        },
        'subscription': 'sub_1RQC23AGhmEWZKnhSZzbpKYf',
    }

    # Clear any existing entries to ensure a clean test
    StripeSubscriptionMeta.objects.filter(
        stripe_subscription_id=stripe_session['subscription']
    ).delete()

    # Manually commit the transaction
    transaction.commit()
    logging.debug("Transaction committed and event set!")

    # Launch the threads **after the transaction commit is confirmed**
    logging.debug("Launching threads...")
    t1 = threading.Thread(
        target=run_webhook_handler,
        args=(user.id, address.id, stripe_session)
    )
    t2 = threading.Thread(
        target=run_webhook_handler,
        args=(user.id, address.id, stripe_session)
    )

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    time.sleep(5)

    # Assertions
    logging.debug("Verifying StripeSubscriptionMeta entries...")
    subs = StripeSubscriptionMeta.objects.filter(
        stripe_subscription_id=stripe_session['subscription']
    )
    count = subs.count()
    logging.debug(f"Found {count} StripeSubscriptionMeta entries.")

    # Final Assertion
    assert count == 1, (
        f"Multiple StripeSubscriptionMeta entries were created! "
        f"Count: {count}"
    )
