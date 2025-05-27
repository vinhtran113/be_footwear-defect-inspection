from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import LoginView, ImageDetectView, UserRegistrationView, UploadHistoryView, CameraControlView, CameraDetectionView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Auth endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # API endpoints
    path('upload/', ImageDetectView.as_view(), name='upload'),
    path('history-upload/', UploadHistoryView.as_view(), name='history_upload'),
    
    # Camera endpoints
    path('camera/control/', CameraControlView.as_view(), name='camera_control'),
    path('camera/detection/', CameraDetectionView.as_view(), name='camera_detection'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
