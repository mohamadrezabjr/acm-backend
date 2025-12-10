from django.urls import  path
from main_app import views
urlpatterns = [
    path('events/', views.EventListAPIView.as_view(), name= 'events_list'),
]