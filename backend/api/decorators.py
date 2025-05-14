from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
import jwt

def jwt_required(view_func):
    """
    Decorator để xác thực JWT token trước khi cho phép truy cập API
    """
    @wraps(view_func)
    def _wrapped_view(view_instance, request, *args, **kwargs):
        # Kiểm tra header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                {'error': 'Authentication credentials were not provided or invalid.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token = auth_header.split(' ')[1]
        try:
            # Giải mã token
            decoded_token = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.SIMPLE_JWT['ALGORITHM']]
            )
            
            # Lưu thông tin user vào request
            request.jwt_user = decoded_token
            request.jwt_user_id = decoded_token.get('user_id')
            
            # Gọi hàm view gốc
            return view_func(view_instance, request, *args, **kwargs)
        
        except jwt.ExpiredSignatureError:
            return Response(
                {'error': 'Token has expired.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except (jwt.DecodeError, jwt.InvalidTokenError, TokenError):
            return Response(
                {'error': 'Invalid token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    return _wrapped_view 