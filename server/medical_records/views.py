from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Max
from django.utils import timezone
from patients.models import Patient
from .models import MedicalVisit, AudioRecording, MedicalNote, AIGeneratedSummary, Prescription
from .serializers import (
    MedicalVisitSerializer, MedicalVisitListSerializer, AudioRecordingSerializer,
    MedicalNoteSerializer, AIGeneratedSummarySerializer, PrescriptionSerializer,
    PatientMedicalHistorySerializer
)


class MedicalVisitListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MedicalVisitSerializer
        return MedicalVisitListSerializer
    
    def get_queryset(self):
        queryset = MedicalVisit.objects.select_related('patient', 'doctor')
        
        patient_mrn = self.request.query_params.get('patient_mrn')
        doctor_id = self.request.query_params.get('doctor_id')
        status_filter = self.request.query_params.get('status')
        visit_type = self.request.query_params.get('visit_type')
        
        if patient_mrn:
            queryset = queryset.filter(patient__mrn=patient_mrn)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if visit_type:
            queryset = queryset.filter(visit_type=visit_type)
        
        return queryset


class MedicalVisitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MedicalVisit.objects.all()
    serializer_class = MedicalVisitSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def patient_medical_history(request, patient_mrn):
    try:
        patient = Patient.objects.get(mrn=patient_mrn)
        visits = MedicalVisit.objects.filter(patient=patient).order_by('-visit_date')
        
        # Get patient AI summary if exists
        ai_summary = AIGeneratedSummary.objects.filter(
            patient=patient,
            summary_type='patient_history'
        ).first()
        
        history_data = {
            'patient': patient,
            'visits': visits,
            'total_visits': visits.count(),
            'latest_visit': visits.first().visit_date if visits.exists() else None,
        }
        
        if ai_summary:
            history_data['ai_summary'] = ai_summary
        
        serializer = PatientMedicalHistorySerializer(history_data)
        return Response(serializer.data)
        
    except Patient.DoesNotExist:
        return Response({
            'error': 'Patient not found'
        }, status=status.HTTP_404_NOT_FOUND)


class AudioRecordingListCreateView(generics.ListCreateAPIView):
    serializer_class = AudioRecordingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        visit_id = self.kwargs.get('visit_id')
        return AudioRecording.objects.filter(visit_id=visit_id)
    
    def perform_create(self, serializer):
        visit_id = self.kwargs.get('visit_id')
        visit = MedicalVisit.objects.get(id=visit_id)
        serializer.save(visit=visit)


class AudioRecordingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AudioRecordingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        visit_id = self.kwargs.get('visit_id')
        return AudioRecording.objects.filter(visit_id=visit_id)


class MedicalNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = MedicalNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        visit_id = self.kwargs.get('visit_id')
        return MedicalNote.objects.filter(visit_id=visit_id)
    
    def perform_create(self, serializer):
        visit_id = self.kwargs.get('visit_id')
        visit = MedicalVisit.objects.get(id=visit_id)
        serializer.save(visit=visit, created_by=self.request.user)


class MedicalNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MedicalNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        visit_id = self.kwargs.get('visit_id')
        return MedicalNote.objects.filter(visit_id=visit_id)


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        visit_id = self.kwargs.get('visit_id')
        return Prescription.objects.filter(visit_id=visit_id)
    
    def perform_create(self, serializer):
        visit_id = self.kwargs.get('visit_id')
        visit = MedicalVisit.objects.get(id=visit_id)
        serializer.save(visit=visit, patient=visit.patient, doctor=self.request.user)


class PrescriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        visit_id = self.kwargs.get('visit_id')
        return Prescription.objects.filter(visit_id=visit_id)


class AIGeneratedSummaryListView(generics.ListAPIView):
    serializer_class = AIGeneratedSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_mrn = self.kwargs.get('patient_mrn')
        summary_type = self.request.query_params.get('type')
        
        queryset = AIGeneratedSummary.objects.filter(patient__mrn=patient_mrn)
        
        if summary_type:
            queryset = queryset.filter(summary_type=summary_type)
        
        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_summary_reviewed(request, summary_id):
    try:
        summary = AIGeneratedSummary.objects.get(id=summary_id)
        summary.is_reviewed = True
        summary.reviewed_by = request.user
        summary.reviewed_at = timezone.now()
        summary.save()
        
        serializer = AIGeneratedSummarySerializer(summary)
        return Response(serializer.data)
        
    except AIGeneratedSummary.DoesNotExist:
        return Response({
            'error': 'Summary not found'
        }, status=status.HTTP_404_NOT_FOUND)