# Hệ thống phát hiện lỗi sản phẩm sử dụng YOLOv8

Hệ thống backend sử dụng YOLOv8 với model `best.pt` để phát hiện lỗi trong hình ảnh sản phẩm.

## Cài đặt

### Yêu cầu
- Python 3.9+
- Django 5.2
- Ultralytics 8.2.83
- OpenCV
- Thư viện khác (xem `requirements.txt`)

### Cài đặt các gói phụ thuộc
```bash
pip install -r backend/requirements.txt
```

## Chạy server

```bash
python backend/manage.py runserver
```

## API Endpoints

### Đăng nhập
```
POST /api/login/
```
Dữ liệu gửi lên:
```json
{
    "username": "testuser",
    "password": "123456"
}
```
Phản hồi:
```json
{
    "refresh": "<refresh_token>",
    "access": "<access_token>",
    "msg": "Login successful"
}
```

### Phát hiện lỗi trong ảnh
```
POST /api/upload/
```

Headers:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

Dữ liệu gửi lên:
```
image: <file>
```

Phản hồi:
```json
{
    "msg": "Phát hiện lỗi thành công",
    "image_url": "/media/uploads/image.jpg",
    "result_image": "data:image/png;base64,...",
    "detection_results": [
        {
            "class": "scratch",
            "confidence": 0.87,
            "box": [100, 200, 300, 400]
        },
        {
            "class": "dent",
            "confidence": 0.75,
            "box": [500, 600, 700, 800]
        }
    ]
}
```

### Sử dụng Camera USB cho phát hiện lỗi

#### Điều khiển Camera

##### Bật camera:
```
POST /api/camera/control/
```

Headers:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

Body:
```json
{
    "action": "start",
    "camera_id": 0  // Mặc định là 0, có thể thay đổi tùy theo thiết bị
}
```

Phản hồi:
```json
{
    "status": "success",
    "message": "Camera 0 đã được bật"
}
```

##### Tắt camera:
```
POST /api/camera/control/
```

Headers:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

Body:
```json
{
    "action": "stop"
}
```

Phản hồi:
```json
{
    "status": "success",
    "message": "Camera đã được tắt"
}
```

##### Kiểm tra trạng thái camera:
```
GET /api/camera/control/
```

Headers:
```
Authorization: Bearer <access_token>
```

Phản hồi:
```json
{
    "status": "success",
    "camera_running": true
}
```

#### Chụp ảnh và phát hiện lỗi

##### Chụp và phát hiện:
```
POST /api/camera/capture/
```

Headers:
```
Authorization: Bearer <access_token>
```

Phản hồi:
```json
{
    "status": "success",
    "message": "Đã chụp và phát hiện thành công",
    "result_image": "data:image/png;base64,...",
    "detection_results": [
        {
            "class": "scratch",
            "confidence": 0.87,
            "box": [100, 200, 300, 400]
        }
    ],
    "timestamp": 1621234567.890
}
```



