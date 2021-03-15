from django.contrib import admin
from .models import UserProfile, Glucose, Carbohydrate, Insulin, RecordingCategory
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Glucose)
admin.site.register(Carbohydrate)
admin.site.register(Insulin)
admin.site.register(RecordingCategory)


