import json
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from main_app.models import EventParticipant, CourseParticipant
from profile_app.serializers import EventParticipantSerializer, CourseParticipantSerializer
from auth_app.serializers import PersonSerializer
from rest_framework.permissions import IsAuthenticated

class RegisteredEventsListAPIView(generics.ListAPIView):
    serializer_class = EventParticipantSerializer
    queryset = EventParticipant.objects.select_related('person', 'event').all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        person = self.request.user.person
        if person:
            queryset = qs.filter(person=person).order_by('-joined_at')
            return queryset
        raise ValidationError('You are not registered')

class RegisteredCoursesListAPIView(generics.ListAPIView):
    serializer_class = CourseParticipantSerializer
    queryset = CourseParticipant.objects.select_related('person', 'course').all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        person = self.request.user.person
        if person:
            queryset = qs.filter(person=person).order_by('-joined_at')
            return queryset
        raise ValidationError('You are not registered')

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
