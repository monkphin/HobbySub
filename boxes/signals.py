from django.db.models.signals import post_delete
from django.dispatch import receiver
from cloudinary.uploader import destroy
from .models import Box, BoxProduct


@receiver(post_delete, sender=BoxProduct)
def delete_product_image(sender, instance, **kwargs):
    if instance.image:
        destroy(instance.image.public_id)


@receiver(post_delete, sender=Box)
def delete_box_image(sender, instance, **kwargs):
    if instance.image:
        destroy(instance.image.public_id)
