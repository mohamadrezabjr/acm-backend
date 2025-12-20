from rest_framework import generics
from main_app.serializers import EventListSerializer
from rest_framework.permissions import IsAuthenticated

class RegisteredEventsListAPIView(generics.ListAPIView):
    serializer_class = EventListSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        queryset = user.person.registered_events.prefetch_related('tags', 'speakers').all()
        return queryset

