import tempfile
from pathlib import Path

from django.conf import settings
from django.test import TestCase, override_settings

RAILWAY_HOSTS = ["cuanty.co", "www.cuanty.co", ".up.railway.app", "testserver"]


@override_settings(ON_RAILWAY=True, ALLOWED_HOSTS=RAILWAY_HOSTS)
class CanonicalHostTests(TestCase):
    def test_www_redirects_to_apex_keeping_path_and_query(self):
        response = self.client.get("/blog/?q=credito&page=2", HTTP_HOST="www.cuanty.co")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://cuanty.co/blog/?q=credito&page=2")

    def test_apex_and_railway_domain_are_served(self):
        for host in ("cuanty.co", "cuanty-production.up.railway.app"):
            with self.subTest(host=host):
                self.assertEqual(self.client.get("/", HTTP_HOST=host).status_code, 200)

    def test_unknown_host_is_rejected(self):
        self.assertEqual(self.client.get("/", HTTP_HOST="evil.example").status_code, 400)


class CanonicalHostOffLocallyTests(TestCase):
    @override_settings(ON_RAILWAY=False, ALLOWED_HOSTS=RAILWAY_HOSTS)
    def test_no_redirect_outside_railway(self):
        self.assertEqual(self.client.get("/", HTTP_HOST="www.cuanty.co").status_code, 200)


class SiteTests(TestCase):
    def test_canonical_link_points_to_apex(self):
        self.assertContains(self.client.get("/blog/?page=1"), '<link rel="canonical" href="https://cuanty.co/blog/">')

    def test_favicon_redirects_to_static_file(self):
        response = self.client.get("/favicon.ico")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/static/favicon.ico")

    def test_media_files_are_served(self):
        media_root = Path(settings.MEDIA_ROOT)
        media_root.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=media_root, suffix=".txt") as f:
            f.write(b"hola")
            f.flush()
            response = self.client.get("/media/" + Path(f.name).name)
            self.assertEqual(b"".join(response.streaming_content), b"hola")
