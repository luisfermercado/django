from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Category, Post


class PostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Post.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Category.objects.filter(posts__isnull=False).distinct()


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return ["home", "blog:post_list"]

    def location(self, item):
        return reverse(item)
