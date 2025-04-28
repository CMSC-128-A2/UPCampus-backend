from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from .models import Course, ClassSection
from .serializers import (
    CourseSerializer,
    CourseDetailSerializer,
    ClassSectionSerializer,
    ClassSectionCreateSerializer
)

class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing courses and their sections
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    @action(detail=True, methods=['delete'], url_path='sections/(?P<section_name>[^/.]+)')
    def delete_section(self, request, pk=None, section_name=None):
        """Delete a section from a course"""
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

class ClassSectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing class sections
    """
    queryset = ClassSection.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ClassSectionCreateSerializer
        return ClassSectionSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            course_code = request.data.get('course_code')
            section = request.data.get('section')
            return Response(
                {"detail": f"Section {section} already exists for {course_code}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_update(serializer)
            return Response(serializer.data)
        except IntegrityError:
            course_code = request.data.get('course_code')
            section = request.data.get('section')
            return Response(
                {"detail": f"Section {section} already exists for {course_code}"},
                status=status.HTTP_400_BAD_REQUEST
            )
