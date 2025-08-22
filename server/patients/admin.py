from django.contrib import admin
from .models import Patient, PatientFile, EmergencyContact


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['mrn', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'created_at']
    list_filter = ['gender', 'blood_group', 'created_at']
    search_fields = ['mrn', 'first_name', 'last_name', 'phone_number', 'cnic']
    readonly_fields = ['id', 'mrn', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('mrn', 'first_name', 'last_name', 'date_of_birth', 'gender', 'phone_number', 'emergency_contact', 'cnic')
        }),
        ('Address', {
            'fields': ('address', 'city')
        }),
        ('Medical Information', {
            'fields': ('blood_group', 'allergies', 'chronic_conditions', 'current_medications')
        }),
        ('System Fields', {
            'fields': ('id', 'user', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PatientFile)
class PatientFileAdmin(admin.ModelAdmin):
    list_display = ['patient', 'title', 'file_type', 'uploaded_by', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__mrn', 'title']
    readonly_fields = ['id', 'uploaded_at']


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['patient', 'name', 'relationship', 'phone_number', 'is_primary']
    list_filter = ['relationship', 'is_primary']
    search_fields = ['patient__first_name', 'patient__last_name', 'name', 'phone_number']