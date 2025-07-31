from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),  # 👈 registration, activation, reset, etc.
    path('auth/', include('djoser.urls.authtoken')),  # 👈 login/logout using tokens
    path('core/', include('core.urls')),
    path('jobs/', include('jobs.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
