from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Person(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    position = models.CharField(max_length=64, null=True, blank = True)
    description = models.TextField(null = True, blank=True)
    registered_events = models.ManyToManyField(
        'main_app.Event',
            related_name='participants',
            blank = True
    )
    registered_courses = models.ManyToManyField(
        'main_app.Course',
        related_name='participants',
        blank = True
    )
