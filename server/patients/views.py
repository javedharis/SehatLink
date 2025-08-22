from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import Patient, PatientFile, EmergencyContact
from .serializers import (
    PatientSerializer, PatientSearchSerializer, PatientCreateSerializer,
    PatientFileSerializer, EmergencyContactSerializer
)


class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PatientCreateSerializer
        return PatientSearchSerializer
    
    def get_queryset(self):
        queryset = Patient.objects.all()
        phone = self.request.query_params.get('phone', None)
        mrn = self.request.query_params.get('mrn', None)
        search = self.request.query_params.get('search', None)
        
        if phone:
            queryset = queryset.filter(phone_number=phone)
        elif mrn:
            queryset = queryset.filter(mrn=mrn)
        elif search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(mrn__icontains=search) |
                Q(cnic__icontains=search)
            )
        
        return queryset


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'mrn'


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_patients_by_phone(request, phone_number):
    try:
        patients = Patient.objects.filter(phone_number=phone_number)
        serializer = PatientSearchSerializer(patients, many=True)
        return Response({
            'count': patients.count(),
            'patients': serializer.data
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_patient_by_mrn(request, mrn):
    try:
        patient = Patient.objects.get(mrn=mrn)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    except Patient.DoesNotExist:
        return Response({
            'error': 'Patient not found'
        }, status=status.HTTP_404_NOT_FOUND)


class PatientFileListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_mrn = self.kwargs.get('patient_mrn')
        try:
            patient = Patient.objects.get(mrn=patient_mrn)
            return PatientFile.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            return PatientFile.objects.none()
    
    def perform_create(self, serializer):
        patient_mrn = self.kwargs.get('patient_mrn')
        patient = Patient.objects.get(mrn=patient_mrn)
        serializer.save(patient=patient, uploaded_by=self.request.user)


class PatientFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_mrn = self.kwargs.get('patient_mrn')
        try:
            patient = Patient.objects.get(mrn=patient_mrn)
            return PatientFile.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            return PatientFile.objects.none()


class EmergencyContactListCreateView(generics.ListCreateAPIView):
    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_mrn = self.kwargs.get('patient_mrn')
        try:
            patient = Patient.objects.get(mrn=patient_mrn)
            return EmergencyContact.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            return EmergencyContact.objects.none()
    
    def perform_create(self, serializer):
        patient_mrn = self.kwargs.get('patient_mrn')
        patient = Patient.objects.get(mrn=patient_mrn)
        serializer.save(patient=patient)


class EmergencyContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_mrn = self.kwargs.get('patient_mrn')
        try:
            patient = Patient.objects.get(mrn=patient_mrn)
            return EmergencyContact.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            return EmergencyContact.objects.none()