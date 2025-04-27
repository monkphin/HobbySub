"""
dashboard/forms.py

Defines forms used in the admin dashboard for managing boxes, products, and
users.

- BoxForm: used for creating and editing subscription boxes
- ProductForm: used for adding/editing products that appear in boxes
- UserEditForm: allows admin users to update username, email, and staff status

All forms use MaterializeCSS-friendly widgets for consistent styling.
"""

# Django Imports
from django import forms
from django.contrib.auth import get_user_model

# Local Imports
from boxes.models import Box, BoxProduct

User = get_user_model()


class BoxForm(forms.ModelForm):
    """
    Form for creating and editing Box instances in the admin dashboard.
    Includes custom input formats for the shipping date field to support both
    UK and ISO date formats. Materialize-compatible widgets are used for
    styling.
    """
    shipping_date = forms.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={'class': 'datepicker'})
    )

    class Meta:
        model = Box
        fields = [
            'name',
            'description',
            'image',
            'shipping_date',
            'is_archived'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'validate'}),
            'description': forms.TextInput(
                attrs={'class': 'materialize-textarea'}
            ),
            'shipping_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'is_archived': forms.CheckboxInput(),
        }


class ProductForm(forms.ModelForm):
    """
    Form for creating and editing BoxProduct instances.
    Supports linking products to a box.
    Uses Materialize styling for improved admin UX.
    Quantity must be 1 or greater.
    """
    quantity = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 11)],
        widget=forms.Select(attrs={'class': 'browser-default'})
    )

    class Meta:
        model = BoxProduct
        fields = ['box', 'name', 'image', 'description', 'quantity']
        widgets = {
            'box': forms.Select(attrs={'class': 'browser-default'}),
            'name': forms.TextInput(attrs={'class': 'validate'}),
            'description': forms.Textarea(
                attrs={'class': 'materialize-textarea'}
            ),
        }


class UserEditForm(forms.ModelForm):
    """
    Form for admin editing of user accounts.
    Allows changing username, email, and admin/staff status.
    'is_staff' is labeled as 'Admin user?' for clarity.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'validate'}),
            'email': forms.EmailInput(attrs={'class': 'validate'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'filled-in'}),
        }
        labels = {
            'is_staff': 'Admin user?',
        }
