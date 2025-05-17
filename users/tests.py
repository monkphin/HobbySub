from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail
from django.shortcuts import get_object_or_404
from users.models import ShippingAddress
from users.forms import AddAddressForm, ChangePassword
from users.views import (
    account_view,
    edit_account,
    change_email,
    change_password,
    password_reset_request,
    password_reset_confirm,
    add_address,
    edit_address,
    set_default_address,
    secure_delete_account,
    secure_delete_address,
)
from hobbyhub.mail import send_password_reset_email
from django.http import JsonResponse
import json


class TestUsersViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='securepass')
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
        self.factory = RequestFactory()
        self.client.login(username='testuser', password='securepass')

    def test_account_view(self):
        request = self.factory.get(reverse('account'))
        request.user = self.user
        response = account_view(request)
        self.assertEqual(response.status_code, 200)

    def test_edit_account(self):
        data = {'username': 'updateduser'}
        response = self.client.post(reverse('edit_account'), data)
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')


from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class TestUsersViews(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepass'
        )
        self.client.login(username='testuser', password='securepass')

    def test_change_email(self):
        """
        Test the change email process, expecting a JSON response with success status.
        """
        # Define the data to post
        data = {
            'new_email': 'new@example.com',
            'password': 'securepass'
        }

        # Post to the view with `application/json` instead of `multipart/form-data`
        response = self.client.post(
            reverse('change_email'),
            data=json.dumps(data),
            content_type='application/json'
        )

        # Refresh user data from the database
        self.user.refresh_from_db()

        # Assertions
        self.assertEqual(response.status_code, 200)  # ✅ Now expecting a 200 JSON response
        self.assertJSONEqual(response.content, {"success": True})  # ✅ Checking the JSON body
        self.assertEqual(self.user.email, 'new@example.com')  # ✅ Confirm the email actually changed




    def test_change_password(self):
        # Set the password for the user
        self.user.set_password('securepass')
        self.user.save()

        data = {
            'current_password': 'securepass',  # <-- Fixed this
            'new_password1': 'newsecurepass',
            'new_password2': 'newsecurepass',
        }
        response = self.client.post(reverse('change_password'), data)
        if response.status_code == 200:
            print(response.context['form'].errors)  # This will show the form errors
        self.assertEqual(response.status_code, 302)  # Should redirect on success



    def test_add_address(self):
        data = {
            'recipient_f_name': 'John',
            'recipient_l_name': 'Doe',
            'address_line_1': '456 New Street',
            'town_or_city': 'New City',
            'postcode': 'NC57 1NG',
            'country': 'GB',
            'is_default': False,
            'phone_number': '0123456789'  # <-- Added this line
        }
        response = self.client.post(reverse('add_address'), data)
        if response.status_code == 200:
            print(response.context['form'].errors)  # This will display form errors if they exist
        self.assertEqual(response.status_code, 302)  # Expecting a redirect on success


    def test_edit_address(self):
        data = {
            'recipient_f_name': 'Jane',
            'recipient_l_name': 'Doe',
            'address_line_1': '789 Updated Street',
            'town_or_city': 'Updated City',
            'postcode': 'UC57 1NG',
            'country': 'GB',
            'is_default': False,
            'phone_number': '0123456789'  # <-- Added this line
        }
        response = self.client.post(reverse('edit_address', args=[self.address.id]), data)
        if response.status_code == 200:
            print(response.context['form'].errors)  # Show form errors if it fails
        self.assertEqual(response.status_code, 302)  # Expecting a redirect on success



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
        response = self.client.post(reverse('set_default_address', args=[new_address.id]))
        self.assertEqual(response.status_code, 302)
        new_address.refresh_from_db()
        self.assertTrue(new_address.is_default)

    def test_secure_delete_address(self):
        data = {'password': 'securepass'}
        response = self.client.post(reverse('secure_delete_address', args=[self.address.id]),
                                    content_type='application/json', data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ShippingAddress.objects.filter(id=self.address.id).exists())

    def test_password_reset_request(self):
        response = self.client.post(reverse('password_reset'), {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 302)  # Redirect to password reset done
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password reset on', mail.outbox[0].subject)

    def test_password_reset_confirm(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = 'set-password-token'
        response = self.client.get(reverse('password_reset_confirm', args=[uid, token]))
        self.assertEqual(response.status_code, 200)

    def test_secure_delete_account(self):
        data = {'password': 'securepass'}
        response = self.client.post(reverse('secure_delete_account'), content_type='application/json', data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='testuser')
