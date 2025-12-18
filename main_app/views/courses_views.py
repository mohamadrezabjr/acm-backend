import json

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from main_app.serializers import CourseListSerializer, CourseCreateSerializer
from main_app.models import Course
from main_app.permissions import IsCreator, IsAdmin, IsSuperUser


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

        return Response({"message": "Course successfully created"}, status=201)
