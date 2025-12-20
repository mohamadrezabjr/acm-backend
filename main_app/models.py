from django.db import models, IntegrityError
from django.utils import timezone
import uuid
from abc import abstractmethod
from auth_app.models import Person
from registration_app.services import FreeRegistration
from django.db import transaction

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True, db_index=True)

    def __str__(self):
        return self.name
class TimePlan(models.Model):
    class WeekDays(models.TextChoices):
        SATURDAY = 'Sat', "Saturday"
        SUNDAY = 'Sun', "Sunday"
        MONDAY = 'Mon', "Monday"
        TUESDAY = 'Tue', "Tuesday"
        WEDNESDAY = 'Wed', "Wednesday"
        THURSDAY = 'Thu', "Thursday"
        FRIDAY = 'Fr', "Friday"
    weekday = models.CharField(max_length=10, choices=WeekDays.choices)
    time_start = models.TimeField()
    time_end = models.TimeField(null=True, blank=True)
    course = models.ForeignKey("main_app.Course", on_delete=models.CASCADE, related_name="time_plans", null = True, blank=True)

class Activity(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null = True)
    slug = models.CharField(
        max_length=256,
        unique=True,
        db_index=True,
        null=True,
        blank=True
    )
    participants = models.ManyToManyField(Person, related_name="registered_%(class)s", blank=True)

    class Meta:
        abstract = True

    @abstractmethod
    def add_person(self, person:Person):
        raise NotImplementedError
    @abstractmethod
    def get_registration_class(self):
        raise NotImplementedError

class EventParticipant(models.Model):
    event = models.ForeignKey('main_app.Event', on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "person"],
                name="unique_event_person"
            )
        ]

class CourseParticipant(models.Model):
    course = models.ForeignKey('main_app.Course', on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "person"],
                name="unique_course_person"
            )
        ]

class Course(Activity):
    tags = models.ManyToManyField(Tag, related_name='courses', blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
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
    participants = models.ManyToManyField(Person, blank=True, related_name='registered_courses', through='CourseParticipant')

    def add_person(self, person:Person):
        try:
            with transaction.atomic():
                course = self.__class__.objects.select_for_update().get(id = self.id)

                if course.registration_deadline < timezone.now():
                    return {"detail" : "Registration time is over", "status":410}
                registered = course.participants.count()
                if registered >= course.capacity:
                    course.registered = registered
                    course.save()
                    return {"detail" : "Capacity is full", "status":409}

                CourseParticipant.objects.create(
                    course=course,
                    person=person
                )
                course.registered = registered + 1
                course.save()
            return {"message" : "Course successfully added to your account", "status" : 201}
        except IntegrityError:
            return {'detail': 'You already registered to this course', "status": 422}

    def get_registration_class(self):
        if self.price == 0:
            return FreeRegistration(self)
        return None


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.title}-{uuid.uuid4().hex}"
        super().save(*args, **kwargs)

class Event(Activity):
    tags = models.ManyToManyField(Tag, related_name='events', blank=True)
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
    participants = models.ManyToManyField(Person, blank=True, related_name='registered_events', through='EventParticipant')


    def add_person(self, person:Person):
        try:
            with transaction.atomic():
                event = self.__class__.objects.select_for_update().get(id = self.id)

                if event.registration_deadline < timezone.now():
                    return {"detail" : "Registration time is over", "status":403}
                registered = event.participants.count()
                if registered >= event.capacity:
                    event.registered = registered
                    event.save()
                    return {"detail" : "Capacity is full", "status":409}

                EventParticipant.objects.create(
                    event=event,
                    person = person
                )
                event.registered = registered + 1
                event.save()

            return {"message" : "Event successfully added to your account", "status" : 201}
        except IntegrityError:
            return {'detail': 'You already registered to this event', "status": 422}

    def get_registration_class(self):
        if self.price == 0:
            return FreeRegistration(self)
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.title}-{uuid.uuid4().hex}"
        super().save(*args, **kwargs)