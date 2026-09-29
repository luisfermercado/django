from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.templatetags.static import static
from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve

from blog.sitemaps import CategorySitemap, PostSitemap, StaticSitemap

from .views import HomeView

sitemaps = {"static": StaticSitemap, "posts": PostSitemap, "categories": CategorySitemap}

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("blog/", include("blog.urls")),
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    # Browsers request /favicon.ico directly, regardless of the <link> tags.
    path("favicon.ico", RedirectView.as_view(url=static("favicon.ico"), permanent=True)),
    # Django doesn't serve uploads when DEBUG is off; this small site serves them itself.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
