from rest_framework.routers import DefaultRouter

from .views import *



router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'tags', TagViewSet, basename='tags')



urlpatterns = router.urls
