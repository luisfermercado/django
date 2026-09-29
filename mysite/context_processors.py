from django.conf import settings


def site(request):
    return {"canonical_origin": settings.CANONICAL_ORIGIN}
