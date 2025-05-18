import json

from django.contrib.auth.models import User
from django.core import mail
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from users.models import ShippingAddress
from orders.models import Order, StripeSubscriptionMeta


class TestUsersViews(TestCase):

    def setUp(self):
        # Create the test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepass'
        )

        # Create the address and assign to self
        self.address = ShippingAddress.objects.create(
            user=self.user,
            recipient_f_name='Test',
            recipient_l_name='User',
            address_line_1='123 Test Street',
            town_or_city='Test City',
            postcode='TE57 1NG',
            country='GB',
            is_default=True
        )

        self.client.login(username='testuser', password='securepass')
        self.factory = RequestFactory()

    def test_account_view(self):
        request = self.factory.get(reverse('account'))
        request.user = self.user
        response = self.client.get(reverse('account'))
        self.assertEqual(response.status_code, 200)

    def test_edit_account(self):
        data = {'username': 'updateduser'}
        response = self.client.post(reverse('edit_account'), data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_edit_address(self):
        data = {
            'recipient_f_name': 'Jane',
            'recipient_l_name': 'Doe',
            'address_line_1': '789 Updated Street',
            'town_or_city': 'Updated City',
            'postcode': 'UC57 1NG',
            'country': 'GB',
            'is_default': False,
            'phone_number': '0123456789'
        }
        response = self.client.post(
            reverse('edit_address', args=[self.address.id]), data
        )
        if response.status_code == 200:
            print(response.context['form'].errors)
        self.assertEqual(response.status_code, 302)

    def test_add_address(self):
        data = {
            'recipient_f_name': 'John',
            'recipient_l_name': 'Doe',
            'address_line_1': '456 New Street',
            'town_or_city': 'New City',
            'postcode': 'NC57 1NG',
            'country': 'GB',
            'is_default': False,
            'phone_number': '0123456789'
        }
        response = self.client.post(reverse('add_address'), data)
        self.assertEqual(response.status_code, 302)

    def test_set_default_address(self):
        new_address = ShippingAddress.objects.create(
            user=self.user,
            recipient_f_name='John',
            recipient_l_name='Smith',
            address_line_1='222 New Road',
            town_or_city='Another City',
            postcode='AN57 1NG',
            country='GB',
            is_default=False
        )
        response = self.client.post(
            reverse('set_default_address', args=[new_address.id])
        )
        self.assertEqual(response.status_code, 302)
        new_address.refresh_from_db()
        self.assertTrue(new_address.is_default)

    def test_secure_delete_address(self):
        data = {'password': 'securepass'}
        response = self.client.post(
            reverse('secure_delete_address', args=[self.address.id]),
            content_type='application/json', data=json.dumps(data)
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            ShippingAddress.objects.filter(id=self.address.id).exists()
        )

    def test_password_reset_request(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password reset on', mail.outbox[0].subject)

    def test_password_reset_confirm(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = 'set-password-token'
        response = self.client.get(
            reverse('password_reset_confirm', args=[uid, token])
        )
        self.assertEqual(response.status_code, 200)

    def test_secure_delete_account(self):
        data = {'password': 'securepass'}
        response = self.client.post(reverse('secure_delete_account'),
                                    content_type='application/json',
                                    data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='testuser')


class ShippingAddressTest(TestCase):

    def test_address_cannot_be_deleted_if_linked_to_order_or_subscription(self):
        user = User.objects.create(username="testuser")
        address = ShippingAddress.objects.create(
            user=user,
            address_line_1="123 Test St",
            town_or_city="Test City",
            postcode="TEST123",
            country="GB"
        )

        # Create a pending order linked to this address
        Order.objects.create(
            user=user,
            shipping_address=address,
            status='pending'
        )

        self.assertFalse(address.can_be_deleted())

        # Create an active subscription
        StripeSubscriptionMeta.objects.create(
            user=user,
            shipping_address=address,
            stripe_subscription_id="sub_123",
            cancelled_at=None
        )

        self.assertFalse(address.can_be_deleted())
