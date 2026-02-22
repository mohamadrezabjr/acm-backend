from rest_framework import serializers
from admin_panel_app.serializers.courses import AdminCourseListSerializer
from admin_panel_app.serializers.events import AdminEventListSerializer

class AnalyticsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_events= serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_registrations = serializers.IntegerField()

    recent_events= AdminEventListSerializer(many = True)
    recent_courses = AdminCourseListSerializer(many = True)
