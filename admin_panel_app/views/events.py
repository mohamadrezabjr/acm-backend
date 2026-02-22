import json
from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView,
    ListAPIView,
    RetrieveAPIView
)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from admin_panel_app.serializers.events import (
    EventCreateSerializer,
    AdminEventListSerializer,
    AdminEventParticipantSerializer,
)
from main_app.models import Event, EventParticipant
from rest_framework.response import Response
from main_app.permissions import IsAdmin, IsCreator, IsSuperUser
from django.db import transaction

class DeactivateEventAPIView(APIView):
    permission_classes =  [IsAuthenticated, IsAdmin]

    @transaction.atomic
    def post(self, request, slug):
        event = get_object_or_404(Event.objects.select_for_update(), slug=slug)

        event.is_active = not event.is_active
        event.save(update_fields=['is_active'])

        return Response({"detail" : 'event status changed'}, status = 201)

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

class AdminEventListAPIView(ListAPIView):
    serializer_class = AdminEventListSerializer
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.is_admin or self.request.user.is_superuser:
                return qs
        return qs.filter(is_active= True)

class AdminEventRetrieveAPIView(RetrieveAPIView):
    serializer_class = AdminEventListSerializer
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')
    lookup_field = 'slug'

class AdminEventParticipantListAPIView(ListAPIView):
    serializer_class = AdminEventParticipantSerializer
    queryset = EventParticipant.objects.all().prefetch_related('person', 'event')
    permission_classes = [IsAuthenticated, IsCreator|IsAdmin]