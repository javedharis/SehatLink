from django.urls import path
from . import views

urlpatterns = [
    path('', views.PatientListCreateView.as_view(), name='patient-list-create'),
    path('<str:mrn>/', views.PatientDetailView.as_view(), name='patient-detail'),
    path('search/phone/<str:phone_number>/', views.search_patients_by_phone, name='search-patients-by-phone'),
    path('search/mrn/<str:mrn>/', views.get_patient_by_mrn, name='get-patient-by-mrn'),
    
    path('<str:patient_mrn>/files/', views.PatientFileListCreateView.as_view(), name='patient-files'),
    path('<str:patient_mrn>/files/<uuid:pk>/', views.PatientFileDetailView.as_view(), name='patient-file-detail'),
    
    path('<str:patient_mrn>/emergency-contacts/', views.EmergencyContactListCreateView.as_view(), name='emergency-contacts'),
    path('<str:patient_mrn>/emergency-contacts/<int:pk>/', views.EmergencyContactDetailView.as_view(), name='emergency-contact-detail'),
]