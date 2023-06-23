import datetime

from django.core.validators import (
    MaxValueValidator, MinValueValidator,
    RegexValidator
)
from django.db import models

from users.models import User
from api_yamdb.settings import (MAX_LENGTH_NAME,
                                MAX_LENGTH_SLUG,
                                MAX_LENGTH_DESCRIPTION)


class Category(models.Model):
    name = models.CharField(
        'Имя категории',
        max_length=MAX_LENGTH_NAME,
        null=False
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_LENGTH_SLUG,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Недопустимый символ'
        )]
    )

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        'Название жанра',
        max_length=MAX_LENGTH_NAME,
        null=False
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_LENGTH_SLUG,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Недопустимый символ'
        )]
    )

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        'Название произведения',
        max_length=MAX_LENGTH_NAME,
        null=False
    )
    year = models.IntegerField(
        'Год выпуска',
        null=False,
        validators=[
            MinValueValidator(
                0,
                message='Год не может быть отрицательным'
            ),
            MaxValueValidator(
                int(datetime.datetime.now().year),
                message='Год не может быть больше текущего.'
            )
        ]
    )
    description = models.CharField(
        'Описание',
        max_length=MAX_LENGTH_DESCRIPTION,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='categories'
    )

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    """Отзывы."""

    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(
                1,
                message='Ниже допустимой'
            ),
            MaxValueValidator(
                10,
                message='Выше допустимой'
            ),
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        null=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('author', 'title')

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Комментарии."""

    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]
