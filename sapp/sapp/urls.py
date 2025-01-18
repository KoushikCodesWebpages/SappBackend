from accounts.views import StudentSignupView,FacultySignupView, StudentLoginView, FacultyLoginView
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Authentication
    path('student/signup/', StudentSignupView.as_view(), name='student_signup'),
    path('student/login/', StudentLoginView.as_view(), name='student_login'),
    path('faculty/signup/', FacultySignupView.as_view(), name='faculty_signup'),
    path('faculty/login/', FacultyLoginView.as_view(), name='faculty_login'),
]

# Serving media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
