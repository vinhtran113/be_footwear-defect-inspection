# BE_FOOTWEAR-DEFECT-INSPECTION

Backend API cho hệ thống kiểm tra lỗi giày dép, hỗ trợ:
- Đăng nhập bằng tài khoản có sẵn
- Upload ảnh và nhận diện lỗi qua model đã huấn luyện

---

## Yêu cầu hệ thống

- Python >= 3.9
- pip
- Virtualenv (nên dùng)
- OpenCV (`cv2`)
- Django
- djangorestframework

---

## Hướng dẫn cài đặt

Mở Command Prompt:

### 1. Clone repository

git clone <repo_url>
cd be_footwear-defect-inspection
cd backend

### 2. Tạo và kích hoạt môi trường ảo

#### Tạo môi trường ảo (Windows)
python -m venv env

#### Kích hoạt môi trường ảo
env\Scripts\activate

### 3. Cài đặt các thư viện cần thiết

pip install -r requirements.txt

### 4. Chạy migrate database

python manage.py makemigrations
python manage.py migrate

### 5. Chạy server

python manage.py runserver

Truy cập tại:
http://127.0.0.1:8000/

---

## API Endpoint

### POST /api/login/

{
  "username": "testuser",
  "password": "123456"
}

### POST /api/upload/

Dạng multipart/form-data:

Key: image

Value: file ảnh

Kết quả trả về:

{
  "msg": "Image uploaded successfully",
  "image_url": "/media/uploads/abc.jpg",
  "detection_result": "No defect detected"
}

---
### Xác thực JWT
Đăng nhập và lấy token

POST http://127.0.0.1:8000/api/token/
   Content-Type: application/json
   
   {
     "username": "testuser",
     "password": "yourpassword"
   }

Làm mới token khi hết hạn

   POST http://127.0.0.1:8000/api/token/refresh/
   Content-Type: application/json
   
   {
     "refresh": "your_refresh_token_here"
   }

Xác thực token

   POST http://127.0.0.1:8000/api/token/verify/
   Content-Type: application/json
   
   {
     "token": "your_access_token_here"
   }

JWT cho truy cập API được bảo vệ (như upload endpoint)
   POST http://127.0.0.1:8000/api/upload/
   Authorization: Bearer your_access_token_here
   Content-Type: multipart/form-data
   
   (form-data với field "image" và file ảnh)

## Ghi chú
Tài khoản testuser / 123456 được tạo để kiểm tra thử api đăng nhập nếu chưa tồn tại.

Ảnh upload được lưu vào thư mục media/uploads/.



