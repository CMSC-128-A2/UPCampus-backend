import random
from django.core.management.base import BaseCommand
from django.db import transaction
from schedules.models import Course, ClassSection, Department, Faculty, AdminUser

class Command(BaseCommand):
    help = 'Generates initial test data for the UPCampus app'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        AdminUser.objects.all().delete()
        ClassSection.objects.all().delete()
        Faculty.objects.all().delete()
        Department.objects.all().delete()
        Course.objects.all().delete()
        
        try:
            with transaction.atomic():
                # Create departments
                self.stdout.write('Creating departments...')
                departments = {
                    'Biology': Department.objects.create(name='Biology'),
                    'Computer Science': Department.objects.create(name='Computer Science'),
                    'Mathematics': Department.objects.create(name='Mathematics'),
                    'Statistics': Department.objects.create(name='Statistics'),
                }
                
                # Create courses
                self.stdout.write('Creating courses...')
                courses = {
                    'CMSC 126': Course.objects.create(course_code='CMSC 126'),
                    'CMSC 129': Course.objects.create(course_code='CMSC 129'),
                    'MATH 101': Course.objects.create(course_code='MATH 101'),
                    'STAT 101': Course.objects.create(course_code='STAT 101'),
                    'BIO 101': Course.objects.create(course_code='BIO 101'),
                }
                
                # Create faculty members
                self.stdout.write('Creating faculty members...')
                faculty = [
                    Faculty.objects.create(name='Alicaya, Erik', department=departments['Computer Science']),
                    Faculty.objects.create(name='Dulaca, Ryan', department=departments['Computer Science']),
                    Faculty.objects.create(name='Noel, Kyle', department=departments['Computer Science']),
                    Faculty.objects.create(name='Roldan, Jace', department=departments['Computer Science']),
                    Faculty.objects.create(name='Tan, Darmae', department=departments['Computer Science']),
                    Faculty.objects.create(name='Dr. Santos', department=departments['Biology']),
                    Faculty.objects.create(name='Prof. Garcia', department=departments['Mathematics']),
                    Faculty.objects.create(name='Dr. Lee', department=departments['Statistics']),
                ]
                
                # Create class sections
                self.stdout.write('Creating class sections...')
                sections = [
                    # CMSC 126 sections
                    ClassSection.objects.create(
                        course=courses['CMSC 126'],
                        section='A',
                        type='Lecture',
                        room='SCI 405',
                        schedule='M TH | 11:00 AM - 12:00 PM',
                        faculty=faculty[0]  # Alicaya, Erik
                    ),
                    ClassSection.objects.create(
                        course=courses['CMSC 126'],
                        section='A1',
                        type='Laboratory',
                        room='SCI 402',
                        schedule='TH | 3:00 PM - 6:00 PM',
                        faculty=faculty[0]  # Alicaya, Erik
                    ),
                    ClassSection.objects.create(
                        course=courses['CMSC 126'],
                        section='A2',
                        type='Laboratory',
                        room='SCI 402',
                        schedule='M | 3:00 PM - 6:00 PM',
                        faculty=faculty[1]  # Dulaca, Ryan
                    ),
                    
                    # CMSC 129 sections
                    ClassSection.objects.create(
                        course=courses['CMSC 129'],
                        section='A',
                        type='Lecture',
                        room='SCI 405',
                        schedule='M TH | 9:00 AM - 10:00 AM',
                        faculty=faculty[2]  # Noel, Kyle
                    ),
                    ClassSection.objects.create(
                        course=courses['CMSC 129'],
                        section='A1',
                        type='Laboratory',
                        room='SCI 404',
                        schedule='T | 9:00 AM - 12:00 PM',
                        faculty=faculty[3]  # Roldan, Jace
                    ),
                    ClassSection.objects.create(
                        course=courses['CMSC 129'],
                        section='A2',
                        type='Laboratory',
                        room='SCI 404',
                        schedule='F | 9:00 AM - 12:00 PM',
                        faculty=faculty[4]  # Tan, Darmae
                    ),
                    
                    # Other courses
                    ClassSection.objects.create(
                        course=courses['MATH 101'],
                        section='A',
                        type='Lecture',
                        room='SCI 305',
                        schedule='T F | 1:00 PM - 2:00 PM',
                        faculty=faculty[6]  # Prof. Garcia
                    ),
                    ClassSection.objects.create(
                        course=courses['STAT 101'],
                        section='A',
                        type='Lecture',
                        room='SCI 205',
                        schedule='W | 10:00 AM - 12:00 PM',
                        faculty=faculty[7]  # Dr. Lee
                    ),
                    ClassSection.objects.create(
                        course=courses['BIO 101'],
                        section='A',
                        type='Lecture',
                        room='SCI 105',
                        schedule='M W | 2:00 PM - 3:00 PM',
                        faculty=faculty[5]  # Dr. Santos
                    ),
                ]
                
                # Create admin users
                self.stdout.write('Creating admin users...')
                admin_users = [
                    AdminUser.objects.create(
                        name='Jennie Kim',
                        email='jennierubyjanet@gmail.com',
                        user_id='jen123',
                        password='rubyjane1@'
                    ),
                    AdminUser.objects.create(
                        name='Lalisa Manoban',
                        email='lalalisa@gmail.com',
                        user_id='lalisa0327',
                        password='lalaLisa2703'
                    ),
                    AdminUser.objects.create(
                        name='Rose Park',
                        email='rosie@gmail.com',
                        user_id='aptrose1@',
                        password='apateupateuRSP'
                    ),
                    AdminUser.objects.create(
                        name='Jisoo Kim',
                        email='sooya@gmail.com',
                        user_id='sooya143',
                        password='hellojisoopp4'
                    ),
                ]
                
                self.stdout.write(self.style.SUCCESS('Successfully created test data!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to create test data: {e}')) 