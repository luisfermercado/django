from django.urls import path

from . import views
from .feeds import LatestPostsFeed

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("categoria/<slug:category>/", views.PostListView.as_view(), name="category"),
    path("etiqueta/<slug:tag>/", views.PostListView.as_view(), name="tag"),
    path("<int:year>/<int:month>/<int:day>/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    path("p/<int:pk>/", views.post_by_pk, name="short"),
    path("suscribirme/", views.subscribe, name="subscribe"),
    path("feed/", LatestPostsFeed(), name="feed"),
]
