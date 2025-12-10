from rest_framework import serializers
from main_app.models import Event, Tag
from auth_app.serializers import PersonSerializer

class EventSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    speakers = PersonSerializer(many=True)

    def get_tags(self, obj):
        return obj.tags.values_list('name', flat=True)

    class Meta:
        model = Event
        fields = [
            'title',
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