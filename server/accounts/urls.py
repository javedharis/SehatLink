from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('profile/', views.user_profile, name='user_profile'),
    path('hospital-profile/', views.hospital_profile, name='hospital_profile'),
    path('doctor-profile/', views.doctor_profile, name='doctor_profile'),
]