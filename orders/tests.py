import pytest
from datetime import datetime
from django.utils import timezone
from orders.models import Order, Payment, StripeSubscriptionMeta
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.models import ShippingAddress
from django.utils import timezone


User = get_user_model()

@pytest.mark.django_db
class TestStripeSubscriptionMeta:

    def test_subscription_creation(self):
        """
        Tests that a subscription can be created with valid data.
        """
        user = User.objects.create(username="testuser", email="testuser@example.com")
        subscription = StripeSubscriptionMeta.objects.create(
            user=user,
            stripe_subscription_id="sub_123456"
        )
        assert subscription.user == user
        assert subscription.stripe_subscription_id == "sub_123456"
        assert subscription.cancelled_at is None

    def test_subscription_string_representation(self):
        """
        Tests the string representation of a subscription.
        """
        user = User.objects.create(username="testuser", email="testuser@example.com")
        subscription = StripeSubscriptionMeta.objects.create(
            user=user,
            stripe_subscription_id="sub_123456"
        )
        assert str(subscription) == f"{user} - sub_123456"

    def test_subscription_cascade_delete(self):
        """
        Tests that deleting a user cascades and deletes the subscription.
        """
        user = User.objects.create(username="testuser", email="testuser@example.com")
        StripeSubscriptionMeta.objects.create(
            user=user,
            stripe_subscription_id="sub_123456"
        )
        user.delete()
        assert not StripeSubscriptionMeta.objects.exists()


@pytest.mark.django_db
class TestOrder:

    def test_order_creation(self):
        """
        Tests that an order can be created and stored in the database.
        """
        user = User.objects.create(username="testuser", email="testuser@example.com")
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

    def test_order_string_representation(self):
        """
        Tests the string representation of an order.
        """
        user = User.objects.create(username="testuser", email="testuser@example.com")
        order = Order.objects.create(
            user=user,
            status='pending',
            stripe_subscription_id="sub_123456"
        )
        # ✅ This now matches the fixed model
        assert str(order) == f"Order #{order.id} - pending"

    def test_order_cascade_delete(self):
        """
        Tests that deleting a user cascades and deletes associated orders.
        """
        user = User.objects.create(username="testuser", email="testuser@example.com")
        Order.objects.create(user=user, status='pending')
        user.delete()
        assert not Order.objects.exists()


@pytest.mark.django_db
class TestPayment:

    def test_payment_creation(self):
        """
        Tests that a payment can be created and linked to an order.
        """
        user = User.objects.create(username="testuser", email="testuser@example.com")
        order = Order.objects.create(user=user, status='pending')
        
        # ✅ Fix: Added user
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

    def test_payment_string_representation(self):
        """
        Tests the string representation of a payment.
        """
        user = User.objects.create(username="testuser", email="testuser@example.com")
        order = Order.objects.create(user=user, status='pending')
        
        payment = Payment.objects.create(
            user=user,
            order=order,
            amount=5000,
            status='paid',
            payment_intent_id="pi_78910"
        )
        # ✅ This now matches the fixed model
        assert str(payment) == f"Payment for Order #{order.id} - paid"
        
    def test_payment_cascade_delete(self):
        """
        Tests that deleting an order cascades and deletes the associated payment.
        """
        user = User.objects.create(username="testuser", email="testuser@example.com")
        order = Order.objects.create(user=user, status='pending')
        
        # ✅ Fix: Added user
        Payment.objects.create(user=user, order=order, amount=5000, status='paid')
        order.delete()
        assert not Payment.objects.exists()

@pytest.mark.django_db
def test_order_start_view(client, admin_user):
    """
    Tests that the order start page renders correctly.
    """
    client.force_login(admin_user)
    response = client.get(reverse('order_start'))
    assert response.status_code == 200
    assert "started an order" in response.content.decode()

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
    assert "Your order was successfully processed." in response.content.decode()

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

    # ✅ Mock a shipping address in the session to bypass the redirect
    client.session['checkout_shipping_id'] = 1  # Example ID
    client.session.save()

    response = client.get(reverse('gift_message', args=['monthly']))
    assert response.status_code == 200
    assert "Enter your gift message" in response.content.decode()

@pytest.mark.django_db
def test_secure_cancel_subscription(client, admin_user):
    """
    Tests that a subscription can be cancelled securely.
    """
    client.force_login(admin_user)
    subscription = StripeSubscriptionMeta.objects.create(
        user=admin_user,
        stripe_subscription_id="sub_123456"
    )
    response = client.post(reverse('secure_cancel_subscription'), {
        'subscription_id': subscription.stripe_subscription_id,
        'password': 'admin_password'
    }, content_type='application/json')
    assert response.status_code == 200
    assert 'success' in response.json()

@pytest.mark.django_db
def test_order_success_clears_session(client, admin_user):
    """
    Tests that the session is cleared after order success.
    """
    client.force_login(admin_user)
    client.session['checkout_shipping_id'] = 123
    client.session.save()
    client.get(reverse('order_success'))
    assert 'checkout_shipping_id' not in client.session

@pytest.mark.django_db
def test_order_cancel_clears_session(client, admin_user):
    """
    Tests that the session is cleared after order cancel.
    """
    client.force_login(admin_user)
    client.session['checkout_shipping_id'] = 123
    client.session.save()
    client.get(reverse('order_cancel'))
    assert 'checkout_shipping_id' not in client.session
