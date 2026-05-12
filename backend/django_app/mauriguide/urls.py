from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Existing API endpoints
    path("api/accounts/", include("accounts.urls")),
    path("api/datasets/", include("datasets.urls")),
    path("api/itinerary/", include("itinerary.urls")),
    
    # New API endpoints for FastAPI integration
    path("api/", include("api.urls")),  # Add this line
    
    # Frontend
    path("", include("frontend.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)