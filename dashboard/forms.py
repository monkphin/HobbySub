from django import forms 

from boxes.models import Box

class BoxForm(forms.ModelForm):
    class Meta:
        model = Box
        fields = ['name','description','image_url','shipping_date','is_archived']