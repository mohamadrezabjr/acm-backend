from django.urls import  path
from main_app.views import event, course, general
urlpatterns = [
    path('events/', event.EventListAPIView.as_view(), name='events_list'),
    path('events/<str:slug>/', event.EventRetrieveAPIView.as_view(), name ='event_detail'),
    path('events/registration/<str:slug>/', event.EventRegistration.as_view(), name ='event_registration'),
    path('courses/', course.CourseListAPIView.as_view(), name='courses_list'),
    path('courses/<str:slug>/', course.CourseRetrieveAPIView.as_view(), name ='course_detail'),
    path('courses/registration/<str:slug>/', course.CourseRegistration.as_view(), name ="course_registration"),
    path('persons/', general.PersonListAPIView.as_view(), name='persons_list'),
    path('tags/', general.TagListAPIView.as_view(), name ='tags_list'),

]