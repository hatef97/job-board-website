from rest_framework.routers import DefaultRouter

from .views import *



router = DefaultRouter()
router.register('categories', CategoryViewSet)



urlpatterns = router.urls
