from django.contrib import admin
from .models import Course, ClassSection

class ClassSectionInline(admin.TabularInline):
    model = ClassSection
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code',)
    inlines = [ClassSectionInline]
    search_fields = ('course_code',)

@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ('course', 'section', 'type', 'room', 'schedule')
    list_filter = ('type', 'room')
    search_fields = ('course__course_code', 'section', 'room', 'schedule') 