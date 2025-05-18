from django.contrib import admin

from .models import Box, BoxProduct


# Inline admin setup for managing BoxProducts within the Box admin interface.
class BoxProductInline(admin.TabularInline):
    model = BoxProduct
    # Displays one empty row for adding new BoxProducts inline.
    extra = 1


# Registers the Box model with custom admin configuration.
@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    # Fields shown in list view.
    list_display = ('name', 'shipping_date', 'is_archived')
    # Auto-generate slug from name.
    prepopulated_fields = {"slug": ("name",)}
    # Inline editing of BoxProducts.
    inlines = [BoxProductInline]


# Registers the BoxProduct model for direct admin access.
@admin.register(BoxProduct)
class BoxProductAdmin(admin.ModelAdmin):
    # Fields shown in list view.
    list_display = ('name', 'box', 'quantity')
