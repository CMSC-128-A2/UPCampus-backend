from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework.views import APIView
from datetime import datetime
import re

from .models import Course, ClassSection, Department, Faculty, AdminUser, Room
from .serializers import (
    CourseSerializer,
    CourseDetailSerializer,
    ClassSectionSerializer,
    ClassSectionCreateSerializer,
    ClassSectionUpdateSerializer,
    DepartmentSerializer,
    FacultySerializer,
    FacultyDetailSerializer,
    AdminUserSerializer,
    AdminUserDetailSerializer,
    RoomSerializer
)
from .utils import check_schedule_conflicts

class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing courses and their sections
    """
    queryset = Course.objects.all().prefetch_related('sections')
    serializer_class = CourseSerializer
    
    def list(self, request, *args, **kwargs):
        """Override list method to add extra logging and ensure related sections are included"""
        print(f"CourseViewSet.list called by {request.user}")
        queryset = self.get_queryset()
        print(f"Found {queryset.count()} courses")
        
        # Trigger prefetch of related sections
        for course in queryset:
            print(f"Course: {course.course_code}, Sections: {course.sections.count()}")
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    @action(detail=True, methods=['delete'], url_path='sections/(?P<section_name>[^/.]+)')
    def delete_section(self, request, pk=None, section_name=None):
        """Delete a section from a course"""
        print(f"Deleting section {section_name} from course {pk}")
        course = self.get_object()
        try:
            section = course.sections.get(section=section_name)
            section.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ClassSection.DoesNotExist:
            return Response(
                {"detail": "Section not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing rooms
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
    def create(self, request, *args, **kwargs):
        print(f"RoomViewSet.create called with data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            room = request.data.get('room')
            floor = request.data.get('floor')
            return Response(
                {"detail": f"Room {room} on floor {floor} already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

class ClassSectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing class sections
    """
    queryset = ClassSection.objects.all().select_related('course', 'faculty')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ClassSectionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClassSectionUpdateSerializer
        return ClassSectionSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new section with logging and error handling"""
        print(f"ClassSectionViewSet.create called with data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check for faculty schedule conflicts
        if hasattr(serializer, '_conflicts') and serializer._conflicts:
            return Response(
                {
                    "detail": "Faculty schedule conflict detected",
                    "conflicts": serializer._conflicts
                },
                status=status.HTTP_409_CONFLICT
            )
        
        try:
            self.perform_create(serializer)
            
            # Return the created instance using ClassSectionSerializer to include room_display
            instance = serializer.instance
            response_serializer = ClassSectionSerializer(instance)
            headers = self.get_success_headers(response_serializer.data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            course_code = request.data.get('course_code')
            section = request.data.get('section')
            return Response(
                {"detail": f"Section {section} already exists for {course_code}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """Update an existing section with logging and error handling"""
        print(f"ClassSectionViewSet.update called with data: {request.data}")
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Check for faculty schedule conflicts
        if hasattr(serializer, '_conflicts') and serializer._conflicts:
            return Response(
                {
                    "detail": "Faculty schedule conflict detected",
                    "conflicts": serializer._conflicts
                },
                status=status.HTTP_409_CONFLICT
            )
        
        try:
            self.perform_update(serializer)
            
            # Return the updated instance using ClassSectionSerializer to include room_display
            instance = serializer.instance
            response_serializer = ClassSectionSerializer(instance)
            return Response(response_serializer.data)
        except IntegrityError:
            course_code = request.data.get('course_code')
            section = request.data.get('section')
            return Response(
                {"detail": f"Section {section} already exists for {course_code}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing academic departments
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    
    def create(self, request, *args, **kwargs):
        print(f"DepartmentViewSet.create called with data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            name = request.data.get('name')
            return Response(
                {"detail": f"Department {name} already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

class FacultyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing faculty members
    """
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    
    def get_queryset(self):
        queryset = Faculty.objects.all()
        
        # Get the admin user from the request
        admin_id = self.request.query_params.get('admin_id')
        if admin_id:
            try:
                admin = AdminUser.objects.get(id=admin_id)
                # If admin is not a superuser, filter by department
                if not admin.is_superuser and admin.department:
                    queryset = queryset.filter(department=admin.department)
            except AdminUser.DoesNotExist:
                pass
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FacultyDetailSerializer
        return FacultySerializer
    
    def list(self, request, *args, **kwargs):
        print(f"FacultyViewSet.list called by {request.user}")
        queryset = self.get_queryset()
        print(f"Found {queryset.count()} faculty members")
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def schedules(self, request, pk=None):
        """Get all schedules for a faculty member"""
        faculty = self.get_object()
        sections = faculty.class_sections.all().select_related('course')
        serializer = ClassSectionSerializer(sections, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print(f"FacultyViewSet.create called with data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            email = request.data.get('email')
            return Response(
                {"detail": f"Faculty with email {email} already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

class AdminUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing admin users
    """
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AdminUserDetailSerializer
        return AdminUserSerializer
    
    @action(detail=False, methods=['post'], url_path='authenticate')
    def authenticate(self, request):
        """Authenticate an admin user"""
        user_id = request.data.get('user_id')
        password = request.data.get('password')
        
        if not user_id or not password:
            return Response(
                {"detail": "User ID and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            admin = AdminUser.objects.get(user_id=user_id)
            if admin.password == password:
                # Return admin details without password
                serializer = AdminUserSerializer(admin)
                return Response(serializer.data)
            else:
                return Response(
                    {"detail": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except AdminUser.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    def create(self, request, *args, **kwargs):
        print(f"AdminUserViewSet.create called with data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            if 'email' in str(e):
                return Response(
                    {"detail": f"Email already in use"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if 'user_id' in str(e):
                return Response(
                    {"detail": f"User ID already in use"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"detail": f"Admin user could not be created"},
                status=status.HTTP_400_BAD_REQUEST
            )

class ScheduleConflictView(APIView):
    """
    API view to check for schedule conflicts
    """
    def post(self, request):
        day = request.data.get('day', '')
        time = request.data.get('time', '')
        room = request.data.get('room', '')
        faculty_id = request.data.get('faculty_id', '')
        exclude_section_id = request.data.get('exclude_section_id', None)
        
        # Validate input
        if not all([day, time, room]):
            return Response(
                {"detail": "Day, time, and room are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse the time string to get start and end times
        # Format: "11:00 AM - 12:00 PM"
        time_pattern = r"(\d+:\d+\s*[AP]M)\s*-\s*(\d+:\d+\s*[AP]M)"
        time_match = re.match(time_pattern, time)
        
        if not time_match:
            return Response(
                {"detail": "Invalid time format. Expected format: '11:00 AM - 12:00 PM'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        start_time_str, end_time_str = time_match.groups()
        
        # Convert to datetime objects for comparison
        try:
            start_time = datetime.strptime(start_time_str.strip(), "%I:%M %p")
            end_time = datetime.strptime(end_time_str.strip(), "%I:%M %p")
        except ValueError:
            return Response(
                {"detail": "Invalid time format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for conflicts in the database
        conflicts = []
        
        # Check for faculty conflicts if faculty_id is provided
        if faculty_id:
            faculty_conflicts = check_schedule_conflicts(day, time, faculty_id, room, exclude_section_id)
            conflicts.extend(faculty_conflicts)
        
        # Get all class sections with the same day, excluding the section being edited if provided
        day_sections = ClassSection.objects.filter(schedule__contains=day)
        
        # Exclude the section being edited if provided
        if exclude_section_id:
            day_sections = day_sections.exclude(id=exclude_section_id)
        
        for section in day_sections:
            # Parse the schedule string (format: "M TH | 11:00 AM - 12:00 PM")
            section_parts = section.schedule.split('|')
            if len(section_parts) != 2:
                continue
                
            section_days, section_time = section_parts[0].strip(), section_parts[1].strip()
            section_day_list = section_days.split()
            
            # Skip if the day doesn't match
            if not any(d in day.split() for d in section_day_list):
                continue
            
            # Check time overlap
            section_time_match = re.match(time_pattern, section_time)
            if not section_time_match:
                continue
                
            section_start_str, section_end_str = section_time_match.groups()
            
            try:
                section_start = datetime.strptime(section_start_str.strip(), "%I:%M %p")
                section_end = datetime.strptime(section_end_str.strip(), "%I:%M %p")
            except ValueError:
                continue
            
            # Check for time overlap
            has_time_overlap = (
                (start_time <= section_start < end_time) or
                (start_time < section_end <= end_time) or
                (section_start <= start_time < section_end) or
                (section_start < end_time <= section_end)
            )
            
            if has_time_overlap and section.room == room:
                # We already checked for faculty conflicts above, so we only need to check for room conflicts here
                conflict = {
                    "type": "room",
                    "course": section.course.course_code,
                    "section": section.section,
                    "schedule": section.schedule,
                    "room": section.room
                }
                if conflict not in conflicts:  # Avoid duplicates
                    conflicts.append(conflict)
        
        if conflicts:
            return Response(
                {
                    "detail": "Schedule conflict detected",
                    "conflicts": conflicts
                },
                status=status.HTTP_409_CONFLICT
            )
        
        return Response({"detail": "No conflicts found"}, status=status.HTTP_200_OK)

class NewSemesterView(APIView):
    """
    API view to reset data for a new semester
    Deletes all class sections (schedules) but keeps rooms and courses
    """
    def post(self, request):
        try:
            # Delete all class sections (this removes all schedules)
            deleted_count = ClassSection.objects.all().count()
            ClassSection.objects.all().delete()
            
            print(f"New semester reset: Deleted {deleted_count} class sections")
            
            return Response(
                {
                    "detail": f"New semester started successfully. Deleted {deleted_count} schedules.",
                    "deleted_schedules": deleted_count
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"Error during new semester reset: {e}")
            return Response(
                {"detail": "Failed to start new semester. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
