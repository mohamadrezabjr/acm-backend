from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from auth_app.models import Person, User
from auth_app.serializers import PersonSerializer
from main_app.models import Tag, Event, Course, EventParticipant, CourseParticipant
from main_app.permissions import IsAdmin, IsCreator
from main_app.serializers import TagSerializer, EventListSerializer, CourseListSerializer, AnalyticsSerializer


class TagListAPIView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class PersonListAPIView(ListAPIView):
    queryset = Person.objects.all().select_related('user')
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsCreator]

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


