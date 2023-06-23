from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, GenreViewSet, TitleViewSet,
                    ReviewViewSet, CommentViewSet,)
from users.views import (UserViewSet, UserSignUp, get_token)

v1_router = DefaultRouter()
v1_router.register('users', UserViewSet)
v1_router.register('categories', CategoryViewSet)
v1_router.register('genres', GenreViewSet)
v1_router.register('titles', TitleViewSet)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

auth_urls = [
    'v1/auth/signup/',
    'v1/auth/token/',
]


urlpatterns = [
    path(auth_urls[0], UserSignUp.as_view()),
    path(auth_urls[1], get_token),
    path('v1/', include(v1_router.urls))
]
