from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField

class Box(models.Model):
    """
    Represents a monthly subscription box created by an admin.

    Each Box contains a curated selection of products and is assigned a shipping
    date. Boxes can be archived once no longer available for active shipping.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='box_images/', null=True, blank=True)
    shipping_date = models.DateField()
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Auto-generate the slug from the box name if not manually set."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.shipping_date.strftime('%b %Y')}"


class BoxProduct(models.Model):
    """
    Represents a single product included in a specific Box.

    Products can include miniatures, paints, brushes, or other hobby items.
    This model supports display of past box contents as well as upcoming releases.
    """
    box = models.ForeignKey(
        Box,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        help_text="The box this product belongs to. Can be left blank if unassigned."
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of the included product."
    )
    image = CloudinaryField(
        'image',
        help_text="Upload an image to represent this product.",
        null=True,
        blank=True
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description for this product (shown in UI carousel)."
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Quantity of this product included in the box."
    )

    def __str__(self):
        return f"{self.name} (x{self.quantity})"
