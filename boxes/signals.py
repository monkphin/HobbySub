"""
Signal handlers for cleaning up Cloudinary images when Box or BoxProduct
instances are deleted.
"""
import logging

from cloudinary.uploader import destroy
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Box, BoxProduct

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=BoxProduct)
def delete_product_image(sender, instance, **kwargs):
    """
    Delete the Cloudinary image associated with a BoxProduct after it is
    deleted.
    """
    if (
        instance.image
        and hasattr(instance.image, 'public_id')
        and instance.image.public_id
    ):
        destroy(instance.image.public_id)
        logger.info(
            f"Deleted Cloudinary image for {instance} "
            "(public_id={instance.image.public_id})"
        )


@receiver(post_delete, sender=Box)
def delete_box_image(sender, instance, **kwargs):
    """
    Delete the Cloudinary image associated with a Box after it is deleted.
    """
    if (
        instance.image
        and hasattr(instance.image, 'public_id')
        and instance.image.public_id
    ):
        destroy(instance.image.public_id)
        logger.info(
            f"Deleted Cloudinary image for {instance} "
            "(public_id={instance.image.public_id})"
        )
