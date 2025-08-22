from rest_framework import serializers
from .models import Patient, PatientFile, EmergencyContact


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = '__all__'
        read_only_fields = ['patient']


class PatientFileSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = PatientFile
        fields = '__all__'
        read_only_fields = ['patient', 'uploaded_by', 'uploaded_at']


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(source='get_age', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    files = PatientFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'mrn', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class PatientSearchSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(source='get_age', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Patient
        fields = ['id', 'mrn', 'first_name', 'last_name', 'full_name', 'phone_number', 'date_of_birth', 'age', 'gender']


class PatientCreateSerializer(serializers.ModelSerializer):
    emergency_contacts = EmergencyContactSerializer(many=True, required=False)
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'mrn', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        emergency_contacts_data = validated_data.pop('emergency_contacts', [])
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        patient = Patient.objects.create(**validated_data)
        
        for contact_data in emergency_contacts_data:
            EmergencyContact.objects.create(patient=patient, **contact_data)
        
        return patient