from rest_framework import generics
from main_app.serializers import EventSerializer
from rest_framework.permissions import IsAuthenticated

class RegisteredEventsListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        queryset = user.person.registered_events.all()
        return queryset

