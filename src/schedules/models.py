from django.db import models
from django.core.validators import RegexValidator

# Create your models here.

class Course(models.Model):
    """Model representing a course"""
    course_code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.course_code

    class Meta:
        ordering = ['course_code']


class Department(models.Model):
    """Model representing an academic department"""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Room(models.Model):
    """Model representing a room"""
    room = models.CharField(max_length=50)
    floor = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.room}"

    class Meta:
        ordering = ['room']
        unique_together = ['room', 'floor']


class Faculty(models.Model):
    """Model representing a faculty member or professor"""
    name = models.CharField(max_length=100)
    email = models.EmailField(
        validators=[
            RegexValidator(
                regex=r'^[\w\.-]+@up\.edu\.ph$',
                message='Email must be in the format: "example@up.edu.ph"',
                code='invalid_email'
            )
        ],
        unique=True
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='faculty_members')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.department})"
    
    class Meta:
        verbose_name_plural = "Faculty"
        ordering = ['name']


class AdminUser(models.Model):
    """Model representing an admin user"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    user_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)  # In production, this should use proper password hashing
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_users')
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    class Meta:
        ordering = ['name']


class ClassSection(models.Model):
    """Model representing a class section of a course"""
    LECTURE = 'Lecture'
    LABORATORY = 'Laboratory'
    
    SECTION_TYPE_CHOICES = [
        (LECTURE, 'Lecture'),
        (LABORATORY, 'Laboratory'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    section = models.CharField(max_length=10)
    type = models.CharField(max_length=20, choices=SECTION_TYPE_CHOICES, default=LECTURE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='class_sections')
    schedule = models.CharField(max_length=100)  # Format: "M TH | 11:00 AM - 12:00 PM"
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_sections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.course_code} - {self.section} ({self.type})"
    
    class Meta:
        ordering = ['course', 'section']
        unique_together = ['course', 'section']
