from django.db import models
from django.conf import settings

class Report(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='performed_reports'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='medical_history', 
        null=True, 
        blank=True,
        db_index=True 
    )
    
    image = models.ImageField(upload_to='xrays/')
    lime_image = models.ImageField(upload_to='lime_results/', null=True, blank=True)
    
    result = models.CharField(max_length=100)
    confidence = models.FloatField(default=0.0)
    explanation = models.TextField(null=True, blank=True)
    
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        patient_name = self.patient.username if self.patient else "Anonymous"
        return f"Report for {patient_name} - {self.result}"