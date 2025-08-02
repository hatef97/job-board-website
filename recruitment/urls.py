from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recruitment.views import (
    CategoryViewSet,
    TagViewSet,
    CompanyProfileViewSet,
    JobViewSet,
    ApplicationViewSet,
    InterviewScheduleViewSet,
    ApplicantNoteViewSet,
)



router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'company-profiles', CompanyProfileViewSet, basename='company-profile')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'interviews', InterviewScheduleViewSet, basename='interview')
router.register(r'notes', ApplicantNoteViewSet, basename='note')



urlpatterns = [
    path('', include(router.urls)),
]
