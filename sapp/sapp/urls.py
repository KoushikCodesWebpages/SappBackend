from django.contrib import admin 
from django.urls import path,  include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers
from accounts.views import ExcelUploadView, LoginView,StudentViewSet,FacultyViewSet,OfficeAdminViewSet

from features.veiws.profile import StudentProfileView, SOProfileView, FacultyProfileView
from features.veiws.attendance import AttendanceLockView,AttendanceDaysView, AttendanceView
from features.veiws.announcements import AnnouncementView,AnnouncementMainDisplayView
from features.veiws.calendar import CalendarEventView
from features.veiws.assignments import AssignmentView
from features.veiws.submissions import FacultySubmissionViewSet,StudentSubmissionViewSet
from features.veiws.timetable import TimetableView
from features.veiws.results import ResultLockView,ResultLockDetailView, StudentResultAPIView, FacultyResultView 
from features.veiws.portions import PortionViewSet
from features.veiws.defaults import AdminDashboardAPIView, FilterStudentsView



router = routers.DefaultRouter()
router.register('studentslist', StudentViewSet)
router.register('facultylist', FacultyViewSet)
router.register('soadminlist', OfficeAdminViewSet)

#submissions
router.register(r'student/submissions', StudentSubmissionViewSet, basename='student-submission')
router.register(r'faculty/submissions', FacultySubmissionViewSet, basename='faculty-submission')

#portions
router.register(r'portions', PortionViewSet, basename='portion')


urlpatterns = [
    # Admin panel
     path('admin/', admin.site.urls),
    
    # Authentication
     path('upload-excel-signup/', ExcelUploadView.as_view(), name='upload-excel'),
     path('login/',LoginView.as_view(),name='login'),
    
     path('', include(router.urls)), 
    
    #profile
     path('student/profile/',StudentProfileView.as_view(),name='student-profile'),
     path('student/profile/<str:student_code>/', StudentProfileView.as_view(), name='student-profile'),
     path('faculty/profile/',FacultyProfileView.as_view(),name='faculty-profile'),
     path('soadmin/profile/',SOProfileView.as_view(),name='soadmin-profile'),
     
     
    #default
     path("office/dashboard/", AdminDashboardAPIView.as_view(), name="dashboard-stats"),
     path('faculty/filter-students/', FilterStudentsView.as_view(), name ='filter-students'),
    
         
    #attendance
     path('office/attendancelock/', AttendanceLockView.as_view(),name='attendancelock'),
     path('office/attendancedays/', AttendanceDaysView.as_view(), name='attendance-days'),
     path('class/attendance/', AttendanceView.as_view(), name='attendance-list'),
     path('class/attendance/<str:student_code>/', AttendanceView.as_view(), name='attendance-detail'),
    
    #resultlock
     path('office/resultlock/', ResultLockView.as_view(), name='result-lock-list'),
     path('office/resultlock/<int:pk>/', ResultLockDetailView.as_view(), name='result-lock-detail'),
    
    #results
    
     path("student/results/", StudentResultAPIView.as_view(), name="student-results"),

     path("faculty/results/", FacultyResultView.as_view(), name="faculty-results"),
     path("faculty/results/<int:pk>/", FacultyResultView.as_view(), name="faculty-result-detail"),

    
    #announcement
     path('office/announcementdisplay/',AnnouncementMainDisplayView.as_view(),name='announcement'),
     path('office/announcement/', AnnouncementView.as_view(),name='announcezment'),
    
    #calendar
     path('office/calendar/', CalendarEventView.as_view(),name='calendar'),
     path('office/calendar/<uuid:pk>/', CalendarEventView.as_view(),name='calendar_details'),
    
    #timetable
     path('office/timetables/', TimetableView.as_view(), name='timetables'),  # For list and create
     path('office/timetables/<uuid:pk>/', TimetableView.as_view(), name='timetable-detail'),  # For retrieve, update, and delete
    
    #assignments
     path('faculty/assignments/', AssignmentView.as_view(), name='assignment-list'),
     path('faculty/assignments/<uuid:assignment_id>/', AssignmentView.as_view(), name='assignment_delete'),
     
    #submissions
    #registered
    
    #portions
     
     
     
]
# Serving media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
