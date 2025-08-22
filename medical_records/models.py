from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient
from hospitals.models import DoctorProfile

User = get_user_model()

class MedicalRecord(models.Model):
    VISIT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('emergency', 'Emergency'),
        ('follow_up', 'Follow-up'),
        ('routine_checkup', 'Routine Checkup'),
        ('diagnostic', 'Diagnostic'),
        ('surgery', 'Surgery'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='medical_records')
    visit_date = models.DateTimeField()
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES)
    chief_complaint = models.TextField()
    symptoms = models.TextField()
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    medications_prescribed = models.TextField(blank=True, null=True)
    follow_up_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    ai_summary = models.TextField(blank=True, null=True, help_text="AI-generated summary")
    is_discharged = models.BooleanField(default=False)
    discharge_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.patient_id} - {self.visit_date.strftime('%Y-%m-%d')}"

class VitalSigns(models.Model):
    medical_record = models.OneToOneField(MedicalRecord, on_delete=models.CASCADE, related_name='vital_signs')
    blood_pressure_systolic = models.PositiveIntegerField(blank=True, null=True)
    blood_pressure_diastolic = models.PositiveIntegerField(blank=True, null=True)
    heart_rate = models.PositiveIntegerField(blank=True, null=True, help_text="beats per minute")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, help_text="Celsius")
    respiratory_rate = models.PositiveIntegerField(blank=True, null=True, help_text="breaths per minute")
    oxygen_saturation = models.PositiveIntegerField(blank=True, null=True, help_text="percentage")
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="kg")
    bmi = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.height and self.weight:
            height_m = self.height / 100
            self.bmi = self.weight / (height_m * height_m)
        super().save(*args, **kwargs)

class LabTest(models.Model):
    TEST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='lab_tests')
    test_name = models.CharField(max_length=200)
    test_type = models.CharField(max_length=100)
    ordered_by = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    ordered_date = models.DateTimeField(auto_now_add=True)
    sample_collected_date = models.DateTimeField(blank=True, null=True)
    result_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=TEST_STATUS_CHOICES, default='pending')
    results = models.TextField(blank=True, null=True)
    normal_range = models.CharField(max_length=100, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    is_abnormal = models.BooleanField(default=False)
    report_file = models.FileField(upload_to='lab_reports/', blank=True, null=True)

    def __str__(self):
        return f"{self.test_name} - {self.medical_record.patient.patient_id}"

class Prescription(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100, help_text="e.g., Once daily, Twice daily")
    duration = models.CharField(max_length=100, help_text="e.g., 7 days, 2 weeks")
    instructions = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField()
    refills = models.PositiveIntegerField(default=0)
    prescribed_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.medication_name} - {self.medical_record.patient.patient_id}"

class MedicalDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('xray', 'X-Ray'),
        ('ct_scan', 'CT Scan'),
        ('mri', 'MRI'),
        ('ultrasound', 'Ultrasound'),
        ('ecg', 'ECG'),
        ('lab_report', 'Lab Report'),
        ('prescription', 'Prescription'),
        ('discharge_summary', 'Discharge Summary'),
        ('other', 'Other'),
    ]
    
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='medical_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.medical_record.patient.patient_id}"