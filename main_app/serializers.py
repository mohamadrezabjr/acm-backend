from django.core.checks.security.base import check_sts
from rest_framework import serializers
from sqlparse import split

from auth_app.models import Person
from main_app.models import Event, Tag
from auth_app.serializers import PersonSerializer, PersonGetOrCreateSerializer


class EventSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field= 'name'
    )
    speakers = PersonGetOrCreateSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = [
            'title',
            'slug',
            'description',
            'tags',
            'start_date',
            'end_date',
            'registration_start_at',
            'registration_deadline',
            'capacity',
            'registered',
            'location',
            'price',
            'organizer',
            'image',
            'speakers'
        ]
    def create(self, validated_data):
        speakers = validated_data.pop('speakers')
        tags = validated_data.pop("tags")
        event = Event.objects.create(**validated_data)
        event.tags.set(tags)
        for speaker in speakers:
            user = speaker.get('user')
            if not user:
                person = Person.objects.create(position = speaker.get('position'), description = speaker.get('description'))
            else :
                person = Person.objects.filter(user = user).first()
            event.speakers.add(person)
        return event