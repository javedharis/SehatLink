from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
import uuid
import random
import string


def generate_mrn():
    return ''.join(random.choices(string.digits, k=8))


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='patient_profile')
    mrn = models.CharField(max_length=20, unique=True, default=generate_mrn)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = PhoneNumberField()
    emergency_contact = PhoneNumberField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    cnic = models.CharField(max_length=15, unique=True)
    
    allergies = models.TextField(blank=True, help_text="Known allergies")
    chronic_conditions = models.TextField(blank=True, help_text="Chronic medical conditions")
    current_medications = models.TextField(blank=True, help_text="Current medications")
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_patients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['mrn']),
            models.Index(fields=['cnic']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.mrn}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class PatientFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('lab_report', 'Lab Report'),
        ('radiology', 'Radiology'),
        ('prescription', 'Prescription'),
        ('medical_note', 'Medical Note'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='files')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='patient_files/')
    file_url = models.URLField(blank=True)  # For S3 URLs
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.title}"


class EmergencyContact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('sibling', 'Sibling'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    phone_number = PhoneNumberField()
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_primary', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.patient.get_full_name()}"