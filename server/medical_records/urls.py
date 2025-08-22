from django.urls import path
from . import views

urlpatterns = [
    # Medical Visits
    path('visits/', views.MedicalVisitListCreateView.as_view(), name='medical-visit-list-create'),
    path('visits/<uuid:pk>/', views.MedicalVisitDetailView.as_view(), name='medical-visit-detail'),
    
    # Patient Medical History
    path('history/<str:patient_mrn>/', views.patient_medical_history, name='patient-medical-history'),
    
    # Audio Recordings
    path('visits/<uuid:visit_id>/recordings/', views.AudioRecordingListCreateView.as_view(), name='audio-recording-list-create'),
    path('visits/<uuid:visit_id>/recordings/<uuid:pk>/', views.AudioRecordingDetailView.as_view(), name='audio-recording-detail'),
    
    # Medical Notes
    path('visits/<uuid:visit_id>/notes/', views.MedicalNoteListCreateView.as_view(), name='medical-note-list-create'),
    path('visits/<uuid:visit_id>/notes/<uuid:pk>/', views.MedicalNoteDetailView.as_view(), name='medical-note-detail'),
    
    # Prescriptions
    path('visits/<uuid:visit_id>/prescriptions/', views.PrescriptionListCreateView.as_view(), name='prescription-list-create'),
    path('visits/<uuid:visit_id>/prescriptions/<uuid:pk>/', views.PrescriptionDetailView.as_view(), name='prescription-detail'),
    
    # AI Generated Summaries
    path('summaries/<str:patient_mrn>/', views.AIGeneratedSummaryListView.as_view(), name='ai-summary-list'),
    path('summaries/<uuid:summary_id>/review/', views.mark_summary_reviewed, name='mark-summary-reviewed'),
]