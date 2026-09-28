import math

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Post.Status.PUBLISHED, published_at__lte=timezone.now())


class Category(models.Model):
    name = models.CharField("nombre", max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    description = models.TextField("descripción", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", args=[self.slug])


class Tag(models.Model):
    name = models.CharField("nombre", max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "etiqueta"
        verbose_name_plural = "etiquetas"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:tag", args=[self.slug])


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PUBLISHED = "published", "Publicado"

    # Matches the three bars of the brand: numbers, data, narrative.
    class Pillar(models.TextChoices):
        NUMBERS = "numeros", "Números"
        DATA = "datos", "Datos"
        NARRATIVE = "narrativa", "Narrativa"
        CAPITAL = "capital", "Capital"

    title = models.CharField("título", max_length=200)
    slug = models.SlugField(max_length=220, unique_for_date="published_at")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="blog_posts",
        verbose_name="autor",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="posts",
        verbose_name="categoría",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts", verbose_name="etiquetas")
    pillar = models.CharField("pilar", max_length=12, choices=Pillar.choices, default=Pillar.NUMBERS)
    excerpt = models.TextField("resumen", max_length=300, help_text="Aparece en listados y en la vista previa al compartir.")
    body = models.TextField("contenido", help_text="Separa los párrafos con una línea en blanco.")
    status = models.CharField("estado", max_length=10, choices=Status.choices, default=Status.DRAFT)
    featured = models.BooleanField("destacado", default=False)
    published_at = models.DateTimeField("fecha de publicación", default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at"]
        indexes = [models.Index(fields=["-published_at"]), models.Index(fields=["status"])]
        verbose_name = "artículo"
        verbose_name_plural = "artículos"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        local = timezone.localtime(self.published_at)
        return reverse("blog:post_detail", args=[local.year, local.month, local.day, self.slug])

    @property
    def reading_minutes(self):
        words = len(strip_tags(self.body).split())
        return max(1, math.ceil(words / 200))

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED and self.published_at <= timezone.now()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="artículo")
    name = models.CharField("nombre", max_length=80)
    email = models.EmailField("correo")
    body = models.TextField("comentario", max_length=2000)
    approved = models.BooleanField("aprobado", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "comentario"
        verbose_name_plural = "comentarios"

    def __str__(self):
        return f"{self.name} en «{self.post}»"


class Subscriber(models.Model):
    class Source(models.TextChoices):
        BLOG = "blog", "Boletín del blog"
        CAPITAL_CHECK = "capital_check", "Capital Check AI"

    email = models.EmailField("correo", unique=True)
    source = models.CharField("origen", max_length=20, choices=Source.choices, default=Source.BLOG)
    # Answers from the Capital Check quiz, when the subscriber came from there.
    diagnosis = models.JSONField("diagnóstico", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "suscriptor"
        verbose_name_plural = "suscriptores"

    def __str__(self):
        return self.email
