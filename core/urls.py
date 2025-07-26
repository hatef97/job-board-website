from django.urls import path, include

from rest_framework.routers import DefaultRouter

from core.views import UserViewSet, CheckEmailView, EmployerProfileViewSet, ApplicantProfileViewSet



router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'employer-profiles', EmployerProfileViewSet, basename='employer-profiles')
router.register(r'applicant-profiles', ApplicantProfileViewSet, basename='applicant-profiles')



urlpatterns = router.urls + [
    path('check-email/', CheckEmailView.as_view(), name='auth-check-email'),
]
