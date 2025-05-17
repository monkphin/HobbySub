from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.core import mail
from hobbyhub.mail import (
    send_gift_notification_to_recipient,
    send_gift_confirmation_to_sender,
    send_order_confirmation_email,
    send_subscription_confirmation_email,
    send_payment_failed_email,
    send_upcoming_renewal_email
)
from hobbyhub.utils import (
    alert,
    get_user_default_shipping_address,
    build_shipping_details,
    get_gift_metadata,
    get_subscription_duration_display,
    get_subscription_status
)
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from users.models import User, ShippingAddress
from datetime import datetime, timedelta
from django.utils import timezone

class TestMailFunctions(TestCase):

    def test_send_gift_notification_to_recipient(self):
        send_gift_notification_to_recipient('test@example.com', 'Sender Name', 'Enjoy this!', 'Recipient Name')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])
        self.assertIn('Enjoy this!', mail.outbox[0].body)

    def test_send_gift_confirmation_to_sender(self):
        user = User.objects.create(username="testuser", email="sender@example.com")
        send_gift_confirmation_to_sender(user, 'Recipient Name')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['sender@example.com'])
        self.assertIn('Recipient Name', mail.outbox[0].body)

    def test_send_order_confirmation_email(self):
        user = User.objects.create(username="testuser", email="user@example.com")
        send_order_confirmation_email(user, 1234)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Order #1234', mail.outbox[0].subject)

    def test_send_subscription_confirmation_email(self):
        user = User.objects.create(username="testuser", email="user@example.com")
        send_subscription_confirmation_email(user, "Monthly Plan")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Monthly Plan', mail.outbox[0].body)

    def test_send_payment_failed_email(self):
        user = User.objects.create(username="testuser", email="user@example.com")
        send_payment_failed_email(user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Payment Failed', mail.outbox[0].subject)

    def test_send_upcoming_renewal_email(self):
        user = User.objects.create(username="testuser", email="user@example.com")
        send_upcoming_renewal_email(user, timezone.now() + timedelta(days=7))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Your subscription is set to renew', mail.outbox[0].body)



class TestUtilsFunctions(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="testuser", email="user@example.com")
        self.address = ShippingAddress.objects.create(
            user=self.user,
            address_line_1="123 Test St",
            town_or_city="Test City",
            postcode="TE57 1NG",
            country="GB",
            is_gift_address=False
        )
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        middleware = SessionMiddleware(lambda req: None)  # Fix: added lambda
        middleware.process_request(self.request)
        self.request.session.save()


    def test_alert(self):
        alert(self.request, "info", "Test message")
        self.assertIn("Test message", self.request.session.get('_messages')._queued_messages[0].message)

    def test_get_user_default_shipping_address(self):
        self.request.user = self.user
        address, _ = get_user_default_shipping_address(self.request)
        self.assertEqual(address, self.address)


    def test_build_shipping_details(self):
        shipping_data = build_shipping_details(self.address)
        self.assertEqual(shipping_data['address']['line1'], "123 Test St")
        self.assertEqual(shipping_data['address']['postal_code'], "TE57 1NG")

    def test_get_gift_metadata(self):
        metadata = get_gift_metadata(
            form_data={
                'recipient_name': 'John Doe',
                'recipient_email': 'john.doe@example.com',
                'sender_name': 'Jane Smith',
                'gift_message': 'Happy Birthday!'
            },
            user_id=self.user.id,
            address_id=self.address.id
        )
        self.assertEqual(metadata['recipient_name'], 'John Doe')
        self.assertEqual(metadata['gift_message'], 'Happy Birthday!')

    def test_get_subscription_duration_display(self):
        sub_date = timezone.now() - timedelta(days=30)
        display = get_subscription_duration_display(sub_date, 3)
        self.assertIn("ends", display)

    def test_get_subscription_status(self):
        sub_date = timezone.now() - timedelta(days=30)
        status = get_subscription_status(sub_date, 3)
        self.assertEqual(status, "Active")
