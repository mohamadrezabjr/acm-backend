from django.urls import path
from admin_panel_app.views.dashboard import AdminDashboardStatusAPIView
from admin_panel_app.views.events import (
    EventCreateAPIView,
    EventUpdateAPIView,
    AdminEventParticipantListAPIView,
    AdminEventListAPIView,
    DeactivateEventAPIView,
    AdminEventRetrieveAPIView,
)
from admin_panel_app.views.courses import (
    AdminCourseListAPIView,
    CourseCreateAPIView,
    AdminCourseRetrieveAPIView,
    DeactivateCourseAPIView,
    CourseUpdateAPIView,
    AdminCourseParticipantListAPIView
)
from admin_panel_app.views.users import (
    UserListRetrieveAPIView, UserDetailAPIView
)

urlpatterns = [
    path('dashboard-stats/', AdminDashboardStatusAPIView.as_view()),

    path('events/', AdminEventListAPIView.as_view(), name= 'admin_event_list'),
    path('events/create/', EventCreateAPIView.as_view(), name='event_create'),
    path('events/<str:slug>/', AdminEventRetrieveAPIView.as_view(), name= 'admin_event_retrieve'),
    path('events/<str:slug>/deactivate/', DeactivateEventAPIView.as_view(), name = 'event_deactivate'),
    path('events/<str:slug>/update/', EventUpdateAPIView.as_view(), name = 'event_update'),

    path('courses/', AdminCourseListAPIView.as_view(), name= 'admin_course_list'),
    path('courses/create/', CourseCreateAPIView.as_view(), name='course_create'),
    path('courses/<str:slug>/', AdminCourseRetrieveAPIView.as_view(), name = 'admin_course_retrieve'),
    path('courses/<str:slug>/deactivate/', DeactivateCourseAPIView.as_view(), name='course_deactivate'),
    path('courses/<str:slug>/update/', CourseUpdateAPIView.as_view(), name = 'course_update'),

    path('registrations/events/', AdminEventParticipantListAPIView.as_view(), name= 'admin_registration_event_list'),
    path('registrations/courses/', AdminCourseParticipantListAPIView.as_view(), name = 'admin_registration_course_list'),

    path('users/', UserListRetrieveAPIView.as_view(), name = 'users_list'),
    path('users/<pk>/', UserDetailAPIView.as_view(), name = "user_detail")

]