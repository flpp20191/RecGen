from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from audit.models import *


@receiver(post_save, sender=Category)
def add_category_to_all_users(sender, instance, created, **kwargs):
    if created:
        for user in User.objects.all():
            UserCategory.objects.create(user=user, category=instance, is_tracking=True)
