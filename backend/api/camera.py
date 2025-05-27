import cv2
import threading
import time
import numpy as np
from django.conf import settings
import os
from ultralytics import YOLO
import base64
from io import BytesIO
import matplotlib.pyplot as plt

class CameraManager:
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.frame = None
        self.last_detection = None
        self.detection_results = []
        self.thread = None
        
        # Đường dẫn đến model YOLOv8
        self.model_path = os.path.join(settings.BASE_DIR.parent, 'best.pt')
        self.model = YOLO(self.model_path)
    
    def start_camera(self, camera_id=0):
        """Bắt đầu kết nối với camera"""
        if self.is_running:
            return False
            
        try:
            self.camera = cv2.VideoCapture(camera_id)
            if not self.camera.isOpened():
                raise Exception("Không thể mở camera")
                
            self.is_running = True
            self.thread = threading.Thread(target=self._capture_loop)
            self.thread.daemon = True
            self.thread.start()
            return True
        except Exception as e:
            print(f"Lỗi khi kết nối camera: {str(e)}")
            return False
    
    def stop_camera(self):
        """Dừng kết nối camera"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        if self.camera and self.camera.isOpened():
            self.camera.release()
            self.camera = None
    
    def _capture_loop(self):
        """Vòng lặp capture frame từ camera"""
        while self.is_running:
            if self.camera and self.camera.isOpened():
                success, frame = self.camera.read()
                if success:
                    self.frame = frame
                    # Thực hiện phát hiện mỗi 5 frames để giảm tải
                    if np.random.randint(0, 5) == 0:
                        self.process_frame()
            time.sleep(0.03)  # ~30 FPS
    
    def process_frame(self):
        """Xử lý frame hiện tại với YOLOv8"""
        if self.frame is None:
            return None
            
        # Thực hiện phát hiện với model YOLOv8
        results = self.model(self.frame, conf=0.25)
        
        # Vẽ kết quả lên ảnh
        result_image = results[0].plot()
        
        # Chuyển sang định dạng RGB để hiển thị đúng màu sắc
        result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
        
        # Chuyển đổi ảnh thành base64
        buffer = BytesIO()
        plt.figure(figsize=(10, 6))
        plt.imshow(result_rgb)
        plt.axis('off')
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Lấy kết quả phát hiện
        detection_results = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = self.model.names[cls]
                detection_results.append({
                    'class': class_name,
                    'confidence': conf,
                    'box': [x1, y1, x2, y2]
                })
        
        # Lưu kết quả phát hiện mới nhất
        self.last_detection = {
            'result_image': f"data:image/png;base64,{image_base64}",
            'detection_results': detection_results,
            'timestamp': time.time()
        }
        self.detection_results = detection_results
        
        return self.last_detection
    
    def get_latest_detection(self):
        """Lấy kết quả phát hiện mới nhất"""
        return self.last_detection

# Singleton instance
camera_manager = CameraManager() 