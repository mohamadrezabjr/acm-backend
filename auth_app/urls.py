from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from auth_app import views
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name = 'login'),
    path('register/', views.UserRegister.as_view(), name = 'register'),
    path('register/verify/', views.VerifyRegistrationOTP.as_view(), name = 'verify'),
    path('register/revalidate/', views.RevalidateRegistrationOTP.as_view(), name = 'revalidate'),
    path('refresh/', TokenRefreshView.as_view(), name = 'refresh'),
    path('me/', views.auth_me, name = 'auth_me')
]