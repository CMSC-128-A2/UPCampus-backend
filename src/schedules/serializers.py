from rest_framework import serializers
from .models import Course, ClassSection, Department, Faculty, AdminUser, Room
from .utils import check_schedule_conflicts

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room', 'floor']
        read_only_fields = ['id']

class ClassSectionSerializer(serializers.ModelSerializer):
    faculty_name = serializers.SerializerMethodField()
    room_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassSection
        fields = ['id', 'section', 'type', 'room', 'room_display', 'schedule', 'faculty', 'faculty_name']
        read_only_fields = ['id']
    
    def get_faculty_name(self, obj):
        return obj.faculty.name if obj.faculty else None
    
    def get_room_display(self, obj):
        return str(obj.room) if obj.room else None

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
        fields = ['id', 'name', 'email', 'department', 'department_name']
        read_only_fields = ['id']
    
    def get_department_name(self, obj):
        return obj.department.name

class FacultyDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    class_sections = ClassSectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'email', 'department', 'department_name', 'class_sections', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_department_name(self, obj):
        return obj.department.name

class AdminUserSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AdminUser
        fields = ['id', 'name', 'email', 'user_id', 'password', 'department', 'department_name', 'is_superuser']
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True}}
    
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

class AdminUserDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AdminUser
        fields = ['id', 'name', 'email', 'user_id', 'password', 'department', 'department_name', 'is_superuser', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

class ClassSectionCreateSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(write_only=True)
    day = serializers.CharField(write_only=True)
    time = serializers.CharField(write_only=True)
    faculty_id = serializers.IntegerField(write_only=True, required=False)
    room_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ClassSection
        fields = ['id', 'course_code', 'section', 'type', 'room_id', 'day', 'time', 'schedule', 'faculty_id', 'faculty', 'room']
        read_only_fields = ['id', 'schedule', 'faculty', 'room']
    
    def validate(self, data):
        """Check for faculty and room schedule conflicts but don't raise an error - this is handled in the view"""
        day = data.get('day')
        time = data.get('time')
        faculty_id = data.get('faculty_id')
        room_id = data.get('room_id')
        
        # Only check for conflicts if we have the necessary data
        if day and time and (faculty_id or room_id):
            conflicts = check_schedule_conflicts(
                day=day, 
                time=time, 
                faculty_id=faculty_id, 
                room_id=room_id
            )
            
            if conflicts:
                # Store the conflicts on the instance for the view to access
                self._conflicts = conflicts
        
        return data
    
    def create(self, validated_data):
        course_code = validated_data.pop('course_code')
        day = validated_data.pop('day')
        time = validated_data.pop('time')
        faculty_id = validated_data.pop('faculty_id', None)
        room_id = validated_data.pop('room_id')
        
        # Create the schedule string format
        schedule_string = f"{day} | {time}"
        validated_data['schedule'] = schedule_string
        
        # Get or create the course
        course, _ = Course.objects.get_or_create(course_code=course_code)
        validated_data['course'] = course
        
        # Set room
        try:
            room = Room.objects.get(id=room_id)
            validated_data['room'] = room
        except Room.DoesNotExist:
            raise serializers.ValidationError("Room not found")
        
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
    day = serializers.CharField(write_only=True, required=False)
    time = serializers.CharField(write_only=True, required=False)
    faculty_id = serializers.IntegerField(write_only=True, required=False)
    room_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ClassSection
        fields = ['id', 'course_code', 'section', 'type', 'room_id', 'day', 'time', 'schedule', 'faculty_id', 'faculty', 'room']
        read_only_fields = ['id', 'schedule', 'faculty', 'room']
    
    def validate(self, data):
        """Check for faculty and room schedule conflicts but don't raise an error - this is handled in the view"""
        day = data.get('day')
        time = data.get('time')
        faculty_id = data.get('faculty_id')
        room_id = data.get('room_id')
        instance = self.instance
        
        # We need to check for conflicts if any scheduling-related field is changing
        if instance and (day is not None or time is not None or room_id is not None):
            # Use existing values for any missing fields
            if faculty_id is None and instance.faculty:
                faculty_id = instance.faculty.id
            
            if day is None and instance.schedule:
                parts = instance.schedule.split('|')
                if len(parts) > 0:
                    day = parts[0].strip()
            
            if time is None and instance.schedule:
                parts = instance.schedule.split('|')
                if len(parts) > 1:
                    time = parts[1].strip()
            
            if room_id is None:
                room_id = instance.room.id if instance.room else None
            
            # Now check for conflicts if we have all the necessary data
            if day and time and (faculty_id or room_id):
                conflicts = check_schedule_conflicts(
                    day=day, 
                    time=time, 
                    faculty_id=faculty_id, 
                    room_id=room_id,
                    exclude_section_id=instance.id
                )
                
                if conflicts:
                    # Store the conflicts on the instance for the view to access
                    self._conflicts = conflicts
        
        return data
    
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
        
        # Set room if provided
        room_id = validated_data.pop('room_id', None)
        if room_id is not None:
            try:
                room = Room.objects.get(id=room_id)
                instance.room = room
            except Room.DoesNotExist:
                pass
        
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