"""
dashboard/forms.py

Defines forms used in the admin dashboard for managing boxes, products, and
users.

- BoxForm: used for creating and editing subscription boxes
- ProductForm: used for adding/editing products that appear in boxes
- UserEditForm: allows admin users to update username, email, and staff status

All forms use MaterializeCSS-friendly widgets for consistent styling.
"""
from django import forms
from django.contrib.auth import get_user_model
from datetime import timedelta, date
from django.core.exceptions import ValidationError
from boxes.models import Box, BoxProduct

User = get_user_model()


def last_day_of_month(any_day):
    """Return the last day of the month for the given date."""
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


class BoxForm(forms.ModelForm):
    """
    Form for creating and editing Box instances in the admin dashboard.
    Includes custom input formats for the shipping date field to support both
    UK and ISO date formats. Materialize-compatible widgets are used for
    styling.
    """
    def clean_name(self):
        name = self.cleaned_data['name']
        if (
            Box.objects.filter(name__iexact=name)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("A box with this name already exists.")
        return name

    def clean_description(self):
        desc = self.cleaned_data.get('description', '')
        if len(desc) > 300:
            raise forms.ValidationError(
                "Description must be 300 characters or fewer."
            )
        return desc

    def clean_image(self):
        """
        Ensure the uploaded image is actually an image file.
        """
        image = self.cleaned_data.get('image')
        if image:
            # Check if it's a CloudinaryResource or a standard file
            if hasattr(image, 'content_type'):
                # This means it's a freshly uploaded image
                if not image.content_type.startswith('image/'):
                    raise ValidationError(
                        "The uploaded file is not a valid image."
                    )
            else:
                # If it's a CloudinaryResource, we need to trust it's valid
                # You can extend this with Cloudinary's API call to
                # double-check if needed
                from cloudinary.api import resource
                try:
                    metadata = resource(image.public_id)
                    if 'image' not in metadata.get('resource_type', ''):
                        raise ValidationError(
                            "The saved file is not a valid image."
                        )
                except Exception as e:
                    raise ValidationError(
                        f"Could not verify the image from Cloudinary: {e}"
                    )
        return image

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Get the last day of the month for the shipping date
        last_day = last_day_of_month(instance.shipping_date)

        # Only archive if the current date is past the end of that month
        if date.today() > last_day:
            instance.is_archived = True
        else:
            instance.is_archived = False

        if commit:
            instance.save()
        return instance

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
