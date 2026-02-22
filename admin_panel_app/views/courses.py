import json
from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView,
    ListAPIView,
    RetrieveAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from admin_panel_app.serializers import (
    CourseCreateSerializer,
    AdminCourseListSerializer,
    AdminCourseParticipantSerializer,
)
from main_app.models import Course, CourseParticipant
from rest_framework.response import Response
from main_app.permissions import IsAdmin, IsCreator, IsSuperUser
from django.db import transaction

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

class AdminCourseRetrieveAPIView(RetrieveAPIView):
    serializer_class = AdminCourseListSerializer
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]
    queryset = Course.objects.all().prefetch_related('tags', 'instructors', 'time_plans')
    lookup_field = 'slug'

class AdminCourseListAPIView(ListAPIView):
    serializer_class = AdminCourseListSerializer
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]
    queryset = Course.objects.all().prefetch_related('tags', 'instructors', 'time_plans')

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

class DeactivateCourseAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @transaction.atomic
    def post(self, request, slug):
        course = get_object_or_404(Course.objects.select_for_update(), slug=slug)

        course.is_active = not course.is_active
        course.save(update_fields=['is_active'])

        return Response({"detail": 'course status changed'}, status=201)

class AdminCourseParticipantListAPIView(ListAPIView):
    serializer_class = AdminCourseParticipantSerializer
    queryset = CourseParticipant.objects.all().prefetch_related('person', 'course')
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]

