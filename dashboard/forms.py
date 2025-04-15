from django import forms 

from boxes.models import Box

class BoxForm(forms.ModelForm):
    class Meta:
        model = Box
        fields = ['name','description','image_url','shipping_date','is_archived']
        widgets = {
            'name' : forms.TextInput(attrs={'class':'validate'}),
            'description' : forms.TextInput(attrs={'class':'materialize-textarea'}),
            'image_url' : forms.URLInput(attrs={'class': 'validate'}),
            'shipping_date' : forms.DateInput(attrs={'class': 'datepicker'}),
            'is_archived' : forms.CheckboxInput(),
        }