from django.db import transaction
from rest_framework import serializers
from auth_app.models import Person
from auth_app.serializers import PersonGetOrCreateSerializer, PersonSerializer
from main_app.models import Tag, Event,EventParticipant
from main_app.serializers.general_serializers import TagSerializer

class AdminEventListSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        required=False,
        slug_field='name',
        many=True,
        queryset=Tag.objects.all(),
    )
    speakers = PersonGetOrCreateSerializer(many=True, required=False)

    image = serializers.SerializerMethodField(required = False)
    dependencies = serializers.ListSerializer(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        allow_empty=True
    )

    def validate_dependencies(self, value):
        person_fields = {f for f in Person._meta.fields}
        invalid = set(value) - person_fields
        if invalid:
            raise serializers.ValidationError(
                f"Invalid user fields: {', '.join(invalid)}"
            )

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
    class Meta:
        model = Event
        fields =[
            'id',
            'title',
            'slug',
            'description',
            'tags',
            'start_date',
            'end_date',
            'registration_start_at',
            'registration_deadline',
            'location',
            'price',
            'organizer',
            'registered',
            'capacity',
            'image',
            'speakers',
            'is_active',
            'dependencies',
            'is_full'
        ]


class EventCreateSerializer(serializers.ModelSerializer):
    tags = serializers.ListSerializer(child=TagSerializer(), required=False)
    speakers = PersonGetOrCreateSerializer(many=True, required=False)
    image = serializers.SerializerMethodField(required = False)

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
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
            'speakers',
            'dependencies',
            'is_full',
        ]
    def create(self, validated_data):
        speakers = validated_data.pop('speakers', None)
        tags = validated_data.pop("tags", None)
        with transaction.atomic():
            event = Event.objects.create(**validated_data)
            if tags:
                serializer_tags = TagSerializer(data=tags, many=True)
                serializer_tags.is_valid(raise_exception=True)
                tags = serializer_tags.save()

                event.tags.set(tags)
            if speakers:
                speakers_serializer = PersonGetOrCreateSerializer(data=speakers, many=True)
                speakers_serializer.is_valid(raise_exception=True)
                speakers = speakers_serializer.save()

                event.speakers.set(speakers)
        return event
    def update(self, instance, validated_data):
        speakers = validated_data.pop('speakers', None)
        tags = validated_data.pop("tags", None)
        with transaction.atomic():
            event = Event.objects.select_for_update().get(id=instance.id)
            event = super().update(event, validated_data)
            if tags:
                serializer_tags = TagSerializer(data=tags, many=True)
                serializer_tags.is_valid(raise_exception=True)
                tags = serializer_tags.save()

                event.tags.set(tags)
            if speakers:
                speakers_serializer = PersonGetOrCreateSerializer(data=speakers, many=True)
                speakers_serializer.is_valid(raise_exception=True)
                speakers = speakers_serializer.save()

                event.speakers.set(speakers)
        return event

class AdminEventParticipantSerializer(serializers.ModelSerializer):
    event = AdminEventListSerializer()
    person = PersonSerializer()

    class Meta:
        model = EventParticipant
        fields = '__all__'
