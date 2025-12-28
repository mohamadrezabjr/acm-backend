from rest_framework import serializers
from auth_app.serializers import PersonGetOrCreateSerializer
from main_app.models import Tag, Course, TimePlan

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
            'image',
            'instructors',
            'time_plans',
            'is_active',
            'dependencies',
            'is_full'
        ]