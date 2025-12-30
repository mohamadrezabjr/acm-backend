import json
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from admin_panel_app.serializers import (
    AnalyticsSerializer,
    EventCreateSerializer,
    CourseCreateSerializer,
    AdminCourseListSerializer,
    AdminEventListSerializer,
    AdminEventParticipantSerializer,
    AdminCourseParticipantSerializer,
)
from main_app.models import Event, Course,EventParticipant, CourseParticipant
from auth_app.models import User
from rest_framework.response import Response
from main_app.permissions import IsAdmin, IsCreator, IsSuperUser
from django.db import transaction

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

    @transaction.atomic
    def post(self, request, slug):
        event = get_object_or_404(Event.objects.select_for_update(), slug=slug)

        event.is_active = not event.is_active
        event.save(update_fields=['is_active'])

        return Response({"detail" : 'event status changed'}, status = 201)

class DeactivateCourse(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @transaction.atomic
    def post(self, request, slug):
        course = get_object_or_404(Course.objects.select_for_update(), slug=slug)

        course.is_active = not course.is_active
        course.save(update_fields=['is_active'])

        return Response({"detail": 'course status changed'}, status=201)

class EventCreateAPIView(CreateAPIView):
    serializer_class = EventCreateSerializer
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')
    permission_classes = [IsAuthenticated, IsCreator | IsSuperUser | IsAdmin]
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):

        payload_raw = request.data.get('data')
        if not payload_raw:
            return Response(
                {"error": "data field is required"},
                status=400
            )

        payload = json.loads(payload_raw)

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        image = request.FILES.get('image')
        if image:
            event.image = image
            event.save(update_fields=['image'])

        return Response(serializer.data, status=201)

class EventUpdateAPIView(UpdateAPIView):
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')
    serializer_class = EventCreateSerializer
    permission_classes = [IsAuthenticated,IsCreator|IsAdmin]
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        event = self.get_object()

        payload_raw = request.data.get('data')
        if not payload_raw:
            return Response(
                {"error": "data field is required"},
                status=400
            )

        payload = json.loads(payload_raw)
        serializer = self.get_serializer(
            event,
            data = payload,
            partial = True
        )
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        event.registered = event.participants.count()
        event.save(update_fields=['registered'])

        image = request.FILES.get('image')
        if image:
            event.image = image
            event.save(update_fields=['image'])

        return Response(serializer.data, status=200)

class CourseCreateAPIView(CreateAPIView):
    serializer_class = CourseCreateSerializer
    queryset = Course.objects.all().prefetch_related('tags', 'instructors', 'time_plans')
    permission_classes = [IsAuthenticated, IsCreator | IsSuperUser | IsAdmin]

    def create(self, request, *args, **kwargs):

        raw_payload = request.data.get('data')

        if not raw_payload:
            return Response(
                {'error' : 'data field is required'},
                status=400
            )

        data = json.loads(raw_payload)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        image = request.FILES.get('image')

        if image:
            course.image = image
            course.save(update_fields=['image'])

        return Response({"message": "Course successfully created"}, status=201)

class CourseUpdateAPIView(UpdateAPIView):
    queryset = Course.objects.all().prefetch_related('tags', 'instructors', 'time_plans')
    serializer_class = CourseCreateSerializer
    permission_classes = [IsAuthenticated, IsAdmin|IsCreator]
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        raw_payload = request.data.get('data')

        if not raw_payload:
            return Response(
                {'error' : 'data field is required'},
                status=400
            )
        data = json.loads(raw_payload)

        serializer = self.get_serializer(
            instance = instance,
            data = data,
            partial = True
        )
        serializer.is_valid(raise_exception = True)
        course = serializer.save()
        course.registered = course.participants.count()
        course.save(update_fields=['registered'])

        image = request.FILES.get('image')

        if image:
            course.image = image
            course.save(update_fields=['image'])

        return Response(serializer.data, status=200)

class AdminEventListAPIView(ListAPIView):
    serializer_class = AdminEventListSerializer
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.is_admin or self.request.user.is_superuser:
                return qs
        return qs.filter(is_active= True)

class AdminCourseListAPIView(ListAPIView):
    serializer_class = AdminCourseListSerializer
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]
    queryset = Course.objects.all().prefetch_related('tags', 'instructors', 'time_plans')

class AdminEventRetrieveAPIView(RetrieveAPIView):
    serializer_class = AdminEventListSerializer
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')
    lookup_field = 'slug'

class AdminCourseRetrieveAPIView(RetrieveAPIView):
    serializer_class = AdminCourseListSerializer
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]
    queryset = Course.objects.all().prefetch_related('tags', 'instructors', 'time_plans')
    lookup_field = 'slug'

class AdminEventParticipantListAPIView(ListAPIView):
    serializer_class = AdminEventParticipantSerializer
    queryset = EventParticipant.objects.all().prefetch_related('person', 'event')
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]

class AdminCourseParticipantListAPIView(ListAPIView):
    serializer_class = AdminCourseParticipantSerializer
    queryset = CourseParticipant.objects.all().prefetch_related('person', 'event')
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]

