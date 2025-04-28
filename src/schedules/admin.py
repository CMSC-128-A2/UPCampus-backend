from django.contrib import admin
from .models import Course, ClassSection

class ClassSectionInline(admin.TabularInline):
    model = ClassSection
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'created_at', 'updated_at')
    search_fields = ('course_code',)
    inlines = [ClassSectionInline]

@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'room', 'schedule', 'created_at', 'updated_at')
    list_filter = ('type', 'course')
    search_fields = ('section', 'room', 'schedule', 'course__course_code')
