from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from auth_app.models import Person
from auth_app.serializers import PersonSerializer
from main_app.models import Tag
from main_app.permissions import IsAdmin, IsCreator
from main_app.serializers.general_serializers import TagSerializer


class TagListAPIView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class PersonListAPIView(ListAPIView):
    queryset = Person.objects.all().select_related('user')
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsCreator]
