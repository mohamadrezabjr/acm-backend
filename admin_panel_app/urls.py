from django.urls import path
from admin_panel_app import views
urlpatterns = [
    path('dashboard-stats/', views.AdminDashboardStatus.as_view()),
    path('events/', views.AdminEventsListAPIView.as_view(), name = 'admin_events'),
    path('courses/', views.AdminCourseListAPIView.as_view(), name = 'admin_courses'),
]