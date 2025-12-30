from django.urls import path
from admin_panel_app import views
urlpatterns = [
    path('dashboard-stats/', views.AdminDashboardStatus.as_view()),

    path('events/', views.AdminEventListAPIView.as_view(), name= 'admin_event_list'),
    path('events/create/', views.EventCreateAPIView.as_view(), name='event_create'),
    path('events/<str:slug>/', views.AdminEventRetrieveAPIView.as_view(), name= 'admin_event_retrieve'),
    path('events/<str:slug>/deactivate/', views.DeactivateEvent.as_view(), name = 'event_deactivate'),
    path('events/<str:slug>/update/', views.EventUpdateAPIView.as_view(), name = 'event_update'),

    path('courses/', views.AdminCourseListAPIView.as_view(), name= 'admin_course_list'),
    path('courses/create/', views.CourseCreateAPIView.as_view(), name='course_create'),
    path('courses/<str:slug>/', views.AdminCourseRetrieveAPIView.as_view(), name = 'admin_course_retrieve'),
    path('courses/<str:slug>/deactivate/', views.DeactivateCourse.as_view(), name='course_deactivate'),
    path('courses/<str:slug>/update/', views.CourseUpdateAPIView.as_view(), name = 'course_update'),

    path('registrations/events/', views.AdminEventParticipantListAPIView.as_view(), name= 'admin_registration_event_list'),
    path('registrations/courses/', views.AdminEventParticipantListAPIView.as_view(), name = 'admin_registration_course_list'),

]