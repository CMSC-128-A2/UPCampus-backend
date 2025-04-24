from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Course, ClassSection
from .serializers import CourseSerializer, ClassSectionSerializer, ClassSectionCreateSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def get_queryset(self):
        """
        Optionally filters the courses by search query
        """
        queryset = Course.objects.all().prefetch_related('sections')
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(course_code__icontains=search_query)
            
        return queryset

class ClassSectionViewSet(viewsets.ModelViewSet):
    queryset = ClassSection.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'create_schedule':
            return ClassSectionCreateSerializer
        return ClassSectionSerializer
    
    @action(detail=False, methods=['post'])
    def create_schedule(self, request):
        """
        Custom endpoint for creating a schedule with course_code, section, type, room, day, and time
        """
        serializer = ClassSectionCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                class_section = serializer.save()
                # Return the full course with all sections
                course = class_section.course
                course_serializer = CourseSerializer(course)
                return Response(course_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to handle deleting courses with no sections
        """
        instance = self.get_object()
        course = instance.course
        self.perform_destroy(instance)
        
        # If this was the last section, delete the course too
        if not course.sections.exists():
            course.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        # Otherwise return the updated course
        course_serializer = CourseSerializer(course)
        return Response(course_serializer.data) 