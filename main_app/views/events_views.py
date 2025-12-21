import json

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from main_app.serializers import EventCreateSerializer, EventListSerializer
from main_app.models import Event
from main_app.permissions import IsCreator, IsAdmin, IsSuperUser
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from registration_app.services import RegistrationResultType

class EventListAPIView(ListAPIView):
    serializer_class = EventListSerializer
    queryset = Event.objects.filter(is_active = True).prefetch_related('tags', 'speakers')

class EventRetrieveAPIView(RetrieveAPIView):
    serializer_class = EventListSerializer
    queryset = Event.objects.filter(is_active = True).prefetch_related('tags', 'speakers')
    lookup_field = 'slug'
    
class EventCreateAPIView(CreateAPIView):
    serializer_class = EventCreateSerializer
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')
    permission_classes = [IsAuthenticated, IsCreator | IsSuperUser | IsAdmin]
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):

        payload_raw = request.data.get('data')
        if not payload_raw:
            return Response(
                {"error": "data field is required"},
                status=400
            )

        payload = json.loads(payload_raw)

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        image = request.FILES.get('image')
        if image:
            event.image = image
            event.save(update_fields=['image'])

        return Response(serializer.data, status=201)
class EventRegistration(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        user = request.user

        event = get_object_or_404(Event, slug=slug)
        registration_class = event.get_registration_class()
        result = registration_class.register(user.person)

        if result.result_type == RegistrationResultType.PAYMENT_REQUIRED:
            return Response(
                {"payment_url": result.payment_url},
                status=202
            )
        return Response({"detail" : result.response.get('detail')}, status = result.response.get('status'))

class EventUpdateAPIView(UpdateAPIView):
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')
    serializer_class = EventCreateSerializer
    permission_classes = [IsAuthenticated,IsCreator|IsAdmin]
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        event = self.get_object()

        payload_raw = request.data.get('data')
        if not payload_raw:
            return Response(
                {"error": "data field is required"},
                status=400
            )

        payload = json.loads(payload_raw)
        serializer = self.get_serializer(
            event,
            data = payload,
            partial = True
        )
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        event.registered = event.participants.count()
        event.save(update_fields=['registered'])

        image = request.FILES.get('image')
        if image:
            event.image = image
            event.save(update_fields=['image'])

        return Response(serializer.data, status=200)