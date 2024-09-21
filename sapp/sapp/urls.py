"""
URL configuration for sapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from backend.views import SignUp,Login,StudentsProfileView,FacultyProfileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/',Login.as_view(),name='login'),
    
    #http://localhost:8000/api/login/
    #{
    #"email": "hariniwork@gmail.com",
    #"password": "your_password"
    #}

    path('api/signup/',SignUp.as_view(),name='signup'),
    
    path('student-profile/', StudentsProfileView.as_view(), name='student-profile-list'),
    path('student-profile/<int:index>/', StudentsProfileView.as_view(), name='student-profile-detail'),

    path('faculty-profile/', FacultyProfileView.as_view(), name='faculty-profile-list'),
    path('faculty-profile/<int:index>/', FacultyProfileView.as_view(), name='faculty-profile-detail'),
]
