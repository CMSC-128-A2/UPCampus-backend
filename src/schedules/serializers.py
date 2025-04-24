from rest_framework import serializers
from .models import Course, ClassSection

class ClassSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSection
        fields = ['id', 'section', 'type', 'room', 'schedule']

class CourseSerializer(serializers.ModelSerializer):
    sections = ClassSectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'course_code', 'sections']

class ClassSectionCreateSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(write_only=True)
    day = serializers.CharField(write_only=True)
    time = serializers.CharField(write_only=True)
    
    class Meta:
        model = ClassSection
        fields = ['course_code', 'section', 'type', 'room', 'day', 'time']
    
    def create(self, validated_data):
        course_code = validated_data.pop('course_code')
        day = validated_data.pop('day')
        time = validated_data.pop('time')
        
        # Format the schedule string
        schedule = f"{day} | {time}"
        
        # Get or create the course
        course, created = Course.objects.get_or_create(course_code=course_code)
        
        # Create the class section
        class_section = ClassSection.objects.create(
            course=course,
            schedule=schedule,
            **validated_data
        )
        
        return class_section 