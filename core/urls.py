from django.urls import path, include

from rest_framework.routers import DefaultRouter

from core.views import UserViewSet, CheckEmailView



router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')



urlpatterns = router.urls + [
    path('check-email/', CheckEmailView.as_view(), name='auth-check-email'),
]
