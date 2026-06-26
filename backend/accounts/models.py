from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    name = models.CharField(max_length=100, blank=True)
    
    # Doctor specific fields
    certificate = models.FileField(upload_to='certificates/', null=True, blank=True)
    is_doctor_verified = models.BooleanField(default=False)

    # Patient specific fields
    assigned_doctor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'doctor'},
        related_name='my_patients'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"