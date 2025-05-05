from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, ClassSectionViewSet, DepartmentViewSet, FacultyViewSet, AdminUserViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'sections', ClassSectionViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'faculty', FacultyViewSet)
router.register(r'admins', AdminUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 