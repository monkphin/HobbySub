from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.test import RequestFactory, TestCase
from django.utils import timezone

from hobbyhub.mail import (
    send_gift_confirmation_to_sender,
    send_gift_notification_to_recipient,
    send_order_confirmation_email,
    send_payment_failed_email,
    send_subscription_confirmation_email,
    send_upcoming_renewal_email
)
from hobbyhub.utils import (
    alert, build_shipping_details, get_gift_metadata,
    get_subscription_duration_display,
    get_subscription_status,
    get_user_default_shipping_address
)
from users.models import ShippingAddress, User


class TestMailFunctions(TestCase):

    def test_send_gift_notification_to_recipient(self):
        send_gift_notification_to_recipient(
            'test@example.com',
            'Sender Name',
            'Enjoy this!',
            'Recipient Name'
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])
        self.assertIn('Enjoy this!', mail.outbox[0].body)

    def test_send_gift_confirmation_to_sender(self):
        user = User.objects.create(
            username="testuser",
            email="sender@example.com"
        )
        send_gift_confirmation_to_sender(user, 'Recipient Name')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['sender@example.com'])
        self.assertIn('Recipient Name', mail.outbox[0].body)

    def test_send_order_confirmation_email(self):
        user = User.objects.create(
            username="testuser",
            email="user@example.com"
        )
        send_order_confirmation_email(user, 1234)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Order #1234', mail.outbox[0].subject)

    def test_send_subscription_confirmation_email(self):
        user = User.objects.create(
            username="testuser",
            email="user@example.com"
        )
        send_subscription_confirmation_email(user, "Monthly Plan")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Monthly Plan', mail.outbox[0].body)

    def test_send_payment_failed_email(self):
        user = User.objects.create(
            username="testuser",
            email="user@example.com"
        )
        send_payment_failed_email(user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Payment Failed', mail.outbox[0].subject)

    def test_send_upcoming_renewal_email(self):
        user = User.objects.create(
            username="testuser",
            email="user@example.com"
        )
        send_upcoming_renewal_email(user, timezone.now() + timedelta(days=7))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Your subscription is set to renew', mail.outbox[0].body)


class TestUtilsFunctions(TestCase):

    def setUp(self):
        """
        Setup user, address, and request for testing.
        """
        # Create test user and address
        self.user = User.objects.create(
            username="testuser",
            email="user@example.com"
        )
        self.address = ShippingAddress.objects.create(
            user=self.user,
            address_line_1="123 Test St",
            town_or_city="Test City",
            postcode="TE57 1NG",
            country="GB",
            is_gift_address=False
        )

        # Set up request factory and middleware
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.user

        # Manually add the session middleware
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(self.request)
        self.request.session.save()

        # Manually add the message middleware to the request
        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(self.request)

    def test_alert(self):
        """
        Test that alert messages are properly added to the message framework.
        """
        alert(self.request, "info", "Test message")
        messages = list(get_messages(self.request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Test message")
        self.assertEqual(messages[0].level, 20)  # 20 is the level for INFO

    def test_get_user_default_shipping_address(self):
        # Set the address as the default
        self.address.is_default = True
        self.address.save()

        address, _ = get_user_default_shipping_address(self.request)
        self.assertEqual(address, self.address)

    def test_build_shipping_details(self):
        """
        Test building the shipping details from the address.
        """
        shipping_data = build_shipping_details(self.address)
        self.assertEqual(shipping_data['address']['line1'], "123 Test St")
        self.assertEqual(shipping_data['address']['postal_code'], "TE57 1NG")

    def test_get_gift_metadata(self):
        """
        Test that get_gift_metadata correctly builds metadata.
        """
        # Mock the form with cleaned_data
        form = MagicMock()
        form.cleaned_data = {
            'recipient_name': 'John Doe',
            'recipient_email': 'john.doe@example.com',
            'sender_name': 'Jane Smith',
            'gift_message': 'Happy Birthday!'
        }

        metadata = get_gift_metadata(
            form=form,
            user_id=self.user.id,
            address_id=self.address.id
        )

        self.assertEqual(metadata['recipient_name'], 'John Doe')
        self.assertEqual(metadata['recipient_email'], 'john.doe@example.com')
        self.assertEqual(metadata['sender_name'], 'Jane Smith')
        self.assertEqual(metadata['gift_message'], 'Happy Birthday!')
        self.assertEqual(metadata['user_id'], str(self.user.id))
        self.assertEqual(metadata['shipping_address_id'], str(self.address.id))

    def test_get_subscription_duration_display(self):
        # Mocking a StripeSubscriptionMeta instance
        mock_subscription = MagicMock()
        mock_subscription.stripe_price_id = 'price_123'
        mock_subscription.created_at = timezone.now() - timedelta(days=30)

        # Mock PLAN_MAP to return the expected duration and label
        with patch(
            'hobbyhub.utils.PLAN_MAP',
            {'price_123': (3, "3-month plan")}
        ):
            display = get_subscription_duration_display(mock_subscription)

        # Now assert that it contains the expected string
        self.assertIn("3-month plan", display)
        self.assertIn("ends", display)

    def test_get_subscription_status(self):
        # Mocking a StripeSubscriptionMeta instance
        mock_subscription = MagicMock()
        mock_subscription.cancelled_at = None  # Not cancelled
        mock_subscription.created_at = timezone.now() - timedelta(days=30)

        status = get_subscription_status(mock_subscription)

        # Check the status is what we expect
        self.assertEqual(status, "Active")
