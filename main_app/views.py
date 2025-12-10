from rest_framework.generics import CreateAPIView, ListAPIView
from .serializers import EventSerializer
from main_app.models import Event

class EventListAPIView(ListAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all().prefetch_related('tags', 'speakers').select_related('image')
