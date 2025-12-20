import json
from functools import partial

from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from main_app.serializers import CourseListSerializer, CourseCreateSerializer
from main_app.models import Course
from main_app.permissions import IsCreator, IsAdmin, IsSuperUser
from registration_app.services import RegistrationResultType


class CourseListAPIView(ListAPIView):
    serializer_class = CourseListSerializer
    queryset = Course.objects.all().prefetch_related('tags', 'instructors', 'time_plans')

class CourseRetrieveAPIView(RetrieveAPIView):
    serializer_class = CourseListSerializer
    queryset = Course.objects.all().prefetch_related('tags', 'instructors', 'time_plans')
    lookup_field = 'slug'

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

class CourseRegistration(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        user = request.user

        event = get_object_or_404(Course, slug=slug)
        registration_class = event.get_registration_class()
        result = registration_class.register(user.person)

        if result.result_type == RegistrationResultType.PAYMENT_REQUIRED:
            return Response(
                {"payment_url": result.payment_url},
                status=202
            )
        return Response({"detail" : result.response.get('detail')}, status = result.response.get('status'))

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
            data =data,
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

