from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from admin_panel_app.serializers import AnalyticsSerializer
from main_app.models import Event, Course,EventParticipant, CourseParticipant
from main_app.serializers import EventListSerializer, CourseListSerializer
from auth_app.models import User
from rest_framework.response import Response
from main_app.permissions import IsAdmin, IsCreator

class AdminDashboardStatus(APIView):
    permission_classes = [IsAuthenticated, IsAdmin | IsCreator]

    def get(self, request, *args, **kwargs):
        events = Event.objects.order_by('-start_date')[:5]


        courses = Course.objects.order_by('-start_date')[:5]


        analytics = {
            "total_events" : Event.objects.count(),
            "total_courses" : Course.objects.count(),
            "total_registrations" : (EventParticipant.objects.count() + CourseParticipant.objects.count()),
            "total_users" : User.objects.count(),
            "recent_events" : events,
            'recent_courses' : courses,
        }

        serializer = AnalyticsSerializer(analytics)
        return Response(serializer.data, status = 200)

class DeactivateEvent(APIView):
    permission_classes =  [IsAuthenticated, IsAdmin]

    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug)

        event.is_active = not event.is_active
        event.save(update_fields=['is_active'])

        return Response({"detail" : 'event status changed'}, status = 201)