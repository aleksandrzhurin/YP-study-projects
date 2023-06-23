from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreateModel


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField('Текст поста')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа, к которой будет относиться пост'
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']


class Comment(CreateModel):
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField('Текст комментария')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
