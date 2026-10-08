from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import json

from .forms import CommentForm, SearchForm, SubscribeForm
from .models import Category, Post, Subscriber, Tag


class PostListView(ListView):
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        qs = Post.objects.published().select_related("category", "author").prefetch_related("tags")
        self.category = self.tag = None
        if "category" in self.kwargs:
            self.category = get_object_or_404(Category, slug=self.kwargs["category"])
            qs = qs.filter(category=self.category)
        if "tag" in self.kwargs:
            self.tag = get_object_or_404(Tag, slug=self.kwargs["tag"])
            qs = qs.filter(tags=self.tag)
        self.search_form = SearchForm(self.request.GET)
        self.query = ""
        if self.search_form.is_valid():
            self.query = self.search_form.cleaned_data["q"].strip()
        if self.query:
            qs = qs.filter(
                Q(title__icontains=self.query) | Q(excerpt__icontains=self.query) | Q(body__icontains=self.query)
            ).distinct()
        # The featured post gets its own block on the unfiltered list, so keep it out of the grid.
        self.featured = None
        if not (self.category or self.tag or self.query):
            self.featured = qs.filter(featured=True).first()
            if self.featured:
                qs = qs.exclude(pk=self.featured.pk)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            category=self.category,
            tag=self.tag,
            query=self.query,
            search_form=self.search_form,
            featured=self.featured if ctx["page_obj"].number == 1 else None,
        )
        return ctx


class PostDetailView(FormMixin, DetailView):
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    form_class = CommentForm

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post.objects.published().select_related("category", "author").prefetch_related("tags"),
            slug=self.kwargs["slug"],
            published_at__year=self.kwargs["year"],
            published_at__month=self.kwargs["month"],
            published_at__day=self.kwargs["day"],
        )

    def get_success_url(self):
        return self.object.get_absolute_url() + "#comentarios"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.object
        published = Post.objects.published()
        tag_ids = post.tags.values_list("id", flat=True)
        related = (
            published.filter(tags__in=tag_ids)
            .exclude(pk=post.pk)
            .annotate(shared=Count("tags"))
            .order_by("-shared", "-published_at")
            .select_related("category")[:3]
        )
        if not related:
            related = published.filter(category=post.category).exclude(pk=post.pk).select_related("category")[:3]
        ctx.update(
            comments=post.comments.filter(approved=True),
            related=related,
            previous_post=published.filter(published_at__lt=post.published_at).order_by("-published_at").first(),
            next_post=published.filter(published_at__gt=post.published_at).order_by("published_at").first(),
        )
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.save()
            messages.success(request, "Gracias. Tu comentario se publicará cuando lo revisemos.")
            return redirect(self.get_success_url())
        messages.error(request, "Revisa los campos marcados.")
        return self.render_to_response(self.get_context_data(form=form))


def _wants_json(request):
    return "application/json" in request.headers.get("Accept", "")


@require_POST
def subscribe(request):
    form = SubscribeForm(request.POST)
    if not form.is_valid():
        if _wants_json(request):
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
        messages.error(request, "Escribe un correo válido.")
        return redirect(request.META.get("HTTP_REFERER") or "blog:post_list")

    data = form.cleaned_data
    subscriber, created = Subscriber.objects.get_or_create(
        email=data["email"].lower(),
        defaults={"source": data["source"] or Subscriber.Source.BLOG, "diagnosis": data["diagnosis"]},
    )
    if not created and data["diagnosis"]:
        subscriber.diagnosis = data["diagnosis"]
        subscriber.save(update_fields=["diagnosis"])

    if data.get("diagnosis"):
        try:
            # En Django, forms.JSONField ya parsea el string a dict.
            diag_data = data["diagnosis"] if isinstance(data["diagnosis"], dict) else json.loads(data["diagnosis"])
            html_message = render_to_string('blog/emails/diagnosis_report.html', {'diagnosis': diag_data})
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject='Tu resultado del Capital Check AI de Cuanty',
                message=plain_message,
                from_email=None, # usa DEFAULT_FROM_EMAIL
                recipient_list=[subscriber.email],
                html_message=html_message,
                fail_silently=False, # Ponemos false para ver errores en terminal
            )
        except Exception as e:
            # En producción se recomienda usar logging
            print(f"Error enviando correo: {e}")

    if _wants_json(request):
        return JsonResponse({"ok": True})
    messages.success(request, "Listo. Te avisaremos cuando publiquemos algo nuevo.")
    return redirect(request.META.get("HTTP_REFERER") or "blog:post_list")


def post_by_pk(request, pk):
    """Short link /blog/p/<pk>/ that redirects to the canonical URL."""
    post = get_object_or_404(Post.objects.published(), pk=pk)
    return redirect(post, permanent=True)
