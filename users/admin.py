from django.contrib import admin
from .models import ShippingAddress


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipient_f_name', 'recipient_l_name', 'postcode', 'is_default')
    search_fields = ('recipient_f_name', 'recipient_l_name', 'postcode', 'user__username')
    list_filter = ('is_default', 'country')