from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import ExcelUploadView, LoginView, StudentNavbarView,StudentProfileView,FacultyNavbarView,FacultyProfileView


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
     path('student-profile/<str:student_code>/', StudentProfileView.as_view(), name='student-profile')
]

# Serving media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
