from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .services import TranscriptionService, MedicalSummaryService
from .models import TranscriptionJob, SummaryGenerationJob
from .serializers import TranscriptionJobSerializer, SummaryGenerationJobSerializer
from medical_records.models import AudioRecording
from patients.models import Patient


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_transcription(request):
    """
    Start transcription for an audio recording
    """
    audio_recording_id = request.data.get('audio_recording_id')
    
    if not audio_recording_id:
        return Response({
            'error': 'audio_recording_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        audio_recording = AudioRecording.objects.get(id=audio_recording_id)
        
        # Check if transcription already exists
        if hasattr(audio_recording, 'transcription_job'):
            return Response({
                'message': 'Transcription already exists',
                'job': TranscriptionJobSerializer(audio_recording.transcription_job).data
            }, status=status.HTTP_200_OK)
        
        # Start transcription
        transcription_service = TranscriptionService()
        job = transcription_service.transcribe_audio(audio_recording_id)
        
        return Response({
            'message': 'Transcription started',
            'job': TranscriptionJobSerializer(job).data
        }, status=status.HTTP_201_CREATED)
        
    except AudioRecording.DoesNotExist:
        return Response({
            'error': 'Audio recording not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_transcription_status(request, job_id):
    """
    Get status of a transcription job
    """
    try:
        job = TranscriptionJob.objects.get(id=job_id)
        serializer = TranscriptionJobSerializer(job)
        return Response(serializer.data)
        
    except TranscriptionJob.DoesNotExist:
        return Response({
            'error': 'Transcription job not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_visit_summary(request):
    """
    Generate AI summary for a medical visit
    """
    visit_id = request.data.get('visit_id')
    
    if not visit_id:
        return Response({
            'error': 'visit_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        summary_service = MedicalSummaryService()
        ai_summary = summary_service.generate_visit_summary(visit_id)
        
        if ai_summary:
            return Response({
                'message': 'Visit summary generated successfully',
                'summary_id': str(ai_summary.id)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Failed to generate summary'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_patient_history_summary(request):
    """
    Generate AI summary for patient's medical history
    """
    patient_mrn = request.data.get('patient_mrn')
    
    if not patient_mrn:
        return Response({
            'error': 'patient_mrn is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        patient = Patient.objects.get(mrn=patient_mrn)
        
        summary_service = MedicalSummaryService()
        ai_summary = summary_service.generate_patient_history_summary(patient.id)
        
        if ai_summary:
            return Response({
                'message': 'Patient history summary generated successfully',
                'summary_id': str(ai_summary.id)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Failed to generate summary'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Patient.DoesNotExist:
        return Response({
            'error': 'Patient not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_summary_generation_status(request, job_id):
    """
    Get status of a summary generation job
    """
    try:
        job = SummaryGenerationJob.objects.get(id=job_id)
        serializer = SummaryGenerationJobSerializer(job)
        return Response(serializer.data)
        
    except SummaryGenerationJob.DoesNotExist:
        return Response({
            'error': 'Summary generation job not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_ai_processing_stats(request):
    """
    Get AI processing statistics
    """
    try:
        transcription_stats = {
            'total_jobs': TranscriptionJob.objects.count(),
            'completed': TranscriptionJob.objects.filter(status='completed').count(),
            'failed': TranscriptionJob.objects.filter(status='failed').count(),
            'processing': TranscriptionJob.objects.filter(status='processing').count(),
        }
        
        summary_stats = {
            'total_jobs': SummaryGenerationJob.objects.count(),
            'completed': SummaryGenerationJob.objects.filter(status='completed').count(),
            'failed': SummaryGenerationJob.objects.filter(status='failed').count(),
            'processing': SummaryGenerationJob.objects.filter(status='processing').count(),
        }
        
        return Response({
            'transcription': transcription_stats,
            'summary_generation': summary_stats
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)