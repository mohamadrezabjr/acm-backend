from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from auth_app.models import User, PasswordChangeOTP
from auth_app.utils import send_otp_email_for_forgot_password, get_tokens_for_user


class ForgotPasswordSendOTP(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"success" : "code has bean sent"}, status=status.HTTP_200_OK)

        if not user.can_change_password:
            return Response({"cant_change_password" : "can't change password"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            otp = user.password_change_otp
        except:
            otp = PasswordChangeOTP.objects.create(user=user)
            send_otp_email_for_forgot_password(otp.user.email, otp.otp)
            return Response({"success" : "code has been sent"}, status=status.HTTP_200_OK)

        if otp.can_revalidate:
            otp.revalidate()
            send_otp_email_for_forgot_password(otp.user.email, otp.otp)
            return Response({"success" : "code has been sent"}, status=status.HTTP_200_OK)

        remaining_revalidation = otp.remaining_revalidation_time.total_seconds()
        return Response({"remaining_revalidation" : remaining_revalidation, "revalidation_time" : "you can not request another code"}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordVerifyOTPView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        otp = request.data.get('otp')
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"invalid_otp" : "otp is invalid"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_otp = user.password_change_otp
        except :
            return Response({"invalid_otp" : "otp is invalid"}, status=status.HTTP_400_BAD_REQUEST)

        if user_otp.is_expired:
            return Response({"expired" : "otp is expired"}, status=status.HTTP_400_BAD_REQUEST)

        if str(user_otp.otp) != str(otp):
            return Response({"invalid_otp" : "otp is expired"}, status=status.HTTP_400_BAD_REQUEST)

        tokens = get_tokens_for_user(user)
        print(tokens)
        return Response({"success" : "verified successfully", "tokens": tokens}, status=status.HTTP_200_OK)