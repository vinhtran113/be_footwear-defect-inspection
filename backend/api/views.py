import matplotlib
matplotlib.use('Agg')  

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer
import cv2
import numpy as np
import os
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ImageUpload
from .serializers import ImageUploadSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from ultralytics import YOLO
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from django.conf import settings

from PIL import Image
import tempfile


import json
from .camera import camera_manager
from .camera import camera_manager


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


model_path = os.path.join(settings.BASE_DIR.parent, 'best.pt')
model = YOLO(model_path)

class ImageDetectView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]


    def post(self, request):
        uploaded_file = request.FILES.get('image')
        if not uploaded_file:
            return Response({'error': 'No image provided'}, status=400)

        img_pil = Image.open(uploaded_file).convert('RGB')
        img = np.array(img_pil)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        results = model(img, conf=0.25)
        result_image = results[0].plot()
        result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)

        buffer = BytesIO()
        plt.figure(figsize=(10, 6))
        plt.imshow(result_rgb)
        plt.axis('off')
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        detection_results = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = model.names[cls]
                detection_results.append({
                    'class': class_name,
                    'confidence': conf,
                    'box': [x1, y1, x2, y2]
                })

        return Response({
            'msg': 'Phát hiện lỗi thành công',
            'result_image': f"data:image/png;base64,{image_base64}",
            'detection_results': detection_results
        })


class RealTimeDetectView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = []

    def post(self, request):
        uploaded_file = request.FILES.get('image')
        if not uploaded_file:
            return Response({'error': 'No image provided'}, status=400)

        img_pil = Image.open(uploaded_file).convert('RGB')
        img = np.array(img_pil)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        results = model(img, conf=0.25)
        result_image = results[0].plot() 
        result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)

        _, buffer = cv2.imencode('.png', result_image)  
        image_base64 = base64.b64encode(buffer).decode('utf-8')


        detection_results = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = model.names[cls]
                detection_results.append({
                    'class': class_name,
                    'confidence': conf,
                    'box': [x1, y1, x2, y2]
                })

        return Response({
            'msg': 'Running detection',
            'result_image': f"data:image/png;base64,{image_base64}",
            'detection_results': detection_results
        })

class VideoDetectView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        uploaded_file = request.FILES.get('video')
        if not uploaded_file:
            return Response({'error': 'No image provided'}, status=400)
                
        frames = self.process_video(uploaded_file)
        if not frames:
            return Response({'error': 'No frames extracted from video'}, status=400)
        
        all_frames_results = []
        for i, frame in enumerate(frames):
            results = model(frame, conf=0.25)
            result_image = results[0].plot()
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)

            buffer = BytesIO()
            plt.figure(figsize=(10, 6))
            plt.imshow(result_rgb)
            plt.axis('off')
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            detection_results = []
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = model.names[cls]
                    detection_results.append({
                        'class': class_name,
                        'confidence': conf,
                        'box': [x1, y1, x2, y2]
                    })
            all_frames_results.append({
                'frame_index': i,
                'detection_results': detection_results,
                'result_image': f"data:image/png;base64,{image_base64}"
            })

        len_frames = len(all_frames_results)
        print(f"Total frames processed: {len_frames}")
        return Response({
            'msg': 'Phát hiện lỗi thành công',
            'len_frames': len_frames,
            'all_frames_results': all_frames_results,
        })
            
            

    def process_video(self, uploaded_file):
        video_bytes = uploaded_file.read()

        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as temp_video_file:
            temp_video_file.write(video_bytes)
            temp_video_file.flush()

            cap = cv2.VideoCapture(temp_video_file.name)
            frames = []
            frame_index = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_index % 30 == 0: # Giảm frame rate xuống 1/6
                    frames.append(frame)

                frame_index += 1

            cap.release()

        return frames
    

class UploadHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        uploads_path = os.path.join(settings.MEDIA_ROOT, 'uploads')
        file_names = os.listdir(uploads_path)
        file_urls = [request.build_absolute_uri(os.path.join(settings.MEDIA_URL, 'uploads', file)) for file in file_names]
        return Response(file_urls)

# Thêm các views mới cho camera
class CameraControlView(APIView):
    """API để điều khiển camera USB"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Bật/tắt camera hoặc thay đổi cài đặt"""
        action = request.data.get('action')
        
        if action == 'start':
            camera_id = request.data.get('camera_id', 0)
            success = camera_manager.start_camera(camera_id=int(camera_id))
            if success:
                return Response({'status': 'success', 'message': f'Camera {camera_id} đã được bật'})
            else:
                return Response({
                    'status': 'error', 
                    'message': f'Không thể bật camera {camera_id}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        elif action == 'stop':
            camera_manager.stop_camera()
            return Response({'status': 'success', 'message': 'Camera đã được tắt'})
            
        return Response({
            'status': 'error', 
            'message': 'Hành động không hợp lệ'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """Kiểm tra trạng thái camera"""
        is_running = camera_manager.is_running
        return Response({
            'status': 'success',
            'camera_running': is_running
        })

class CameraDetectionView(APIView):
    """API để lấy kết quả phát hiện từ camera theo thời gian thực"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Lấy kết quả phát hiện mới nhất"""
        if not camera_manager.is_running:
            return Response({
                'status': 'error', 
                'message': 'Camera chưa được bật'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        detection = camera_manager.get_latest_detection()
        
        if detection is None:
            return Response({
                'status': 'pending', 
                'message': 'Đang chờ kết quả phát hiện đầu tiên'
            })
            
        return Response({
            'status': 'success',
            'result_image': detection['result_image'],
            'detection_results': detection['detection_results'],
            'timestamp': detection['timestamp']
        })
    
    def post(self, request):
        """Yêu cầu phát hiện ngay lập tức (không đợi vòng lặp)"""
        if not camera_manager.is_running:
            return Response({
                'status': 'error', 
                'message': 'Camera chưa được bật'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        detection = camera_manager.process_frame()
        
        if detection is None:
            return Response({
                'status': 'error', 
                'message': 'Không thể thực hiện phát hiện'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
            'status': 'success',
            'result_image': detection['result_image'],
            'detection_results': detection['detection_results'],
            'timestamp': detection['timestamp']
        })

class CameraCaptureView(APIView):
    """API để chụp một frame từ camera và phát hiện lỗi"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Chụp một frame mới và thực hiện phát hiện"""
        if not camera_manager.is_running:
            return Response({
                'status': 'error', 
                'message': 'Camera chưa được bật'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Chụp và xử lý frame mới
        detection = camera_manager.capture_and_process_frame()
        
        if detection is None:
            return Response({
                'status': 'error', 
                'message': 'Không thể chụp hoặc xử lý frame'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
            'status': 'success',
            'message': 'Đã chụp và phát hiện thành công',
            'result_image': detection['result_image'],
            'detection_results': detection['detection_results'],
            'timestamp': detection['timestamp']
        })