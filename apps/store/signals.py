from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Category, SearchCount, AdPhoto


@receiver(post_save, sender=Category)
def create_search_count(sender, instance, created, **kwargs):
    if created:
        SearchCount.objects.get_or_create(category=instance)


@receiver(post_save, sender=AdPhoto)
def manage_main_photo(sender, instance, created, **kwargs):
    if instance.is_main:
        AdPhoto.objects.filter(
            ad=instance.ad,
            is_main=True
        ).exclude(id=instance.id).update(is_main=False)
    else:
        if not AdPhoto.objects.filter(ad=instance.ad, is_main=True).exists():
            first_photo = AdPhoto.objects.filter(ad=instance.ad).first()
            if first_photo:
                first_photo.is_main = True
                first_photo.save()


@receiver(post_delete, sender=AdPhoto)
def manage_main_photo_on_delete(sender, instance, **kwargs):
    if instance.is_main:
        next_photo = AdPhoto.objects.filter(ad=instance.ad).first()
        if next_photo:
            next_photo.is_main = True
            next_photo.save()
