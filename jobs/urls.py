from rest_framework.routers import DefaultRouter

from .views import *



router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'company-profiles', CompanyProfileViewSet, basename='company-profile')
router.register(r'jobs', JobViewSet, basename='job')



urlpatterns = router.urls
