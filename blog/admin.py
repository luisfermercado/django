from django.contrib import admin, messages
from django.db.models import Count
from django.utils import timezone

from .models import Category, Comment, Post, Subscriber, Tag


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("name", "email", "body", "approved", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "post_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_post_count=Count("posts"))

    @admin.display(description="artículos", ordering="_post_count")
    def post_count(self, obj):
        return obj._post_count


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "pillar", "author", "status", "featured", "published_at")
    list_filter = ("status", "featured", "pillar", "category", "tags", "published_at")
    list_editable = ("status", "featured")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("tags",)
    raw_id_fields = ("author",)
    date_hierarchy = "published_at"
    ordering = ("-published_at",)
    inlines = (CommentInline,)
    actions = ("publish_now", "mark_draft")
    fieldsets = (
        (None, {"fields": ("title", "slug", "excerpt", "body")}),
        ("Clasificación", {"fields": ("category", "pillar", "tags")}),
        ("Publicación", {"fields": ("author", "status", "featured", "published_at")}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="Publicar ahora")
    def publish_now(self, request, queryset):
        count = queryset.update(status=Post.Status.PUBLISHED, published_at=timezone.now())
        self.message_user(request, f"{count} artículo(s) publicados.", messages.SUCCESS)

    @admin.action(description="Pasar a borrador")
    def mark_draft(self, request, queryset):
        count = queryset.update(status=Post.Status.DRAFT)
        self.message_user(request, f"{count} artículo(s) pasados a borrador.", messages.SUCCESS)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "post", "approved", "created_at")
    list_filter = ("approved", "created_at")
    search_fields = ("name", "email", "body")
    list_select_related = ("post",)
    actions = ("approve",)

    @admin.action(description="Aprobar comentarios seleccionados")
    def approve(self, request, queryset):
        count = queryset.update(approved=True)
        self.message_user(request, f"{count} comentario(s) aprobados.", messages.SUCCESS)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "source", "created_at")
    list_filter = ("source", "created_at")
    search_fields = ("email",)
    readonly_fields = ("diagnosis", "created_at")


admin.site.site_header = "Cuanty · Administración"
admin.site.site_title = "Cuanty"
admin.site.index_title = "Contenido del sitio"
