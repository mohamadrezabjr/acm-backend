from django.db.models.signals import post_save
from django.dispatch import receiver
from auth_app.models import User, Person

@receiver(post_save, sender=User)
def create_person(sender, instance, created, **kwargs):
    if created:
        person = Person.objects.create(user=instance)