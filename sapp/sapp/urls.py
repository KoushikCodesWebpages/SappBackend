from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import ExcelUploadView, LoginView, StudentNavbarView,StudentProfileView,FacultyNavbarView,FacultyProfileView, FilterStudentsView

from features.views import AttendanceLockView,AttendanceDaysView, AttendanceView, AnnouncementView,AnnouncementMainDisplayView, CalendarEventView,TimetableView


urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Authentication
     path('upload-excel-signup/', ExcelUploadView.as_view(), name='upload-excel'),
     path('login/',LoginView.as_view(),name='login'),
     
    #profile
     path('student/navbar/',StudentNavbarView.as_view(),name='student-navbar'),
     path('student/profile/',StudentProfileView.as_view(),name='student-profile'),
     path('faculty/navbar/',FacultyNavbarView.as_view(),name='student-navbar'),
     path('faculty/profile/',FacultyProfileView.as_view(),name='faculty-profile'),
     path('student-profile/<str:student_code>/', StudentProfileView.as_view(), name='student-profile'),
     
     
    #default
    path('faculty/filter-students/', FilterStudentsView.as_view(), name ='filter-students'),
     
    #attendance
    path('office/attendancelock/', AttendanceLockView.as_view(),name='attendancelock'),
    path('office/attendancedays/', AttendanceDaysView.as_view(), name='attendance-days'),
    path('class/attendance/', AttendanceView.as_view(), name='attendance-list'),
    path('class/attendance/<str:student_code>/', AttendanceView.as_view(), name='attendance-detail'),
    
    #announcement
    path('office/announcementdisplay/',AnnouncementMainDisplayView.as_view(),name='announcement'),
    path('office/announcement/', AnnouncementView.as_view(),name='announcezment'),
    
    #calendar
    path('office/calendar/', CalendarEventView.as_view(),name='calendar'),
    path('office/calendar/<uuid:pk>/', CalendarEventView.as_view(),name='calendar_details'),
    
    #timetable
    path('office/timetables/', TimetableView.as_view(), name='timetables'),  # For list and create
    path('office/timetables/<uuid:pk>/', TimetableView.as_view(), name='timetable-detail'),  # For retrieve, update, and delete
]
# Serving media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
