from rest_framework import serializers

from reviews.models import Comment, Review, Category, Genre, Title


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)


class PageReadTitleSerializer(serializers.ModelSerializer):
    """Сериализатор Title при запросах GET"""
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id',
                  'name',
                  'year',
                  'rating',
                  'description',
                  'genre',
                  'category')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор Title при любых запросах кроме GET"""
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category')

    def to_representation(self, instance):
        serializer = PageReadTitleSerializer(instance)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if not self.context.get('request').method == "POST":
            return data
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Отзыв на данное произведение уже оставлен.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
