import json
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from main_app.serializers.events_serializers import EventListSerializer
from auth_app.serializers import PersonSerializer
from rest_framework.permissions import IsAuthenticated

class RegisteredEventsListAPIView(generics.ListAPIView):
    serializer_class = EventListSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        queryset = user.person.registered_events.prefetch_related('tags', 'speakers').all()
        return queryset

class ProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def put(self, request):
        current_person = request.user.person

        raw_payload = request.data.get('data')
        if not raw_payload:
            return Response(
                {'error': 'data field is required'},
                status=400
            )

        data = json.loads(raw_payload)
        serializer = PersonSerializer(instance = current_person,data = data)
        serializer.is_valid(raise_exception = True)
        person = serializer.save()

        avatar = request.FILES.get('avatar')
        if avatar:
            person.avatar = avatar
            person.save(update_fields=['avatar'])

        return Response(serializer.data, status = 200)
