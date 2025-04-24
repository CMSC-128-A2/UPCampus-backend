from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, ClassSectionViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'sections', ClassSectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('schedules/create/', ClassSectionViewSet.as_view({'post': 'create_schedule'}), name='create-schedule'),
] 