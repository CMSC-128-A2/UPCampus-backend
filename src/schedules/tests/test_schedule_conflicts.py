from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..models import Course, ClassSection, Department, Faculty
from ..utils import check_faculty_schedule_conflicts


class ScheduleConflictTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test data
        self.department = Department.objects.create(name="Computer Science")
        self.faculty = Faculty.objects.create(name="John Doe", department=self.department)
        self.course = Course.objects.create(course_code="CS101")
        
        # Create a class section with schedule
        self.section = ClassSection.objects.create(
            course=self.course,
            section="A",
            type="Lecture",
            room="Room 101",
            schedule="M | 10:00 AM - 11:30 AM",
            faculty=self.faculty
        )
    
    def test_faculty_schedule_conflict_detection(self):
        """Test that faculty schedule conflicts are correctly detected"""
        # Should detect conflict with same time and same day
        conflicts = check_faculty_schedule_conflicts(
            day="M",
            time="10:00 AM - 11:30 AM",
            faculty_id=self.faculty.id
        )
        self.assertEqual(len(conflicts), 1)
        
        # Should detect conflict with overlapping time
        conflicts = check_faculty_schedule_conflicts(
            day="M",
            time="10:30 AM - 12:00 PM",
            faculty_id=self.faculty.id
        )
        self.assertEqual(len(conflicts), 1)
        
        # Should detect conflict with contained time
        conflicts = check_faculty_schedule_conflicts(
            day="M",
            time="10:15 AM - 11:15 AM",
            faculty_id=self.faculty.id
        )
        self.assertEqual(len(conflicts), 1)
        
        # Should not detect conflict with different day
        conflicts = check_faculty_schedule_conflicts(
            day="T",
            time="10:00 AM - 11:30 AM",
            faculty_id=self.faculty.id
        )
        self.assertEqual(len(conflicts), 0)
        
        # Should not detect conflict with non-overlapping time
        conflicts = check_faculty_schedule_conflicts(
            day="M",
            time="11:30 AM - 1:00 PM",
            faculty_id=self.faculty.id
        )
        self.assertEqual(len(conflicts), 0)
    
    def test_create_section_with_conflict(self):
        """Test that creating a section with a faculty schedule conflict fails"""
        url = reverse('classsection-list')
        data = {
            'course_code': 'CS102',
            'section': 'A',
            'type': 'Lecture',
            'room': 'Room 102',
            'day': 'M',
            'time': '10:00 AM - 11:30 AM',
            'faculty_id': self.faculty.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        
        # Creating with a different day should work
        data['day'] = 'T'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_update_section_with_conflict(self):
        """Test that updating a section to create a faculty schedule conflict fails"""
        # Create a second section for the same faculty member but with a different time
        section2 = ClassSection.objects.create(
            course=self.course,
            section="B",
            type="Lecture",
            room="Room 102",
            schedule="T | 10:00 AM - 11:30 AM",
            faculty=self.faculty
        )
        
        url = reverse('classsection-detail', args=[section2.id])
        data = {
            'day': 'M',
            'time': '10:00 AM - 11:30 AM'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        
        # Updating to a non-conflicting time should work
        data['time'] = '1:00 PM - 2:30 PM'
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK) 