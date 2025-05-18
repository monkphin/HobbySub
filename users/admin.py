from django.contrib import admin
from .models import ShippingAddress


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipient_f_name',
        'recipient_l_name',
        'postcode',
        'is_default',
        'get_stripe_customer_id',  # Changed here
    )
    search_fields = (
        'recipient_f_name',
        'recipient_l_name',
        'postcode',
        'user__username',
        'user__profile__stripe_customer_id',
    )
    list_filter = ('is_default', 'country')

    def get_stripe_customer_id(self, obj):
        # This will directly display the stripe_customer_id if available
        return obj.user.profile.stripe_customer_id if hasattr(obj.user, 'profile') else 'N/A'
    get_stripe_customer_id.short_description = 'Stripe Customer ID'
