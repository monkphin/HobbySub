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
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django import forms


# Local Imports
from hobbyhub.mail import send_auto_archive_notification
from boxes.models import Box, BoxProduct
from hobbyhub.utils import alert

User = get_user_model()


class BoxForm(forms.ModelForm):
    """
    Form for creating and editing Box instances in the admin dashboard.
    Includes custom input formats for the shipping date field to support both
    UK and ISO date formats. Materialize-compatible widgets are used for
    styling.
    """

    def clean_name(self):
        name = self.cleaned_data['name']
        if Box.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A box with this name already exists.")
        return name

    def clean_description(self):
        desc = self.cleaned_data.get('description', '')
        if len(desc) > 300:
            raise forms.ValidationError("Description must be 300 characters or fewer.")
        return desc

    shipping_date = forms.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(
            attrs={
                'class': 'datepicker',
                'placeholder': 'DD/MM/YYYY',
                'autocomplete': 'off',
            }
        )
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
            'description': forms.Textarea(
                attrs={
                    'class': 'materialize-textarea validate',
                    'maxlength': 300,
                    'rows': 4
                }
            ),
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
