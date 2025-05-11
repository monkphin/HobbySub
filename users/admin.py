from django.contrib import admin
from .models import ShippingAddress
from django.contrib.auth.models import User

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipient_f_name',
        'recipient_l_name',
        'postcode',
        'is_default',
        'stripe_customer_id',
    )
    search_fields = (
        'recipient_f_name',
        'recipient_l_name',
        'postcode',
        'user__username',
        'user__profile__stripe_customer_id',
    )
    list_filter = ('is_default', 'country')
    
    def stripe_customer_id(self, obj):
        # This will directly display the stripe_customer_id if available
        return obj.user.profile.stripe_customer_id if hasattr(obj.user, 'profile') else 'N/A'
    stripe_customer_id.short_description = 'Stripe Customer ID'
