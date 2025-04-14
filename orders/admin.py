from django.contrib import admin
from .models import Order, StripeSubscriptionMeta, Payment

admin.site.register(Order)
admin.site.register(StripeSubscriptionMeta)
admin.site.register(Payment)