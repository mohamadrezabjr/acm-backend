from django.db import models, IntegrityError
from django.utils import timezone
import uuid
from rest_framework.exceptions import ValidationError
from auth_app.models import Person
from registration_app.services import FreeRegistration
from django.db import transaction
from main_app.models.utils import check_dependencies
from main_app.models.tag import Tag

class EventParticipant(models.Model):
    class StatusChoices(models.TextChoices):
        ACCEPTED = ('accepted', 'تایید  شده')
        PENDING = ('pending', 'در حال پردازش')
        CANCELLED = ('cancelled', 'لغو شده')

    event = models.ForeignKey('main_app.Event', on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='event_participants')
    first_name_at_registration = models.CharField(max_length=256, null=True, blank=True)
    last_name_at_registration = models.CharField(max_length=256, null=True, blank=True)
    email_at_registration = models.CharField(max_length=256, null=True, blank=True)
    phone_at_registration = models.CharField(max_length=256, null=True, blank=True)
    student_id_at_registration = models.CharField(max_length=256, null=True, blank=True)
    status = models.CharField(choices=StatusChoices, default=StatusChoices.ACCEPTED, max_length=20)
    joined_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk and not self.first_name_at_registration :
            user = self.person.user
            self.first_name_at_registration = self.person.first_name or None
            self.last_name_at_registration = self.person.last_name or None
            self.email_at_registration = user.email if user else None
            self.phone_at_registration = user.phone if user else None
            self.student_id_at_registration = self.person.student_id or None

        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "person"],
                name="unique_event_person"
            )
        ]
    def __str__(self):
        return f'{self.event} --- {self.person}'

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
    is_active = models.BooleanField(default=True)
    dependencies = models.JSONField(default=list, blank=True, null=True)
    is_full = models.BooleanField(default=False)

    def clean(self):
        person_fields = {f.name for f in Person._meta.get_fields()}
        person_fields.add("phone")
        invalid = set(self.dependencies) - person_fields
        if invalid:
            raise ValidationError({
                "dependencies": f"Invalid User fields: {', '.join(invalid)}"
            })

    def add_person(self, person:Person):
        try:
            with transaction.atomic():
                event = self.__class__.objects.select_for_update().get(id = self.id)

                if not event.is_active:
                    return {'detail' : 'Event not found', 'status' : 404}

                if event.registration_deadline < timezone.now():
                    return {"detail" : "Registration time is over", "status":403}
                registered = event.participants.count()
                if registered >= event.capacity:
                    event.registered = registered
                    event.save(update_fields=['registered'])
                    return {"detail" : "Capacity is full", "status":409}
                if not check_dependencies(person, self.dependencies):
                    return {'detail' : 'Dependencies not satisfied', 'status':400}

                EventParticipant.objects.create(
                    event=event,
                    person = person
                )
                event.registered = registered + 1
                event.save(update_fields=['registered'])

            return {"detail" : "Event successfully added to your account", "status" : 201}
        except IntegrityError:
            return {'detail': 'You already registered to this event', "status": 422}

    def get_registration_class(self):
        if self.price == 0:
            return FreeRegistration(self)
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.title}-{uuid.uuid4().hex}"
        if self.registered >= self.capacity:
            self.is_full = True
        super().save(*args, **kwargs)
