from django.urls import path
from profile_app import views
urlpatterns = [
    path('events/', views.RegisteredEventsListAPIView.as_view(), name = "registered_events"),
    path('courses/', views.RegisteredCoursesListAPIView.as_view(), name = "registered_courses"),
    path('update/', views.ProfileUpdateAPIView.as_view(), name = "update_profile")
]