from django.db import models
from django.conf import settings
from patients.models import Patient
import uuid


class MedicalVisit(models.Model):
    VISIT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow Up'),
        ('emergency', 'Emergency'),
        ('routine_check', 'Routine Check'),
        ('surgery', 'Surgery'),
        ('diagnostic', 'Diagnostic'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_visits')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conducted_visits')
    
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    
    chief_complaint = models.TextField(help_text="Patient's main concern or reason for visit")
    symptoms = models.TextField(blank=True, help_text="Patient reported symptoms")
    
    vital_signs = models.JSONField(default=dict, blank=True, help_text="Blood pressure, temperature, pulse, etc.")
    
    physical_examination = models.TextField(blank=True, help_text="Doctor's physical examination findings")
    diagnosis = models.TextField(blank=True, help_text="Medical diagnosis")
    treatment_plan = models.TextField(blank=True, help_text="Recommended treatment plan")
    medications_prescribed = models.TextField(blank=True, help_text="Prescribed medications")
    
    follow_up_instructions = models.TextField(blank=True, help_text="Follow-up care instructions")
    next_appointment = models.DateTimeField(null=True, blank=True)
    
    visit_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date']
        indexes = [
            models.Index(fields=['patient', '-visit_date']),
            models.Index(fields=['doctor', '-visit_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.visit_type} - {self.visit_date.date()}"


class AudioRecording(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('transcribed', 'Transcribed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visit = models.ForeignKey(MedicalVisit, on_delete=models.CASCADE, related_name='audio_recordings')
    
    audio_file = models.FileField(upload_to='audio_recordings/', null=True, blank=True)
    audio_url = models.URLField(blank=True)  # For S3 URLs
    
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")
    
    transcript = models.TextField(blank=True, help_text="Auto-generated transcript")
    transcript_confidence = models.FloatField(null=True, blank=True, help_text="Confidence score 0-1")
    
    processing_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='uploaded')
    processing_error = models.TextField(blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Recording for {self.visit.patient.get_full_name()} - {self.visit.visit_date.date()}"


class MedicalNote(models.Model):
    NOTE_TYPE_CHOICES = [
        ('progress', 'Progress Note'),
        ('assessment', 'Assessment'),
        ('plan', 'Treatment Plan'),
        ('procedure', 'Procedure Note'),
        ('discharge', 'Discharge Summary'),
        ('referral', 'Referral'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visit = models.ForeignKey(MedicalVisit, on_delete=models.CASCADE, related_name='medical_notes')
    note_type = models.CharField(max_length=15, choices=NOTE_TYPE_CHOICES)
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    
    image = models.ImageField(upload_to='medical_notes/', null=True, blank=True)
    image_url = models.URLField(blank=True)  # For S3 URLs
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.visit.patient.get_full_name()}"


class AIGeneratedSummary(models.Model):
    SUMMARY_TYPE_CHOICES = [
        ('visit_summary', 'Visit Summary'),
        ('patient_history', 'Patient History Summary'),
        ('treatment_summary', 'Treatment Summary'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='ai_summaries')
    visit = models.ForeignKey(MedicalVisit, on_delete=models.CASCADE, related_name='ai_summaries', null=True, blank=True)
    
    summary_type = models.CharField(max_length=20, choices=SUMMARY_TYPE_CHOICES)
    summary_content = models.TextField()
    
    source_data = models.JSONField(default=dict, help_text="References to source data used for summary")
    confidence_score = models.FloatField(null=True, blank=True, help_text="AI confidence score 0-1")
    
    generated_by_ai = models.CharField(max_length=100, default='OpenAI GPT-4')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['patient', '-generated_at']),
            models.Index(fields=['summary_type']),
        ]
    
    def __str__(self):
        return f"{self.summary_type} for {self.patient.get_full_name()}"


class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visit = models.ForeignKey(MedicalVisit, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='issued_prescriptions')
    
    medications = models.JSONField(default=list, help_text="List of prescribed medications with details")
    instructions = models.TextField(help_text="General prescription instructions")
    
    issued_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"Prescription for {self.patient.get_full_name()} - {self.issued_at.date()}"