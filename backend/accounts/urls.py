from django.urls import path
from .views import register, login, patient_list, doctor_list

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('patients/', patient_list, name='patient_list'),
    path('doctors/', doctor_list, name='doctor_list'),
]