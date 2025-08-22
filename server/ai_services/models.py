from django.db import models
import uuid


class TranscriptionJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audio_recording = models.OneToOneField(
        'medical_records.AudioRecording',
        on_delete=models.CASCADE,
        related_name='transcription_job'
    )
    
    external_job_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    transcript_text = models.TextField(blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    
    processing_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transcription Job {self.id} - {self.status}"


class SummaryGenerationJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    SUMMARY_TYPE_CHOICES = [
        ('visit_summary', 'Visit Summary'),
        ('patient_history', 'Patient History Summary'),
        ('treatment_summary', 'Treatment Summary'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE)
    visit = models.ForeignKey('medical_records.MedicalVisit', on_delete=models.CASCADE, null=True, blank=True)
    
    summary_type = models.CharField(max_length=20, choices=SUMMARY_TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    input_data = models.JSONField(default=dict, help_text="Input data for AI processing")
    generated_summary = models.TextField(blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    
    ai_model_used = models.CharField(max_length=100, default='OpenAI GPT-4')
    processing_cost = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Summary Job {self.summary_type} - {self.patient.get_full_name()}"