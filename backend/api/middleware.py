import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger(__name__)

class JWTLoggingMiddleware(MiddlewareMixin):
    """
    Middleware để ghi log JWT token information khi người dùng truy cập vào API
    """
    
    def process_request(self, request):
        # Kiểm tra header Authorization
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if auth and auth.startswith('Bearer '):
            token = auth.split(' ')[1]
            try:
                # Giải mã token để lấy thông tin
                access_token = AccessToken(token)
                user_id = access_token.get('user_id')
                
                # Ghi log
                logger.info(f"Authenticated request from user_id: {user_id}")
                
                # Lưu thông tin user vào request để các view có thể sử dụng
                request.jwt_user_id = user_id
            except (InvalidToken, TokenError) as e:
                # Ghi log lỗi nếu token không hợp lệ
                logger.warning(f"Invalid token: {e}")
                
        return None 