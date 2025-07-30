from rest_framework.routers import DefaultRouter

from .views import *



router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'company-profiles', CompanyProfileViewSet, basename='company-profile')



urlpatterns = router.urls
