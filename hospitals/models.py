from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    license_number = models.CharField(max_length=100, unique=True)
    established_date = models.DateField()
    total_beds = models.PositiveIntegerField()
    available_beds = models.PositiveIntegerField()
    specializations = models.TextField(help_text="Comma-separated list of specializations")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    head_doctor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'user_type': 'doctor'}
    )
    location = models.CharField(max_length=100, blank=True, null=True)
    phone_extension = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return f"{self.hospital.name} - {self.name}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'doctor'}
    )
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='doctors')
    medical_license = models.CharField(max_length=100, unique=True)
    specialization = models.CharField(max_length=100)
    years_of_experience = models.PositiveIntegerField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    qualification = models.TextField()
    available_days = models.CharField(
        max_length=50,
        help_text="Comma-separated days (e.g., Monday,Tuesday,Wednesday)"
    )
    available_time_start = models.TimeField()
    available_time_end = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"