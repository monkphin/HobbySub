from django.db import models
from django.utils.text import slugify

class Box(models.Model):
    """
    Represents the monthly box available to subscribers. Boxes are created by
    admins and can be marked as archived once they're no longer active to be 
    shipped
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image_url = models.URLField()
    shipping_date = models.DateField()
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Auto-generate slug if not set."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

        def __str__(self):
            return self.name
        

class BoxProduct(models.Model):
    """
    Represents a single item included a box (eg: paintbrush, mini, paint etc).
    Used to populate box displays for current or historic boxes
    """
    box = models.ForeignKey(Box,
                            on_delete=models.SET_NULL,
                            null=True,
                            blank=True,
                            related_name='products',
                            help_text="The box this product is part of."
                            )
    name = models.CharField(max_length=100,
                            help_text="Name of the included product."
                            )
    image_url = models.URLField(help_text="Image of the product.")
    description = models.TextField(blank=True,
                                   help_text="Optional description shown in carousel."
                                   )
    quantity = models.PositiveIntegerField(default=1,
                                           help_text="Quantity of this product in the box."
                                           )
    
    def __str__ (self):
        return f"{self.name} (x{self.quantity})"
