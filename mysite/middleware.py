from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """On Railway, send requests for www.cuanty.co to https://cuanty.co with a 301.

    Other hosts (such as *.up.railway.app) are left alone.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.ON_RAILWAY:
            host = request.get_host().split(":")[0].lower()
            if host in settings.REDIRECT_TO_CANONICAL_HOSTS:
                return HttpResponsePermanentRedirect(settings.CANONICAL_ORIGIN + request.get_full_path())
        return self.get_response(request)
