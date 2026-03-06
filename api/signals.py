import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import SkincareProduct, SkinProgress

@receiver(post_delete, sender=SkincareProduct)
def delete_product_image_on_delete(sender, instance, **kwargs):
    """
    Deletes image file from filesystem when corresponding SkincareProduct object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(post_delete, sender=SkinProgress)
def delete_progress_image_on_delete(sender, instance, **kwargs):
    """
    Deletes image file from filesystem when corresponding SkinProgress object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
