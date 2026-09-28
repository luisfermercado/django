from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Comment, Post, Subscriber, Tag


class BlogTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Finanzas", slug="finanzas")
        cls.tag = Tag.objects.create(name="Crédito", slug="credito")
        cls.post = Post.objects.create(
            title="Flujo de caja a tres años",
            category=cls.category,
            excerpt="Resumen",
            body="Uno dos tres.\n\nCuatro.",
            status=Post.Status.PUBLISHED,
            published_at=timezone.now() - timedelta(days=1),
        )
        cls.post.tags.add(cls.tag)
        cls.draft = Post.objects.create(title="Borrador secreto", category=cls.category, excerpt="x", body="x")
        cls.scheduled = Post.objects.create(
            title="Programado",
            category=cls.category,
            excerpt="x",
            body="x",
            status=Post.Status.PUBLISHED,
            published_at=timezone.now() + timedelta(days=3),
        )


class ModelTests(BlogTestCase):
    def test_slug_is_generated(self):
        self.assertEqual(self.post.slug, "flujo-de-caja-a-tres-anos")

    def test_published_excludes_drafts_and_future_posts(self):
        self.assertEqual(list(Post.objects.published()), [self.post])

    def test_reading_minutes_is_at_least_one(self):
        self.assertEqual(self.post.reading_minutes, 1)


class ViewTests(BlogTestCase):
    def test_home_lists_latest_posts(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, self.post.title)
        self.assertNotContains(response, self.draft.title)

    def test_list_filters(self):
        self.assertContains(self.client.get(reverse("blog:post_list")), self.post.title)
        self.assertContains(self.client.get(reverse("blog:category", args=["finanzas"])), self.post.title)
        self.assertContains(self.client.get(reverse("blog:tag", args=["credito"])), self.post.title)
        self.assertNotContains(self.client.get(reverse("blog:post_list"), {"q": "inexistente"}), 'class="post-card"')
        self.assertEqual(self.client.get(reverse("blog:category", args=["nada"])).status_code, 404)

    def test_featured_post_is_not_repeated_in_grid(self):
        Post.objects.filter(pk=self.post.pk).update(featured=True)
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.context["featured"], self.post)
        self.assertNotIn(self.post, response.context["posts"])

    def test_detail_and_unpublished_404(self):
        self.assertContains(self.client.get(self.post.get_absolute_url()), "Cuatro.")
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(self.scheduled.get_absolute_url()).status_code, 404)

    def test_comment_is_held_for_moderation(self):
        url = self.post.get_absolute_url()
        response = self.client.post(url, {"name": "Ana", "email": "ana@example.com", "body": "Muy útil"}, follow=True)
        comment = Comment.objects.get()
        self.assertFalse(comment.approved)
        self.assertNotContains(response, "Muy útil")
        comment.approved = True
        comment.save()
        self.assertContains(self.client.get(url), "Muy útil")

    def test_comment_honeypot_rejects_bots(self):
        self.client.post(self.post.get_absolute_url(), {"name": "b", "email": "b@b.co", "body": "spam", "website": "x"})
        self.assertFalse(Comment.objects.exists())

    def test_subscribe_json_saves_diagnosis(self):
        response = self.client.post(
            reverse("blog:subscribe"),
            {"email": "Ceo@Empresa.co", "source": "capital_check", "diagnosis": '{"recommendation": "Pitch Lab"}'},
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.json(), {"ok": True})
        sub = Subscriber.objects.get()
        self.assertEqual(sub.email, "ceo@empresa.co")
        self.assertEqual(sub.diagnosis, {"recommendation": "Pitch Lab"})

    def test_feed_and_sitemap(self):
        self.assertContains(self.client.get(reverse("blog:feed")), self.post.title)
        sitemap = self.client.get("/sitemap.xml")
        self.assertContains(sitemap, self.post.get_absolute_url())
        self.assertNotContains(sitemap, self.draft.slug)


class SeedCommandTests(TestCase):
    def test_seed_is_idempotent(self):
        call_command("seed_blog", verbosity=0)
        count = Post.objects.count()
        call_command("seed_blog", verbosity=0)
        self.assertEqual(Post.objects.count(), count)
        self.assertTrue(Post.objects.published().filter(featured=True).exists())
