from rest_framework import filters, mixins, viewsets

from .permissions import IsAdminOrReadOnly


class MixinGenreCategoryViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'
