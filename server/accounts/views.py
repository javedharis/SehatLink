from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User, OTP, HospitalProfile, DoctorProfile
from .serializers import (
    UserRegistrationSerializer, UserSerializer, PhoneLoginSerializer,
    OTPVerificationSerializer, HospitalProfileSerializer, DoctorProfileSerializer
)
from datetime import datetime, timedelta
import random
import string


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_otp(request):
    serializer = PhoneLoginSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        OTP.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=datetime.now() + timedelta(minutes=5)
        )
        
        return Response({
            'message': 'OTP sent successfully',
            'otp_code': otp_code  # Remove this in production
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
    serializer = OTPVerificationSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']
        
        try:
            otp = OTP.objects.get(
                phone_number=phone_number,
                otp_code=otp_code,
                is_used=False,
                expires_at__gte=datetime.now()
            )
            
            otp.is_used = True
            otp.save()
            
            user = User.objects.get(phone_number=phone_number)
            user.is_verified = True
            user.save()
            
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_200_OK)
            
        except OTP.DoesNotExist:
            return Response({
                'error': 'Invalid or expired OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def hospital_profile(request):
    if request.method == 'GET':
        try:
            profile = request.user.hospital_profile
            serializer = HospitalProfileSerializer(profile)
            return Response(serializer.data)
        except HospitalProfile.DoesNotExist:
            return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'POST':
        if request.user.user_type != 'hospital_staff':
            return Response({'error': 'Only hospital staff can create hospital profiles'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = HospitalProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        try:
            profile = request.user.hospital_profile
            serializer = HospitalProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except HospitalProfile.DoesNotExist:
            return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def doctor_profile(request):
    if request.method == 'GET':
        try:
            profile = request.user.doctor_profile
            serializer = DoctorProfileSerializer(profile)
            return Response(serializer.data)
        except DoctorProfile.DoesNotExist:
            return Response({'error': 'Doctor profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'POST':
        if request.user.user_type != 'doctor':
            return Response({'error': 'Only doctors can create doctor profiles'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = DoctorProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        try:
            profile = request.user.doctor_profile
            serializer = DoctorProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DoctorProfile.DoesNotExist:
            return Response({'error': 'Doctor profile not found'}, status=status.HTTP_404_NOT_FOUND)