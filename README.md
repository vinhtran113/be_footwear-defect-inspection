# Hệ thống phát hiện lỗi sản phẩm sử dụng YOLOv8

Hệ thống backend sử dụng YOLOv8 với model `best.pt` để phát hiện lỗi trong hình ảnh sản phẩm.

link dowload best.pt và thêm vào folder be_footwear-defect-inspection

    https://drive.google.com/file/d/1UeriZ18Cbp2TbjHgBjjGHTQQI2NODfpA/view?usp=drive_link
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

## Sử dụng với Python client

Dưới đây là ví dụ về cách sử dụng API từ Python:

```python
import requests
import json
import base64
import matplotlib.pyplot as plt
from io import BytesIO

# Đăng nhập
login_response = requests.post(
    'http://localhost:8000/api/login/',
    json={'username': 'testuser', 'password': '123456'}
)
token = login_response.json()['access']

# Tải ảnh lên và phát hiện lỗi
headers = {'Authorization': f'Bearer {token}'}
files = {'image': open('path/to/your/image.jpg', 'rb')}

response = requests.post(
    'http://localhost:8000/api/upload/',
    headers=headers,
    files=files
)

result = response.json()
print(f"Kết quả phát hiện: {result['msg']}")
print(f"Số lượng lỗi phát hiện: {len(result['detection_results'])}")

# Hiển thị ảnh kết quả
image_data = result['result_image'].split(',')[1]
image = BytesIO(base64.b64decode(image_data))
plt.figure(figsize=(10, 8))
plt.imshow(plt.imread(image))
plt.axis('off')
plt.show()
```



