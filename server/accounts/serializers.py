from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, HospitalProfile, DoctorProfile, OTP
import random
import string
from datetime import datetime, timedelta


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'user_type', 'password']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class HospitalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalProfile
        fields = '__all__'
        read_only_fields = ['user']


class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = '__all__'
        read_only_fields = ['user']


class UserSerializer(serializers.ModelSerializer):
    hospital_profile = HospitalProfileSerializer(read_only=True)
    doctor_profile = DoctorProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'user_type', 'is_verified', 'hospital_profile', 'doctor_profile']


class PhoneLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    
    def validate_phone_number(self, value):
        try:
            user = User.objects.get(phone_number=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this phone number.")


class OTPVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp_code = serializers.CharField(max_length=6)
    
    def validate(self, data):
        try:
            otp = OTP.objects.get(
                phone_number=data['phone_number'],
                otp_code=data['otp_code'],
                is_used=False,
                expires_at__gte=datetime.now()
            )
            return data
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired OTP.")