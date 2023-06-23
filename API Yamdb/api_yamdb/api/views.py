from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .mixins import MixinGenreCategoryViewSet
from reviews.models import Category, Genre, Title
from .serializers import (
    GenreSerializer,
    CategorySerializer,
    TitleSerializer,
    PageReadTitleSerializer,
    ReviewSerializer,
    CommentSerializer,
)
from .services import TitleFilter
from .permissions import (AdminOrSuperUser,
                          ModeratorOrReadOnly,
                          AuthorOrReadOnly,
                          IsAdminOrReadOnly,
                          )
from reviews.models import Review


class GenreViewSet(MixinGenreCategoryViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(MixinGenreCategoryViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer()
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PageReadTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = ((ModeratorOrReadOnly
                          | AuthorOrReadOnly
                          | AdminOrSuperUser),)

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        return self.get_title().reviews.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = ((ModeratorOrReadOnly
                          | AuthorOrReadOnly
                          | AdminOrSuperUser),)

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
