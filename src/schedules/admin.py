from django.contrib import admin
from .models import Course, ClassSection, Department, Faculty, AdminUser, Room

class ClassSectionInline(admin.TabularInline):
    model = ClassSection
    extra = 0
    fields = ('section', 'type', 'room', 'schedule', 'faculty')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'created_at', 'updated_at')
    search_fields = ('course_code',)
    inlines = [ClassSectionInline]

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room', 'floor', 'created_at', 'updated_at')
    search_fields = ('room', 'floor')
    list_filter = ('floor',)

@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'course', 'section', 'type', 'room', 'faculty', 'schedule')
    list_filter = ('course', 'type')
    search_fields = ('course__course_code', 'section', 'room__room', 'schedule')
    autocomplete_fields = ('course', 'faculty', 'room')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'created_at')
    list_filter = ('department',)
    search_fields = ('name', 'email')
    autocomplete_fields = ('department',)

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'user_id', 'created_at')
    search_fields = ('name', 'email', 'user_id')
    readonly_fields = ('created_at', 'updated_at')
