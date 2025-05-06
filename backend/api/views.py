from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
import cv2
import numpy as np
import os
from rest_framework.parsers import MultiPartParser
from .models import ImageUpload
from .serializers import ImageUploadSerializer

class LoginView(APIView):
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
            return Response({'msg': 'Login successful'})
        return Response({'msg': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class ImageDetectView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            image_path = instance.image.path

            # Đọc ảnh gốc từ file
            img = cv2.imread(image_path)

            # Đoạn codel nhận diện
            # result = your_model.detect(img)
            # tạm thời giả lập kết quả
            result = "No defect detected"

            return Response({
                'msg': 'Image uploaded successfully',
                'image_url': instance.image.url,
                'detection_result': result
            })
        return Response(serializer.errors, status=400)
