from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from blog.sitemaps import CategorySitemap, PostSitemap, StaticSitemap

from .views import HomeView

sitemaps = {"static": StaticSitemap, "posts": PostSitemap, "categories": CategorySitemap}

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("blog/", include("blog.urls")),
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]
