from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy

from .models import Post


class LatestPostsFeed(Feed):
    title = "Blog de Cuanty"
    link = reverse_lazy("blog:post_list")
    description = "Números, datos y narrativa para conseguir capital en Colombia."

    def items(self):
        return Post.objects.published().select_related("category")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_pubdate(self, item):
        return item.published_at

    def item_updateddate(self, item):
        return item.updated_at

    def item_categories(self, item):
        return [item.category.name]
