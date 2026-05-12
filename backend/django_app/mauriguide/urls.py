from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/datasets/", include("datasets.urls")),
    path("api/itinerary/", include("itinerary.urls")),
    path("api/", include("api.urls")),
    path("", include("frontend.urls")),
]

# Serve media files in both dev and production
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files in development only (whitenoise handles production)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)