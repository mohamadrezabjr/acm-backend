from django.db import transaction
from rest_framework import serializers
from auth_app.models import Person
from auth_app.serializers import PersonGetOrCreateSerializer
from main_app.models import Tag, Event, Course, TimePlan, EventParticipant, CourseParticipant
from main_app.serializers.courses_serializers import TimePlanSerializer
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

class AdminCourseListSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many = True,
        queryset = Tag.objects.all(),
        slug_field = 'name'
    )
    instructors = PersonGetOrCreateSerializer(many=True, required=False)
    time_plans = TimePlanSerializer(many=True, required=False)

    image = serializers.SerializerMethodField(required = False)

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
    class Meta:
        model = Course
        fields = [
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
            'capacity',
            'registered',
            'image',
            'instructors',
            'time_plans',
            'is_active',
            'dependencies',
            'is_full',
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

class CourseCreateSerializer(serializers.ModelSerializer):
    tags = serializers.ListSerializer(child=TagSerializer(), required=False)

    instructors = PersonGetOrCreateSerializer(many=True, required=False)
    time_plans = TimePlanSerializer(many=True, required=False)

    image = serializers.SerializerMethodField(required = False)

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
    class Meta:
        model = Course
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
            'instructors',
            'time_plans',
            'dependencies',
            'is_full'
        ]
    def create(self, validated_data):
        time_plans = validated_data.pop('time_plans')
        tags = validated_data.pop('tags')
        instructors = validated_data.pop('instructors')

        with transaction.atomic():
            course = Course.objects.create(**validated_data)
            if time_plans:
                time_plans_serializer = TimePlanSerializer(data = time_plans, many=True)
                time_plans_serializer.is_valid(raise_exception=True)
                time_plans = time_plans_serializer.save()

                course.time_plans.set(time_plans)

            if tags:
                serializer_tags = TagSerializer(data = tags, many=True)
                serializer_tags.is_valid(raise_exception=True)
                tags = serializer_tags.save()

                course.tags.set(tags)

            if instructors:
                instructors_serializer = PersonGetOrCreateSerializer(data=instructors, many=True)
                instructors_serializer.is_valid(raise_exception = True)
                instructors = instructors_serializer.save()

                course.instructors.set(instructors)

        return course
    def update(self, instance, validated_data):
        time_plans = validated_data.pop('time_plans')
        tags = validated_data.pop('tags')
        instructors = validated_data.pop('instructors')

        with transaction.atomic():
            course = Course.objects.select_for_update().get(id=instance.id)
            course = super().update(course, validated_data)

            if time_plans:
                TimePlan.objects.filter(course=course).delete()

                time_plans_serializer = TimePlanSerializer(data = time_plans, many=True)
                time_plans_serializer.is_valid(raise_exception=True)
                time_plans = time_plans_serializer.save()

                course.time_plans.set(time_plans)

            if tags:
                serializer_tags = TagSerializer(data = tags, many=True)
                serializer_tags.is_valid(raise_exception=True)
                tags = serializer_tags.save()

                course.tags.set(tags)

            if instructors:
                instructors_serializer = PersonGetOrCreateSerializer(data=instructors, many=True)
                instructors_serializer.is_valid(raise_exception = True)
                instructors = instructors_serializer.save()

                course.instructors.set(instructors)

        return course

class AnalyticsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_events= serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_registrations = serializers.IntegerField()

    recent_events= AdminEventListSerializer(many = True)
    recent_courses = AdminCourseListSerializer(many = True)
