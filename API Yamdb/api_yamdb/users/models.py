from django.contrib.auth.models import AbstractUser
from django.db import models


from api_yamdb.settings import MAX_LENGTH_ROLE

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
CHOICES_ROLE = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Админ'),
)


class User(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=MAX_LENGTH_ROLE,
        null=True,
        default='user',
        choices=CHOICES_ROLE
    )
    confirmation_code = models.IntegerField(
        'Код-подтверждения',
        null=True
    )

    class Meta:
        unique_together = ('username', 'email')

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser or self.is_staff

    @property
    def is_user(self):
        return self.role == USER
