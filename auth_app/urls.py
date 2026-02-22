from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from auth_app.views.change_password import SendChangePasswordOTP, VerifyPasswordChangeOTP, ChangePassword
from auth_app.views.login import auth_me
from auth_app.views.registration import UserRegister, VerifyRegistrationOTP, RevalidateRegistrationOTP
from auth_app.views.forgot_password import ForgotPasswordSendOTP, ForgotPasswordVerifyOTPView
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name = 'login'),
    path('register/', UserRegister.as_view(), name = 'register'),
    path('register/verify/', VerifyRegistrationOTP.as_view(), name = 'verify'),
    path('register/revalidate/', RevalidateRegistrationOTP.as_view(), name = 'revalidate'),
    path('refresh/', TokenRefreshView.as_view(), name = 'refresh'),
    path('me/', auth_me, name = 'auth_me'),
    path('change-password/send-otp/', SendChangePasswordOTP.as_view(), name = 'send_change_password_otp'),
    path('change-password/verify/', VerifyPasswordChangeOTP.as_view(), name = 'verify_change_password'),
    path('change-password/', ChangePassword.as_view(), name = 'change_password'),
    path('forgot-password/send-otp/', ForgotPasswordSendOTP.as_view(), name= 'send_forgot_password_otp'),
    path('forgot-password/verify/', ForgotPasswordVerifyOTPView.as_view(), name= "verify_forgot_password"),
]