from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('hospital_staff', 'Hospital Staff'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    phone_number = PhoneNumberField(unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'user_type']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.phone_number})"


class OTP(models.Model):
    phone_number = PhoneNumberField()
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.phone_number}"


class HospitalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    hospital_name = models.CharField(max_length=255)
    hospital_address = models.TextField()
    license_number = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=255)
    department = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.hospital_name}"


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    medical_license = models.CharField(max_length=100, unique=True)
    specialization = models.CharField(max_length=255)
    years_of_experience = models.PositiveIntegerField()
    qualification = models.TextField()
    hospital_affiliation = models.CharField(max_length=255)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"