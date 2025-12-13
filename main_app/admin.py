from django.contrib import admin
from main_app.models import Event, Course, Tag, TimePlan

admin.site.register(Event)
admin.site.register(Course)
admin.site.register(Tag)
admin.site.register(TimePlan)