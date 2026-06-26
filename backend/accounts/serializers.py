from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    certificate = serializers.FileField(required=False, allow_null=True)
    
    # This provides the dropdown data: Only shows doctors ALREADY verified by Admin
    assigned_doctor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='doctor', is_doctor_verified=True),
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role', 'name', 'certificate', 'assigned_doctor']

    def validate(self, data):
        role = data.get('role')
        if role == 'doctor' and not data.get('certificate'):
            raise serializers.ValidationError({"certificate": "Doctors must upload a certificate."})
        if role == 'patient' and not data.get('assigned_doctor'):
            raise serializers.ValidationError({"assigned_doctor": "Patients must select a verified doctor."})
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role')
        certificate = validated_data.pop('certificate', None)
        assigned_doctor = validated_data.pop('assigned_doctor', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            password=password,
            email=validated_data.get('email', ''),
            role=role,
            name=validated_data.get('name', '')
        )

        if role == 'doctor':
            user.certificate = certificate
            user.is_doctor_verified = False # Admin must approve
        elif role == 'patient':
            user.assigned_doctor = assigned_doctor
            
        user.save()
        return user