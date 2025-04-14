from django import forms 

class PreCheckoutForm (forms.Form):
    recipient_name = forms.CharField(max_length=100, required=False)
    sender_name = forms.CharField(max_length=100, required=False)
    gift_message = forms.CharField(max_length=250, required=False)