from django.contrib import admin

from .models import Order, Payment, StripeSubscriptionMeta

admin.site.register(Order)
admin.site.register(StripeSubscriptionMeta)
admin.site.register(Payment)
