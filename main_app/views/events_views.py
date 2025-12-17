import json

from django.utils import timezone
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from main_app.serializers import EventCreateSerializer, EventListSerializer
from main_app.models import Event
from main_app.permissions import IsCreator, IsAdmin, IsSuperUser
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

class EventListAPIView(ListAPIView):
    serializer_class = EventListSerializer
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')

class EventRetrieveAPIView(RetrieveAPIView):
    serializer_class = EventListSerializer
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')
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

        if event.price != 0 :
            return Response({"detail" : "payment was not successful"}, status=402) #No payment for now
        if event.registration_deadline < timezone.now():
            return Response({"detail" : "Registration time is over"}, status=403)
        if event.registered >= event.capacity:
            return Response({"detail" : "Capacity is full"}, status=409)
        if event in user.person.registered_events.all():
            return Response({'detail' : 'You already registered to this event'}, status = 422)
        with transaction.atomic():
            user.person.registered_events.add(event)
            event.registered += 1
            event.save()

        return Response({"message" : "Event successfully added to your account"}, status=201)