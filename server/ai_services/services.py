import openai
import assemblyai as aai
from django.conf import settings
from .models import TranscriptionJob, SummaryGenerationJob
from medical_records.models import AIGeneratedSummary, AudioRecording
from datetime import datetime
import json


class TranscriptionService:
    def __init__(self):
        aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
    
    def transcribe_audio(self, audio_recording_id):
        try:
            audio_recording = AudioRecording.objects.get(id=audio_recording_id)
            
            # Create transcription job
            job = TranscriptionJob.objects.create(
                audio_recording=audio_recording,
                status='processing'
            )
            
            # Configure transcription settings
            config = aai.TranscriptionConfig(
                speaker_labels=True,
                auto_punctuation=True,
                auto_highlights=True,
                language_detection=True,
            )
            
            # Submit transcription request
            transcriber = aai.Transcriber()
            
            # Use audio file URL or local path
            audio_url = audio_recording.audio_url or audio_recording.audio_file.url
            transcript = transcriber.transcribe(audio_url, config)
            
            if transcript.status == aai.TranscriptStatus.completed:
                job.status = 'completed'
                job.transcript_text = transcript.text
                job.confidence_score = transcript.confidence
                job.external_job_id = transcript.id
                job.completed_at = datetime.now()
                
                # Update audio recording
                audio_recording.transcript = transcript.text
                audio_recording.transcript_confidence = transcript.confidence
                audio_recording.processing_status = 'transcribed'
                audio_recording.processed_at = datetime.now()
                audio_recording.save()
                
            elif transcript.status == aai.TranscriptStatus.error:
                job.status = 'failed'
                job.error_message = transcript.error
                
                audio_recording.processing_status = 'failed'
                audio_recording.processing_error = transcript.error
                audio_recording.save()
            
            job.save()
            return job
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
            return job


class MedicalSummaryService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    def generate_visit_summary(self, visit_id):
        try:
            from medical_records.models import MedicalVisit
            visit = MedicalVisit.objects.get(id=visit_id)
            
            # Create summary generation job
            job = SummaryGenerationJob.objects.create(
                patient=visit.patient,
                visit=visit,
                summary_type='visit_summary',
                status='processing'
            )
            
            # Prepare input data
            input_data = {
                'patient_info': {
                    'name': visit.patient.get_full_name(),
                    'age': visit.patient.get_age(),
                    'gender': visit.patient.gender,
                    'mrn': visit.patient.mrn,
                },
                'visit_details': {
                    'visit_type': visit.visit_type,
                    'chief_complaint': visit.chief_complaint,
                    'symptoms': visit.symptoms,
                    'vital_signs': visit.vital_signs,
                    'physical_examination': visit.physical_examination,
                    'diagnosis': visit.diagnosis,
                    'treatment_plan': visit.treatment_plan,
                    'medications_prescribed': visit.medications_prescribed,
                },
                'transcripts': []
            }
            
            # Add audio transcripts if available
            for recording in visit.audio_recordings.filter(processing_status='transcribed'):
                input_data['transcripts'].append({
                    'transcript': recording.transcript,
                    'confidence': recording.transcript_confidence,
                })
            
            job.input_data = input_data
            job.save()
            
            # Generate summary using OpenAI
            prompt = self._create_visit_summary_prompt(input_data)
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical AI assistant that creates concise, accurate medical visit summaries for Electronic Health Records."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3,
            )
            
            summary_text = response.choices[0].message.content
            
            # Create AI Generated Summary
            ai_summary = AIGeneratedSummary.objects.create(
                patient=visit.patient,
                visit=visit,
                summary_type='visit_summary',
                summary_content=summary_text,
                source_data=input_data,
                generated_by_ai='OpenAI GPT-4'
            )
            
            # Update job
            job.status = 'completed'
            job.generated_summary = summary_text
            job.completed_at = datetime.now()
            job.processing_cost = self._calculate_openai_cost(response.usage)
            job.save()
            
            return ai_summary
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
            return None
    
    def generate_patient_history_summary(self, patient_id):
        try:
            from patients.models import Patient
            from medical_records.models import MedicalVisit
            
            patient = Patient.objects.get(id=patient_id)
            visits = MedicalVisit.objects.filter(patient=patient).order_by('-visit_date')[:10]
            
            # Create summary generation job
            job = SummaryGenerationJob.objects.create(
                patient=patient,
                summary_type='patient_history',
                status='processing'
            )
            
            # Prepare input data
            input_data = {
                'patient_info': {
                    'name': patient.get_full_name(),
                    'age': patient.get_age(),
                    'gender': patient.gender,
                    'mrn': patient.mrn,
                    'allergies': patient.allergies,
                    'chronic_conditions': patient.chronic_conditions,
                    'current_medications': patient.current_medications,
                },
                'recent_visits': []
            }
            
            for visit in visits:
                visit_data = {
                    'date': visit.visit_date.isoformat(),
                    'type': visit.visit_type,
                    'chief_complaint': visit.chief_complaint,
                    'diagnosis': visit.diagnosis,
                    'treatment': visit.treatment_plan,
                    'medications': visit.medications_prescribed,
                }
                input_data['recent_visits'].append(visit_data)
            
            job.input_data = input_data
            job.save()
            
            # Generate summary using OpenAI
            prompt = self._create_patient_history_prompt(input_data)
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical AI assistant that creates comprehensive patient medical history summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3,
            )
            
            summary_text = response.choices[0].message.content
            
            # Create AI Generated Summary
            ai_summary = AIGeneratedSummary.objects.create(
                patient=patient,
                summary_type='patient_history',
                summary_content=summary_text,
                source_data=input_data,
                generated_by_ai='OpenAI GPT-4'
            )
            
            # Update job
            job.status = 'completed'
            job.generated_summary = summary_text
            job.completed_at = datetime.now()
            job.processing_cost = self._calculate_openai_cost(response.usage)
            job.save()
            
            return ai_summary
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
            return None
    
    def _create_visit_summary_prompt(self, data):
        return f"""
        Create a concise medical visit summary based on the following information:
        
        Patient: {data['patient_info']['name']}, {data['patient_info']['age']} years old, {data['patient_info']['gender']}
        MRN: {data['patient_info']['mrn']}
        
        Visit Details:
        - Type: {data['visit_details']['visit_type']}
        - Chief Complaint: {data['visit_details']['chief_complaint']}
        - Symptoms: {data['visit_details']['symptoms']}
        - Vital Signs: {json.dumps(data['visit_details']['vital_signs'])}
        - Physical Examination: {data['visit_details']['physical_examination']}
        - Diagnosis: {data['visit_details']['diagnosis']}
        - Treatment Plan: {data['visit_details']['treatment_plan']}
        - Medications: {data['visit_details']['medications_prescribed']}
        
        Audio Transcripts: {json.dumps(data['transcripts'])}
        
        Please provide a structured medical summary with the following sections:
        1. Chief Complaint & History
        2. Physical Examination Findings
        3. Assessment/Diagnosis
        4. Treatment Plan
        5. Follow-up Instructions
        """
    
    def _create_patient_history_prompt(self, data):
        return f"""
        Create a comprehensive patient medical history summary based on the following information:
        
        Patient: {data['patient_info']['name']}, {data['patient_info']['age']} years old
        MRN: {data['patient_info']['mrn']}
        
        Known Allergies: {data['patient_info']['allergies']}
        Chronic Conditions: {data['patient_info']['chronic_conditions']}
        Current Medications: {data['patient_info']['current_medications']}
        
        Recent Medical Visits:
        {json.dumps(data['recent_visits'], indent=2)}
        
        Please provide a comprehensive summary with:
        1. Patient Demographics and Key Medical Information
        2. Chronic Conditions and Ongoing Care
        3. Recent Visit Trends and Patterns
        4. Current Treatment Status
        5. Recommendations for Ongoing Care
        """
    
    def _calculate_openai_cost(self, usage):
        # Approximate cost calculation (prices as of 2024)
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        
        # GPT-4 pricing (approximate)
        prompt_cost = prompt_tokens * 0.00003  # $0.03/1K tokens
        completion_cost = completion_tokens * 0.00006  # $0.06/1K tokens
        
        return prompt_cost + completion_cost