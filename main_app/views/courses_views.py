from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from main_app.serializers import CourseSerializer
from main_app.models import Course
from main_app.permissions import IsCreator, IsAdmin, IsSuperUser
from rest_framework.permissions import IsAuthenticated

class CourseListAPIView(ListAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.all().prefetch_related('tags', 'instructors', 'time_plans')

class CourseRetrieveAPIView(RetrieveAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.all().prefetch_related('tags', 'instructors', 'time_plans')
    lookup_field = 'slug'

class CourseCreateAPIView(CreateAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.all().prefetch_related('tags', 'instructors', 'time_plans')
    permission_classes = [IsAuthenticated, IsCreator | IsSuperUser | IsAdmin]
