from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTP, HospitalProfile, DoctorProfile


class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'phone_number', 'user_type', 'is_verified', 'is_active']
    list_filter = ['user_type', 'is_verified', 'is_active']
    search_fields = ['username', 'phone_number', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'is_verified')
        }),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'otp_code', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['phone_number']
    readonly_fields = ['created_at']


@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'hospital_name', 'license_number', 'contact_person']
    search_fields = ['hospital_name', 'license_number', 'user__username']


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'medical_license', 'specialization', 'years_of_experience']
    search_fields = ['medical_license', 'specialization', 'user__username']


admin.site.register(User, UserAdmin)