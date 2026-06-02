from django.contrib import admin
from django.urls import include, path

from app.routers import api_urlpatterns, web_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns)),
    *web_urlpatterns,
]
