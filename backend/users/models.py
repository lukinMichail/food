from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import UniqueConstraint

from backend.settings import LIMITATION


class User(AbstractUser):
    """Модель пользователей."""

    email = models.EmailField(
        'Email',
        max_length=200,
        unique=True
    )
    first_name = models.CharField('Имя', max_length=LIMITATION)
    last_name = models.CharField('Фамилия', max_length=LIMITATION)
    username = models.CharField(
        validators=(UnicodeUsernameValidator(),),
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок пользователя."""

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follows"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        ordering = ('-id', )
        constraints = [
            UniqueConstraint(
                fields=('follower', 'following'),
                name='unique_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'{self.follower} подписан на {self.following}'
