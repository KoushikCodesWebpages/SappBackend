from django.contrib import admin
from django.urls import path
from backend.views.auth_views import SignUpView, LoginView,VerifyEmailView, PasswordResetConfirmView,PasswordResetRequestView, LogoutView
from backend.views.users_views import StudentsDbView, FacultyDbView, StandardListView,SectionListView, ProfileAPI, SubjectListView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/signup/', SignUpView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),  
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('api/password_reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    
    
    path('api/profile/', ProfileAPI.as_view(), name='profile'),
    #http://localhost:8000/api/login/
    #{
    #"email": "hariniwork@gmail.com",
    #"password": "your_password"
    #}
    path('api/profile/', ProfileAPI.as_view(), name='student_profile_api'),
    # Student profile API
    path('api/student-profile/', StudentsDbView.as_view(), name='student-profile-list'),
    path('api/student-profile/<int:index>/', StudentsDbView.as_view(), name='student-profile-detail'),

    # Faculty profile API
    path('api/faculty-profile/', FacultyDbView.as_view(), name='faculty-profile-list'),
    path('api/faculty-profile/<int:index>/', FacultyDbView.as_view(), name='faculty-profile-detail'),
    
    
    #Exposed APIs
    path('api/standards/', StandardListView.as_view(), name='standard-list'),
    path('api/sections/', SectionListView.as_view(), name='section-list'),
     path('subjects/', SubjectListView.as_view(), name='subject-list'),
]

# Serving media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
