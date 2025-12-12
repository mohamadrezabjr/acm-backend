from django.urls import  path
from main_app import views
urlpatterns = [
    path('events/', views.EventListAPIView.as_view(), name= 'events_list'),
    path('events/create/', views.EventCreateAPIView.as_view(), name='create_event'),
    path('events/<str:slug>/', views.EventRetrieveAPIView.as_view(), name = 'event_detail')
]