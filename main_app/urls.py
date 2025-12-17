from django.urls import  path
from main_app.views import events_views, courses_views, general_views
urlpatterns = [
    path('events/', events_views.EventListAPIView.as_view(), name= 'events_list'),
    path('events/create/', events_views.EventCreateAPIView.as_view(), name='create_event'),
    path('events/<str:slug>/', events_views.EventRetrieveAPIView.as_view(), name = 'event_detail'),
    path('events/registration/<str:slug>/', events_views.EventRegistration.as_view(), name = 'event_registration'),
    path('courses/', courses_views.CourseListAPIView.as_view(), name= 'courses_list'),
    path('courses/<str:slug>/', courses_views.CourseRetrieveAPIView.as_view(), name = 'course_detail'),
    path('persons/', general_views.PersonListAPIView.as_view(), name= 'persons_list'),
    path('tags/', general_views.TagListAPIView.as_view(), name = 'tags_list'),
]