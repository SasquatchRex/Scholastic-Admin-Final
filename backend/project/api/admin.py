from django.contrib import admin
from .models import Student,Subject,Mark

class MarkInline(admin.TabularInline):
    model = Mark
    extra = 1

class StudentAdmin(admin.ModelAdmin):
    inlines = [MarkInline]

admin.site.register(Student, StudentAdmin)
admin.site.register(Subject)
# admin.site.register(Mark)