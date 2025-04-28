from django.db import models

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
    room = models.CharField(max_length=50)
    schedule = models.CharField(max_length=100)  # Format: "M TH | 11:00 AM - 12:00 PM"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.course_code} - {self.section} ({self.type})"
    
    class Meta:
        ordering = ['course', 'section']
        unique_together = ['course', 'section']
