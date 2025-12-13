from django.db import models
from django.utils import timezone

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True, db_index=True)

    def __str__(self):
        return self.name
class TimePlan(models.Model):
    class WeekDays(models.TextChoices):
        SATURDAY = '0', 'Saturday'
        SUNDAY = '1', 'Sunday'
        MONDAY = '2', 'Monday'
        TUESDAY = '3', 'Tuesday'
        WEDNESDAY = '4', 'Wednesday'
        THURSDAY = '5', 'Thursday'
        FRIDAY = '6', 'Friday'

    weekday = models.CharField(max_length = 11, choices=WeekDays.choices, db_index=True)
    time = models.TimeField()

class Course(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null = True)
    slug = models.CharField(
        max_length=256,
        unique=True,
        db_index=True,
        null=True,
        blank=True
    )
    tags = models.ManyToManyField(Tag, related_name='courses')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null = True, blank=True)
    registration_start_at = models.DateTimeField(default=timezone.now)
    registration_deadline = models.DateTimeField()
    capacity = models.IntegerField()
    registered = models.IntegerField(default=0)
    location = models.CharField(max_length=256, blank=True, null=True)
    price = models.BigIntegerField(default=0)
    organizer = models.CharField(max_length=64, null=True, blank=True)
    image = models.ImageField(upload_to='courses/',null=True, blank=True)
    instructors = models.ManyToManyField(
        'auth_app.Person',
        related_name='courses_as_instructor',
        blank = True,
    )
    time_plans = models.ManyToManyField(TimePlan, related_name='courses', blank=True)

class Event(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null = True)
    slug = models.CharField(
        max_length=256,
        unique=True,
        db_index=True,
        null=True,
        blank=True
    )
    tags = models.ManyToManyField(Tag, related_name='events')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_start_at = models.DateTimeField(default=timezone.now)
    registration_deadline = models.DateTimeField()
    capacity = models.IntegerField()
    registered = models.IntegerField(default=0)
    location = models.CharField(max_length=256, blank=True, null=True)
    price = models.BigIntegerField(default=0)
    organizer = models.CharField(max_length=64, null=True, blank=True)
    image = models.ImageField(upload_to='events/',null=True, blank=True)
    speakers = models.ManyToManyField(
        'auth_app.Person',
        related_name='events_as_speaker',
        blank = True,
    )
