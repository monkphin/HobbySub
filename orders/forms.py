"""
orders/forms.py

Defines form classes used within the orders app.
Includes optional fields for personalizing gift subscriptions.
"""

from django import forms 

class PreCheckoutForm (forms.Form):
    """
    A simple form used during the checkout process for collecting optional gift details.

    Fields:
        - recipient_name: Optional name of the gift recipient.
        - sender_name: Optional name of the sender.
        - gift_message: Optional short message to include with the gift.
    """
    recipient_name = forms.CharField(max_length=100, required=False)
    sender_name = forms.CharField(max_length=100, required=False)
    gift_message = forms.CharField(max_length=250, required=False)