from rest_framework import serializers
from .models import MedicalVisit, AudioRecording, MedicalNote, AIGeneratedSummary, Prescription
from patients.serializers import PatientSearchSerializer
from accounts.serializers import UserSerializer


class AudioRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioRecording
        fields = '__all__'
        read_only_fields = ['id', 'visit', 'processing_status', 'transcript', 'transcript_confidence', 'processed_at']


class MedicalNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = MedicalNote
        fields = '__all__'
        read_only_fields = ['id', 'visit', 'created_by', 'created_at', 'updated_at']


class AIGeneratedSummarySerializer(serializers.ModelSerializer):
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    
    class Meta:
        model = AIGeneratedSummary
        fields = '__all__'
        read_only_fields = ['id', 'patient', 'visit', 'generated_at']


class PrescriptionSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    
    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['id', 'visit', 'patient', 'doctor', 'issued_at']


class MedicalVisitSerializer(serializers.ModelSerializer):
    patient_info = PatientSearchSerializer(source='patient', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    audio_recordings = AudioRecordingSerializer(many=True, read_only=True)
    medical_notes = MedicalNoteSerializer(many=True, read_only=True)
    ai_summaries = AIGeneratedSummarySerializer(many=True, read_only=True)
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = MedicalVisit
        fields = '__all__'
        read_only_fields = ['id', 'doctor', 'visit_date', 'updated_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['doctor'] = request.user
        return super().create(validated_data)


class MedicalVisitListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    patient_mrn = serializers.CharField(source='patient.mrn', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    
    class Meta:
        model = MedicalVisit
        fields = ['id', 'patient_name', 'patient_mrn', 'doctor_name', 'visit_type', 'status', 'chief_complaint', 'visit_date']


class PatientMedicalHistorySerializer(serializers.Serializer):
    patient = PatientSearchSerializer()
    visits = MedicalVisitListSerializer(many=True)
    total_visits = serializers.IntegerField()
    latest_visit = serializers.DateTimeField()
    ai_summary = AIGeneratedSummarySerializer(required=False)