from django.contrib import admin
from django.conf import settings
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("whatsapp_scraper.urls")),
]

if settings.DEBUG_TOOLBAR_ENABLED is True:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
