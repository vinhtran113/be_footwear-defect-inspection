import matplotlib
matplotlib.use('Agg')  

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer
import os

from rest_framework_simplejwt.tokens import RefreshToken


from django.conf import settings





class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Tài khoản test 
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user(username='testuser', password='123456')

        # Lấy dữ liệu từ client
        username = request.data.get('username')
        password = request.data.get('password')

        # Xác thực đăng nhập
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'msg': 'Login successful'
            })
        return Response({'msg': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
