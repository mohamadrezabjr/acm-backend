from rest_framework import serializers
from main_app.serializers import EventListSerializer, CourseListSerializer

class AnalyticsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_events= serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_registrations = serializers.IntegerField()

    recent_events= EventListSerializer(many = True)
    recent_courses = CourseListSerializer(many = True)
