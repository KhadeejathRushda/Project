from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.role == "doctor" and not getattr(user, 'is_doctor_verified', False):
            return Response({"error": "Doctor account pending admin approval."}, status=403)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'role': user.role,
            'username': user.username,
            'user_id': user.id
        }, status=200)
    return Response({'error': 'Invalid credentials'}, status=401)

@api_view(['GET'])
@permission_classes([AllowAny])
def doctor_list(request):
    # Provides the Dropbox data for Patient Registration
    doctors = User.objects.filter(role='doctor', is_doctor_verified=True).values('id', 'username', 'name')
    return Response(list(doctors), status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_list(request):
    # Provides the Dropbox data for Doctor's Upload X-ray page
    patients = User.objects.filter(role='patient', assigned_doctor=request.user).values('id', 'username', 'name')
    return Response(list(patients), status=200)