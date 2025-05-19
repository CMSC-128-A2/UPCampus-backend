from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, 
    ClassSectionViewSet, 
    DepartmentViewSet, 
    FacultyViewSet, 
    AdminUserViewSet,
    ScheduleConflictView,
    RoomSchedulesView,
    RoomsListView,
    RoomSchedulesByDayView,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'sections', ClassSectionViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'faculty', FacultyViewSet)
router.register(r'admins', AdminUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('conflicts/check/', ScheduleConflictView.as_view(), name='check-conflicts'),
    # Add to src/schedules/urls.py in the urlpatterns list
    path('rooms/<str:room>/schedules/', RoomSchedulesView.as_view(), name='room-schedules'),
    # Add to src/schedules/urls.py in the urlpatterns list
    path('rooms/', RoomsListView.as_view(), name='rooms-list'),
    # Add to src/schedules/urls.py in the urlpatterns list
    path('rooms/<str:room>/schedules-by-day/', RoomSchedulesByDayView.as_view(), name='room-schedules-by-day'),
] 