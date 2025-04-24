from django.db import models

class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.course_code

class ClassSection(models.Model):
    TYPE_CHOICES = [
        ('Lecture', 'Lecture'),
        ('Laboratory', 'Laboratory'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    section = models.CharField(max_length=10)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    room = models.CharField(max_length=20)
    schedule = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('course', 'section')
    
    def __str__(self):
        return f"{self.course.course_code} - {self.section} ({self.type})" 