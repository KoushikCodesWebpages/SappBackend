from django.contrib import admin
from django.urls import path
from backend.views import SignUp, Login, StudentsProfileView, FacultyProfileView, StandardListView,SectionListView, ProfileAPI
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/login/', Login.as_view(), name='login'),
    path('api/signup/', SignUp.as_view(), name='signup'),
    path('api/profile/', ProfileAPI.as_view(), name='student_profile_api'),
    #http://localhost:8000/api/login/
    #{
    #"email": "hariniwork@gmail.com",
    #"password": "your_password"
    #}
    # Student profile API
    path('api/student-profile/', StudentsProfileView.as_view(), name='student-profile-list'),
    path('api/student-profile/<int:index>/', StudentsProfileView.as_view(), name='student-profile-detail'),

    # Faculty profile API
    path('api/faculty-profile/', FacultyProfileView.as_view(), name='faculty-profile-list'),
    path('api/faculty-profile/<int:index>/', FacultyProfileView.as_view(), name='faculty-profile-detail'),
    
    
    #Exposed APIs
     path('api/standards/', StandardListView.as_view(), name='standard-list'),
       path('api/sections/', SectionListView.as_view(), name='section-list'),
]

# Serving media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
