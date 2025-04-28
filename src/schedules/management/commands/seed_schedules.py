from django.core.management.base import BaseCommand
from schedules.models import Course, ClassSection

class Command(BaseCommand):
    help = 'Seeds the database with initial schedule data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding schedules data...')
        
        # Clear existing data
        ClassSection.objects.all().delete()
        Course.objects.all().delete()
        
        # Create courses and sections
        courses_data = [
            {
                'course_code': 'CMSC 126',
                'sections': [
                    {
                        'section': 'A',
                        'type': 'Lecture',
                        'room': 'SCI 405',
                        'schedule': 'M TH | 11:00 AM - 12:00 PM'
                    },
                    {
                        'section': 'A1',
                        'type': 'Laboratory',
                        'room': 'SCI 402',
                        'schedule': 'TH | 3:00 PM - 6:00 PM'
                    },
                    {
                        'section': 'A2',
                        'type': 'Laboratory',
                        'room': 'SCI 402',
                        'schedule': 'M | 3:00 PM - 6:00 PM'
                    }
                ]
            },
            {
                'course_code': 'CMSC 129',
                'sections': [
                    {
                        'section': 'A',
                        'type': 'Lecture',
                        'room': 'SCI 405',
                        'schedule': 'M TH | 9:00 AM - 10:00 AM'
                    },
                    {
                        'section': 'A1',
                        'type': 'Laboratory',
                        'room': 'SCI 404',
                        'schedule': 'T | 9:00 AM - 12:00 PM'
                    },
                    {
                        'section': 'A2',
                        'type': 'Laboratory',
                        'room': 'SCI 404',
                        'schedule': 'F | 9:00 AM - 12:00 PM'
                    }
                ]
            },
            {
                'course_code': 'MATH 101',
                'sections': [
                    {
                        'section': 'B',
                        'type': 'Lecture',
                        'room': 'SCI 301',
                        'schedule': 'T F | 1:00 PM - 2:30 PM'
                    },
                    {
                        'section': 'B1',
                        'type': 'Laboratory',
                        'room': 'SCI 302',
                        'schedule': 'W | 1:00 PM - 4:00 PM'
                    }
                ]
            },
            {
                'course_code': 'PHYS 105',
                'sections': [
                    {
                        'section': 'C',
                        'type': 'Lecture',
                        'room': 'SCI 401',
                        'schedule': 'M W | 2:00 PM - 3:30 PM'
                    },
                    {
                        'section': 'C1',
                        'type': 'Laboratory',
                        'room': 'SCI 408',
                        'schedule': 'F | 10:00 AM - 1:00 PM'
                    },
                    {
                        'section': 'C2',
                        'type': 'Laboratory',
                        'room': 'SCI 408',
                        'schedule': 'F | 2:00 PM - 5:00 PM'
                    }
                ]
            }
        ]
        
        for course_data in courses_data:
            course = Course.objects.create(course_code=course_data['course_code'])
            
            for section_data in course_data['sections']:
                ClassSection.objects.create(
                    course=course,
                    section=section_data['section'],
                    type=section_data['type'],
                    room=section_data['room'],
                    schedule=section_data['schedule']
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded schedules data')) 