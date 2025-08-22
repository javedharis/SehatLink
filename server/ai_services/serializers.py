from rest_framework import serializers
from .models import TranscriptionJob, SummaryGenerationJob


class TranscriptionJobSerializer(serializers.ModelSerializer):
    audio_recording_id = serializers.CharField(source='audio_recording.id', read_only=True)
    patient_name = serializers.CharField(source='audio_recording.visit.patient.get_full_name', read_only=True)
    patient_mrn = serializers.CharField(source='audio_recording.visit.patient.mrn', read_only=True)
    
    class Meta:
        model = TranscriptionJob
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'completed_at']


class SummaryGenerationJobSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    patient_mrn = serializers.CharField(source='patient.mrn', read_only=True)
    
    class Meta:
        model = SummaryGenerationJob
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'completed_at']