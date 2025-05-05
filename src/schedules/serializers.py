from rest_framework import serializers
from .models import Course, ClassSection, Department, Faculty, AdminUser

class ClassSectionSerializer(serializers.ModelSerializer):
    faculty_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassSection
        fields = ['id', 'section', 'type', 'room', 'schedule', 'faculty', 'faculty_name']
        read_only_fields = ['id']
    
    def get_faculty_name(self, obj):
        return obj.faculty.name if obj.faculty else None

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

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']
        read_only_fields = ['id']

class FacultySerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'department', 'department_name']
        read_only_fields = ['id']
    
    def get_department_name(self, obj):
        return obj.department.name

class FacultyDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    class_sections = ClassSectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'department', 'department_name', 'class_sections', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_department_name(self, obj):
        return obj.department.name

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ['id', 'name', 'email', 'user_id', 'password']
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True}}

class AdminUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ['id', 'name', 'email', 'user_id', 'password', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ClassSectionCreateSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(write_only=True)
    day = serializers.CharField(write_only=True)
    time = serializers.CharField(write_only=True)
    faculty_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ClassSection
        fields = ['id', 'course_code', 'section', 'type', 'room', 'day', 'time', 'schedule', 'faculty_id', 'faculty']
        read_only_fields = ['id', 'schedule', 'faculty']
    
    def create(self, validated_data):
        course_code = validated_data.pop('course_code')
        day = validated_data.pop('day')
        time = validated_data.pop('time')
        faculty_id = validated_data.pop('faculty_id', None)
        
        # Create the schedule string format
        schedule_string = f"{day} | {time}"
        validated_data['schedule'] = schedule_string
        
        # Get or create the course
        course, _ = Course.objects.get_or_create(course_code=course_code)
        validated_data['course'] = course
        
        # Set faculty if provided
        if faculty_id:
            try:
                faculty = Faculty.objects.get(id=faculty_id)
                validated_data['faculty'] = faculty
            except Faculty.DoesNotExist:
                pass
        
        return ClassSection.objects.create(**validated_data)

class ClassSectionUpdateSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(write_only=True, required=False)
    day = serializers.CharField(write_only=True)
    time = serializers.CharField(write_only=True)
    faculty_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ClassSection
        fields = ['id', 'course_code', 'section', 'type', 'room', 'day', 'time', 'schedule', 'faculty_id', 'faculty']
        read_only_fields = ['id', 'schedule', 'faculty']
    
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
        
        # Set faculty if provided
        faculty_id = validated_data.pop('faculty_id', None)
        if faculty_id is not None:
            try:
                faculty = Faculty.objects.get(id=faculty_id)
                instance.faculty = faculty
            except Faculty.DoesNotExist:
                pass
        
        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance 