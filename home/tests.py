import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_register_form_required_fields():
    """
    Ensure required fields trigger validation errors if left empty.
    """
    client = Client()
    response = client.post(reverse('register'), data={})
    assert "This field is required." in response.content.decode()
    assert response.status_code == 200

@pytest.mark.django_db
def test_register_form_max_length():
    """
    Test maximum length constraints on fields.
    """
    client = Client()
    long_username = "a" * 31
    long_email = "a" * 101 + "@example.com"
    response = client.post(reverse('register'), data={
        'username': long_username,
        'email': long_email,
        'password1': 'TestPass123!',
        'password2': 'TestPass123!'
    })
    content = response.content.decode()
    assert "Ensure this value has at most 30 characters" in content
    assert "Ensure this value has at most 100 characters" in content
    assert response.status_code == 200

@pytest.mark.django_db
def test_register_form_invalid_email():
    """
    Test form submission with invalid email formats.
    """
    client = Client()
    invalid_emails = ["plainaddress", "@missingusername.com", "username@.com"]
    for email in invalid_emails:
        response = client.post(reverse('register'), data={
            'username': 'ValidUsername',
            'email': email,
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        })
        assert "Enter a valid email address." in response.content.decode()
        assert response.status_code == 200

@pytest.mark.django_db
def test_register_form_password_mismatch():
    """
    Test password mismatch error handling.
    """
    client = Client()
    response = client.post(reverse('register'), data={
        'username': 'ValidUsername',
        'email': 'test@example.com',
        'password1': 'TestPass123!',
        'password2': 'DifferentPass123!'
    })
    assert "The two password fields didn’t match." in response.content.decode()
    assert response.status_code == 200

@pytest.mark.django_db
def test_register_form_success():
    """
    Test successful form submission.
    """
    client = Client()
    response = client.post(reverse('register'), data={
        'username': 'ValidUsername',
        'email': 'test@example.com',
        'password1': 'TestPass123!',
        'password2': 'TestPass123!'
    })
    assert response.status_code == 302  # Should redirect on success
    assert User.objects.filter(username='ValidUsername').exists()
