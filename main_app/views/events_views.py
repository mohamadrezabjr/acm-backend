from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from main_app.serializers.events_serializers import EventListSerializer
from main_app.models import Event
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from registration_app.services import RegistrationResultType

class EventListAPIView(ListAPIView):
    serializer_class = EventListSerializer
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.is_admin or self.request.user.is_superuser:
                return qs
        return qs.filter(is_active= True)
class EventRetrieveAPIView(RetrieveAPIView):
    serializer_class = EventListSerializer
    queryset = Event.objects.all().prefetch_related('tags', 'speakers')
    lookup_field = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.is_admin or self.request.user.is_superuser:
                return qs
        return qs.filter(is_active= True)

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