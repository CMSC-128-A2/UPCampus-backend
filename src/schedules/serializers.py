from rest_framework import serializers
from .models import Course, ClassSection

class ClassSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSection
        fields = ['id', 'section', 'type', 'room', 'schedule']
        read_only_fields = ['id']

class CourseSerializer(serializers.ModelSerializer):
    sections = ClassSectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'course_code', 'sections']
        read_only_fields = ['id']

class CourseDetailSerializer(serializers.ModelSerializer):
    sections = ClassSectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'course_code', 'sections', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ClassSectionCreateSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(write_only=True)
    day = serializers.CharField(write_only=True)
    time = serializers.CharField(write_only=True)
    
    class Meta:
        model = ClassSection
        fields = ['id', 'course_code', 'section', 'type', 'room', 'day', 'time', 'schedule']
        read_only_fields = ['id', 'schedule']
    
    def create(self, validated_data):
        course_code = validated_data.pop('course_code')
        day = validated_data.pop('day')
        time = validated_data.pop('time')
        
        # Create the schedule string format
        schedule_string = f"{day} | {time}"
        validated_data['schedule'] = schedule_string
        
        # Get or create the course
        course, _ = Course.objects.get_or_create(course_code=course_code)
        validated_data['course'] = course
        
        return ClassSection.objects.create(**validated_data)

class ClassSectionUpdateSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(write_only=True, required=False)
    day = serializers.CharField(write_only=True)
    time = serializers.CharField(write_only=True)
    
    class Meta:
        model = ClassSection
        fields = ['id', 'course_code', 'section', 'type', 'room', 'day', 'time', 'schedule']
        read_only_fields = ['id', 'schedule']
    
    def update(self, instance, validated_data):
        # Extract scheduling information
        day = validated_data.pop('day', None)
        time = validated_data.pop('time', None)
        
        # If both day and time are provided, update the schedule
        if day is not None and time is not None:
            validated_data['schedule'] = f"{day} | {time}"
        
        # If course_code is provided, update the course
        course_code = validated_data.pop('course_code', None)
        if course_code is not None:
            course, _ = Course.objects.get_or_create(course_code=course_code)
            instance.course = course
        
        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance 