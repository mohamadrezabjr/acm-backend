from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from auth_app.models import PasswordChangeOTP
from auth_app.utils import get_tokens_for_user, send_otp_email_for_password_reset
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class ChangePassword(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        user = request.user
        if not user.can_change_password:
            return Response({"cant_change_password" : "you can not change password"}, status=400)

        new_password = request.data.get('new_password')
        otp = request.data.get('otp')
        if new_password and otp:
            try:
                user_otp = user.password_change_otp
            except:
                return Response({"invalid_otp": "request otp first"}, status=status.HTTP_400_BAD_REQUEST)
            if user_otp.is_expired:
                return Response({"expired" : "otp is expired"}, status=status.HTTP_401_UNAUTHORIZED)
            if str(otp) == str(user_otp.otp):
                user.set_password(new_password)
                user.password_changed_at = timezone.now()
                user.token_version += 1
                user.save()
                user_otp.delete()
                tokens = get_tokens_for_user(user)

                return Response({"success" : "password changed", "tokens" : tokens}, status=status.HTTP_200_OK)
            return Response({"invalid_otp" : "otp is invalid"}, status=400)
        return Response({"missed" : "password and otp is required"}, status=400)

class SendChangePasswordOTP(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        user = request.user

        if not user.can_change_password:
            return Response({"cant_change_password" : "can't change password"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            otp = user.password_change_otp
        except :
            otp = PasswordChangeOTP.objects.create(user=user)
            send_otp_email_for_password_reset(otp.user.email, otp.otp)

            return Response({"success" : "code has been sent"}, status=status.HTTP_200_OK)

        if otp.can_revalidate:
            otp.revalidate()
            send_otp_email_for_password_reset(otp.user.email, otp.otp)

            return Response({"success" : "code has been sent"}, status=status.HTTP_200_OK)

        remaining_revalidation = otp.remaining_revalidation_time.total_seconds()
        return Response({"remaining_revalidation" : remaining_revalidation, "revalidation_time" : "you can not request another code"}, status=status.HTTP_400_BAD_REQUEST)

class VerifyPasswordChangeOTP(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        otp = request.data.get('otp')
        user = request.user
        try:
            user_otp = user.password_change_otp
        except :
            return Response({"invalid_otp" : "request otp first"}, status=400)
        if user_otp.is_expired:
            return Response({"expired" : "otp is expired"}, status=status.HTTP_401_UNAUTHORIZED)
        if str(otp) == str(user_otp.otp):
            return Response({"success" : "otp is valid"}, status=status.HTTP_200_OK)
        return Response({"invalid_otp" : "otp is invalid"}, status=400)