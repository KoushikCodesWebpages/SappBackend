from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import ExcelUploadView, LoginView
urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Authentication
     path('upload-excel-signup/', ExcelUploadView.as_view(), name='upload-excel'),
     path('login/',LoginView.as_view(),name='login')
]

# Serving media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
