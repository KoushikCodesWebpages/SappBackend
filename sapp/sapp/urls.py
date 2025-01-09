from accounts.views import SignUpView, LoginView,VerifyEmailView, PasswordResetConfirmView,PasswordResetRequestView, LogoutView
from students.views import StudentsDbView
from faculties.views import FacultyDbView
from exposed.views import StandardView,SectionView, SubjectView
from features.views import ProfileView, AssignmentView, ResultView, ReportView, FeeView, AttendanceView, TimetableView, CalendarEventView


from django.contrib import admin
from django.urls import path
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
    #http://localhost:8000/api/login/
    #{
    #"email": "hariniwork@gmail.com",
    #"password": "your_password"
    #}
    # Studentdb API
    path('api/student-db/', StudentsDbView.as_view(), name='student-list'),
    path('api/student-db/<int:index>/', StudentsDbView.as_view(), name='student-detail'),

    # Facultydb API
    path('api/faculty-db/', FacultyDbView.as_view(), name='faculty-list'),
    path('api/faculty-db/<int:index>/', FacultyDbView.as_view(), name='faculty-detail'),
    
    #Profile api
    
    path('api/profile/', ProfileView.as_view(), name='profile'),
    
    path('assignments/', AssignmentView.as_view(), name='assignments'),
    path('results/', ResultView.as_view(), name='results'),
    path('reports/', ReportView.as_view(), name='reports'),
    path('fees/', FeeView.as_view(), name='fees'),
    path('attendance/', AttendanceView.as_view(), name='attendance'),
    path('timetable/', TimetableView.as_view(), name='timetable'),
    path('calendar/', CalendarEventView.as_view(), name='calendar'),  
      
      
      
      
      
      
    #Exposed APIs
    # Subject URLs
    path('api/subjects/', SubjectView.as_view(), name='subject-list-create'),  # Handle GET and POST
    path('api/subjects/<int:index>/', SubjectView.as_view(), name='subject-detail'),  # Handle GET, PUT (update), and DELETE

    # Standard URLs
    path('api/standards/', StandardView.as_view(), name='standard-list-create'),  # Handle GET and POST
    path('api/standards/<int:index>/', StandardView.as_view(), name='standard-detail'),  # Handle GET, PUT (update), and DELETE

    # Section URLs
    path('api/sections/', SectionView.as_view(), name='section-list-create'),  # Handle GET and POST
    path('api/sections/<int:index>/', SectionView.as_view(), name='section-detail'),  # Handle GET, PUT (update), and DELETE
]

# Serving media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
