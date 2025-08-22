from django.contrib import admin
from .models import TranscriptionJob, SummaryGenerationJob


@admin.register(TranscriptionJob)
class TranscriptionJobAdmin(admin.ModelAdmin):
    list_display = ['audio_recording', 'status', 'confidence_score', 'processing_time_seconds', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at', 'completed_at']
    search_fields = ['audio_recording__visit__patient__first_name', 'audio_recording__visit__patient__last_name', 'external_job_id']
    readonly_fields = ['id', 'created_at', 'completed_at']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('audio_recording', 'external_job_id', 'status', 'created_at', 'completed_at')
        }),
        ('Results', {
            'fields': ('transcript_text', 'confidence_score', 'processing_time_seconds')
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SummaryGenerationJob)
class SummaryGenerationJobAdmin(admin.ModelAdmin):
    list_display = ['patient', 'summary_type', 'status', 'ai_model_used', 'processing_cost', 'created_at', 'completed_at']
    list_filter = ['summary_type', 'status', 'ai_model_used', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__mrn']
    readonly_fields = ['id', 'created_at', 'completed_at']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('patient', 'visit', 'summary_type', 'status', 'ai_model_used')
        }),
        ('Input Data', {
            'fields': ('input_data',),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('generated_summary', 'confidence_score', 'processing_cost')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )