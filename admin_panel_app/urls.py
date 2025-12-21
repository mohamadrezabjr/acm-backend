from django.urls import path
from admin_panel_app import views
urlpatterns = [
    path('dashboard-stats/', views.AdminDashboardStatus.as_view())
]