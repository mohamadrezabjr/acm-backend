from rest_framework import serializers
from auth_app.serializers import PersonGetOrCreateSerializer
from main_app.models import Event, Tag
from auth_app.models import Person

class EventListSerializer(serializers.ModelSerializer):
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
            'image',
            'speakers',
            'is_active',
            'dependencies',
            'is_full'
        ]