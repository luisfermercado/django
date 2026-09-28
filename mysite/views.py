from django.views.generic import TemplateView

from blog.forms import SubscribeForm
from blog.models import Post, Subscriber


class HomeView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["latest_posts"] = Post.objects.published().select_related("category")[:3]
        ctx["subscribe_form"] = SubscribeForm(initial={"source": Subscriber.Source.CAPITAL_CHECK})
        return ctx
