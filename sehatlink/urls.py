from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/hospitals/', include('hospitals.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/medical-records/', include('medical_records.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/ai/', include('ai_services.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)