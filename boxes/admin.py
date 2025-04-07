from django.contrib import admin
from .models import Box, BoxProduct

class BoxProductInline(admin.TabularInline):
    model = BoxProduct
    extra = 1 # Shows an extra, empty row for the Django Admin panel

@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'shipping_date', 'is_archived')
    prepopulated_fields = {"slug": ("name",)}
    inlines = [BoxProductInline]

# Will see if I need this - since I may just built to edit contents with the boxes
@admin.register(BoxProduct)
class BoxProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'box', 'quantity')