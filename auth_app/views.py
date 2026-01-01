from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from auth_app.models import PendingRegistration
from auth_app.serializers import UserRegistrationSerializer, PendingRegistrationSerializer
from auth_app.serializers import AuthMeSerializer
from auth_app.utils import get_tokens_for_user

@api_view(['GET'])
def auth_me(request):
    if request.user.is_authenticated:
        user = request.user
        data = AuthMeSerializer(user).data
        return Response(data)

    return Response({'detail' : "Unauthorized"}, status=403)

class UserRegister(APIView):
    serializer_class = PendingRegistrationSerializer
    def post(self, request):

        serialized_data = self.serializer_class(data = request.data)

        if serialized_data.is_valid():
            pending = serialized_data.save()
            # Send email
            return Response({"detail" : "registration is pending for verification", "registration_id" : str(pending.id)}, status=201)
        return Response(serialized_data.errors, status=400)

class RevalidateRegistrationOTP(APIView):
    @transaction.atomic
    def post(self, request):
        reg_id = request.COOKIES.get('registration_id')

        if not reg_id:
            return Response({"detail" : "registration id is missing"}, status=400)
        try:
            pending = (
                PendingRegistration.objects
                .select_for_update()
                .get(id=reg_id)
            )
        except PendingRegistration.DoesNotExist:
            raise Http404

        if pending.can_revalidate:
            pending.revalidate()
            # Send email
            return Response({"detail" : "registration revalidated"}, status=201)
        remaining_revalidation = pending.remaining_revalidation.total_seconds()
        return Response({"detail" : "revalidation_time_is_not_over", "remaining_revalidation" : remaining_revalidation}, status=400)

class VerifyRegistrationOTP(APIView):
    serializer_class = UserRegistrationSerializer

    @transaction.atomic
    def post(self, request):
        otp = request.data.get('otp')
        reg_id = request.COOKIES.get('registration_id')

        try:
            pending = (
                PendingRegistration.objects
                .select_for_update()
                .get(id=reg_id)
            )
        except PendingRegistration.DoesNotExist:
            raise Http404

        if pending.is_expired or pending.is_used:
            return Response({"detail" : "registration expired"}, status=401)
        if str(otp) == str(pending.otp):
            data = {
                "phone" : pending.phone,
                "email" : pending.email,
                "first_name" : pending.first_name,
                "last_name" : pending.last_name,
                "student_id" : pending.student_id,
                'hashed_password' : pending.password,
            }
            try:
                serialized_data = self.serializer_class(data = data)
                serialized_data.is_valid()
                user = serialized_data.save()
            except IntegrityError:
                return Response({"detail" : "user exists"}, status=400)
            pending.is_used = True

            pending.save()

            tokens = get_tokens_for_user(user)

            return Response({"detail" : "registration verified", "tokens" : tokens}, status=200)

        return Response({"detail": "otp is invalid"}, status=400)