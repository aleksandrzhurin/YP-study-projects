from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import SearchFilter

from posts.models import Post, Group
from .serializers import PostSerializer, CommentSerializer
from .serializers import FollowSerializer, GroupSerializer
from .permissions import AuthorOrReadOnly, FollowAuthOnly


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        return post.comments.all()

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return serializer.save(author=self.request.user,
                               post=post)


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (FollowAuthOnly, )
    filter_backends = (SearchFilter, )
    search_fields = ('user__username', 'following__username')

    def get_queryset(self):
        users = self.request.user
        return users.follower.all()

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
