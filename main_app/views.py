from rest_framework.generics import CreateAPIView, ListAPIView
from .serializers import EventSerializer
from main_app.models import Event
from main_app.permissions import IsCreator, IsAdmin, IsSuperUser
from rest_framework.permissions import IsAuthenticated

class EventListAPIView(ListAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')

class EventCreateAPIView(CreateAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')
    permission_classes = [IsAuthenticated, IsCreator | IsSuperUser | IsAdmin]
