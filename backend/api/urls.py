from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import LoginView
from .views import ImageDetectView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('upload/', ImageDetectView.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
