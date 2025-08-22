from django.urls import path
from . import views

urlpatterns = [
    # Transcription Services
    path('transcription/start/', views.start_transcription, name='start-transcription'),
    path('transcription/status/<uuid:job_id>/', views.get_transcription_status, name='transcription-status'),
    
    # Summary Generation Services
    path('summary/visit/', views.generate_visit_summary, name='generate-visit-summary'),
    path('summary/patient-history/', views.generate_patient_history_summary, name='generate-patient-history-summary'),
    path('summary/status/<uuid:job_id>/', views.get_summary_generation_status, name='summary-generation-status'),
    
    # AI Processing Statistics
    path('stats/', views.get_ai_processing_stats, name='ai-processing-stats'),
]