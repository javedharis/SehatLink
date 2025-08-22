from django.contrib import admin
from .models import MedicalVisit, AudioRecording, MedicalNote, AIGeneratedSummary, Prescription


@admin.register(MedicalVisit)
class MedicalVisitAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'visit_type', 'status', 'visit_date']
    list_filter = ['visit_type', 'status', 'visit_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__mrn', 'doctor__username']
    readonly_fields = ['id', 'visit_date', 'updated_at']
    
    fieldsets = (
        ('Visit Information', {
            'fields': ('patient', 'doctor', 'visit_type', 'status', 'visit_date')
        }),
        ('Medical Details', {
            'fields': ('chief_complaint', 'symptoms', 'vital_signs', 'physical_examination', 'diagnosis')
        }),
        ('Treatment', {
            'fields': ('treatment_plan', 'medications_prescribed', 'follow_up_instructions', 'next_appointment')
        }),
        ('System Fields', {
            'fields': ('id', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AudioRecording)
class AudioRecordingAdmin(admin.ModelAdmin):
    list_display = ['visit', 'processing_status', 'duration_seconds', 'transcript_confidence', 'uploaded_at']
    list_filter = ['processing_status', 'uploaded_at']
    search_fields = ['visit__patient__first_name', 'visit__patient__last_name', 'visit__patient__mrn']
    readonly_fields = ['id', 'uploaded_at', 'processed_at']


@admin.register(MedicalNote)
class MedicalNoteAdmin(admin.ModelAdmin):
    list_display = ['visit', 'note_type', 'title', 'created_by', 'created_at']
    list_filter = ['note_type', 'created_at']
    search_fields = ['visit__patient__first_name', 'visit__patient__last_name', 'title', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AIGeneratedSummary)
class AIGeneratedSummaryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'summary_type', 'is_reviewed', 'confidence_score', 'generated_at']
    list_filter = ['summary_type', 'is_reviewed', 'generated_by_ai', 'generated_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__mrn', 'summary_content']
    readonly_fields = ['id', 'generated_at', 'reviewed_at']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'visit', 'issued_at', 'valid_until']
    list_filter = ['issued_at', 'valid_until']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__mrn', 'doctor__username']
    readonly_fields = ['id', 'issued_at']