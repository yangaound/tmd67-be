from .views import ACIDRegister, ACIDDirectory
from django.urls import path
from django.urls import re_path, include

urlpatterns = [
    path(r'user-register/', ACIDRegister.as_view()),
    path(r'user-directory/', ACIDDirectory.as_view()),
    re_path(r'accounts/', include('rest_framework.urls', namespace='admin')),
]
