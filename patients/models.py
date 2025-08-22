from django.db import models
from django.contrib.auth import get_user_model
from hospitals.models import Hospital

User = get_user_model()

class Patient(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'patient'}
    )
    patient_id = models.CharField(max_length=20, unique=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='patients')
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    emergency_contact_relation = models.CharField(max_length=50)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    insurance_number = models.CharField(max_length=100, blank=True, null=True)
    insurance_provider = models.CharField(max_length=100, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kg")
    allergies = models.TextField(blank=True, null=True, help_text="List of known allergies")
    chronic_conditions = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient_id} - {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last_patient = Patient.objects.all().order_by('id').last()
            if last_patient:
                patient_num = int(last_patient.patient_id.split('P')[1]) + 1
            else:
                patient_num = 1
            self.patient_id = f'P{patient_num:06d}'
        super().save(*args, **kwargs)