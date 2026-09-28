from django import template
from django.db.models import Count, Q
from django.db.models.functions import Now

from ..models import Category, Post

register = template.Library()

PILLAR_COLORS = {
    Post.Pillar.NUMBERS: "#6753a3",
    Post.Pillar.DATA: "#9472b2",
    Post.Pillar.NARRATIVE: "#c698c5",
    Post.Pillar.CAPITAL: "#7260aa",
}


@register.filter
def pillar_color(post):
    return PILLAR_COLORS.get(post.pillar, "#6753a3")


@register.simple_tag
def latest_posts(count=3):
    return Post.objects.published().select_related("category")[:count]


@register.inclusion_tag("blog/_sidebar.html", takes_context=True)
def blog_sidebar(context):
    published = Q(posts__status=Post.Status.PUBLISHED, posts__published_at__lte=Now())
    categories = (
        Category.objects.annotate(total=Count("posts", filter=published))
        .filter(total__gt=0)
        .order_by("name")
    )
    return {
        "categories": categories,
        "recent": Post.objects.published()[:4],
        "current_category": context.get("category"),
        "request": context.get("request"),
    }


@register.simple_tag(takes_context=True)
def page_url(context, page_number):
    """Keep the search query and other filters when paginating."""
    params = context["request"].GET.copy()
    params["page"] = page_number
    return "?" + params.urlencode()
