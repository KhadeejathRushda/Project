import os
import io
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

from .models import Report
from .ml_model import predict_diagnosis
from .lime_explainer import generate_lime_explanation

User = get_user_model()

# ================= UPLOAD & AI ANALYSIS =================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_xray(request):
    user = request.user
    if user.role != 'doctor':
        return Response({"error": "Only doctors can upload scans."}, status=403)

    image = request.FILES.get('image')
    patient_id = request.data.get('patient_id')

    if not image or not patient_id:
        return Response({"error": "Missing image or patient ID."}, status=400)

    patient = get_object_or_404(User, id=patient_id)
    report = Report.objects.create(doctor=user, patient=patient, image=image, result="Processing")

    try:
        # Run AI Prediction
        prediction, confidence = predict_diagnosis(report.image.path)
        
        # Setup LIME directory
        lime_filename = f"lime_{report.id}.png"
        lime_dir = os.path.join(settings.MEDIA_ROOT, 'lime_results')
        if not os.path.exists(lime_dir):
            os.makedirs(lime_dir)
            
        lime_path = os.path.join(lime_dir, lime_filename)
        
        # Generate LIME explanation
        generate_lime_explanation(report.image.path, lime_path)

        # Update report object
        report.result = prediction
        report.confidence = confidence * 100
        report.lime_image = f"lime_results/{lime_filename}"
        report.save()

        return Response({
            "id": report.id,
            "prediction": prediction,
            "confidence": round(report.confidence, 2),
            "lime_image": request.build_absolute_uri(report.lime_image.url)
        })
    except Exception as e:
        report.delete()
        return Response({"error": str(e)}, status=500)

# ================= VERIFICATION =================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_report(request, report_id):
    # Only the doctor who created the report can verify it
    report = get_object_or_404(Report, id=report_id, doctor=request.user)
    report.is_verified = True
    report.save()
    return Response({"message": "Report verified successfully."})

# ================= DOCTOR DASHBOARD =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        return Response({"error": "Unauthorized access."}, status=403)

    # Filter for only verified reports belonging to this doctor
    verified_reports = Report.objects.filter(doctor=request.user, is_verified=True)
    
    # Calculate counts based ONLY on verified data
    total_verified = verified_reports.count()
    
    # Unique patients who have at least one verified report
    unique_patients = verified_reports.values('patient').distinct().count()

    # Get 5 most recent verified activities
    recent = verified_reports.order_by('-created_at')[:5]
    
    recent_data = [{
        "id": r.id,
        "result": r.result,
        "confidence": round(r.confidence, 2) if r.confidence else 0,
        "patient_name": r.patient.name if r.patient.name else r.patient.username,
        "created_at": r.created_at.strftime("%Y-%m-%d %H:%M")
    } for r in recent]

    return Response({
        "total_verified_scans": total_verified,
        "unique_patients_count": unique_patients,
        "recent_activity": recent_data
    })

# ================= PATIENT REPORTS =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_reports(request, patient_id):
    # Security check: Patients can only see their own data
    if request.user.role == 'patient' and str(request.user.id) != str(patient_id):
        return Response({"error": "Access denied."}, status=403)

    reports = Report.objects.filter(patient_id=patient_id, is_verified=True).order_by('-created_at')
    data = [{
        "id": r.id,
        "result": r.result,
        "confidence": round(r.confidence, 2),
        "created_at": r.created_at.strftime("%Y-%m-%d"),
        "image": request.build_absolute_uri(r.image.url) if r.image else None
    } for r in reports]
    return Response(data)

# ================= PDF GENERATION =================
# ================= PDF GENERATION =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report_pdf(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    # Permission check: Only the involved doctor or patient can download
    if request.user != report.doctor and request.user != report.patient:
        return Response({"error": "You do not have permission to download this report."}, status=403)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 750, "LUNG DISEASE DIAGNOSTIC REPORT")
    p.line(100, 745, 500, 745)
    
    # Patient Info
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, f"Patient Name: {report.patient.name if report.patient.name else report.patient.username}")
    p.drawString(100, 705, f"Attending Doctor: Dr. {report.doctor.name if report.doctor.name else report.doctor.username}")
    p.drawString(100, 690, f"Date Generated: {report.created_at.strftime('%Y-%m-%d')}")
    
    # Results
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 660, "Diagnosis Results:")
    p.setFont("Helvetica", 12)
    p.drawString(100, 640, f"Detected Condition: {report.result}")
    p.drawString(100, 625, f"Model Confidence: {round(report.confidence, 2)}%")
    
    # LIME Image (AI Interpretation)
    if report.lime_image:
        try:
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, 580, "AI Interpretation (LIME Visualization):")
            img = ImageReader(report.lime_image.path)
            p.drawImage(img, 100, 320, width=250, height=250)
            p.setFont("Helvetica-Oblique", 10)
            p.drawString(100, 305, "*Highlighted areas show features influencing the AI prediction.")
        except Exception:
            p.drawString(100, 560, "[Error loading AI visualization image]")

    # ================= NEW: CONDITIONAL PRESCRIPTION =================
    # This section appears below the image (around Y-coordinate 250)
    p.line(100, 280, 500, 280)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 260, "Doctor's Prescription & Recommendations:")
    
    p.setFont("Helvetica", 11)
    # Check if 'nodule' is in the prediction result
    if "nodule" in report.result.lower():
        p.setFillColorRGB(0.8, 0, 0) # Dark Red for urgency
        p.drawString(100, 240, "RECOMMENDATION: URGENT CT SCAN REQUIRED.")
        p.drawString(100, 225, "Clinical Note: Follow-up CT imaging is prescribed for further nodule characterization.")
    else:
        p.setFillColorRGB(0, 0, 0) # Normal Black
        p.drawString(100, 240, "RECOMMENDATION: Routine clinical follow-up.")
        p.drawString(100, 225, "Clinical Note: No specialized imaging required at this time.")

    # Reset color for the footer
    p.setFillColorRGB(0, 0, 0)

    # Footer
    if report.is_verified:
        p.setFont("Helvetica-Bold", 12)
        p.setFillColorRGB(0, 0.4, 0) # Dark Green
        p.drawString(100, 100, "STATUS: VERIFIED BY MEDICAL PROFESSIONAL")
    else:
        p.setFont("Helvetica-Bold", 12)
        p.setFillColorRGB(0.7, 0, 0) # Red
        p.drawString(100, 100, "STATUS: PENDING CLINICAL VERIFICATION")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename=f"Medical_Report_{report_id}.pdf")