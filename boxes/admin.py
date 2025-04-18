from django.contrib import admin
from .models import Box, BoxProduct


# Inline admin setup for managing BoxProducts directly within the Box admin interface.
# Uses a tabular layout for efficient editing of related BoxProduct entries.
class BoxProductInline(admin.TabularInline):
    model = BoxProduct
    # Displays one empty row for adding new BoxProducts inline.
    extra = 1  


# Registers the Box model with custom admin configuration.
@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    # Fields displayed in the Box list view within the admin.
    list_display = ('name', 'shipping_date', 'is_archived')
    
    # Automatically generate the slug based on the box name.
    prepopulated_fields = {"slug": ("name",)}
    
    # Enables inline editing of associated BoxProducts directly from a Box.
    inlines = [BoxProductInline]


# Registers the BoxProduct model for direct access via the admin interface.
# This complements the inline editing approach and allows for broader-level product management.
@admin.register(BoxProduct)
class BoxProductAdmin(admin.ModelAdmin):
    # Fields displayed in the BoxProduct list view within the admin.
    list_display = ('name', 'box', 'quantity')
