from rest_framework import serializers
from auth_app.serializers import PersonGetOrCreateSerializer
from main_app.models import Tag, Course, TimePlan
from main_app.serializers.general_serializers import TagSerializer
from django.db import transaction

class TimePlanSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, allow_null=True)
    class Meta:
        model = TimePlan
        fields = [
            'pk',
            'weekday',
            'time_start',
            'time_end',
        ]

class CourseListSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field= 'name'
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
            'capacity',
            'registered',
            'location',
            'price',
            'organizer',
            'image',
            'instructors',
            'time_plans',
            'is_active',
            'dependencies',
        ]

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
            'dependencies'
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