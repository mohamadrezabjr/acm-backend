from rest_framework import serializers
from auth_app.serializers import PersonSerializer
from main_app.models import EventParticipant, CourseParticipant
from main_app.serializers.courses_serializers import CourseListSerializer
from main_app.serializers.events_serializers import EventListSerializer

class EventParticipantSerializer(serializers.ModelSerializer):
    event = EventListSerializer(read_only=True)
    class Meta:
        model = EventParticipant
        fields = [
            'event',
            'joined_at',
            'status',
        ]

class CourseParticipantSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = CourseParticipant
        fields = [
            'course',
            'joined_at',
            'status',
        ]
