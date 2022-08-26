from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    def __str__(self):
        return self.title

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()


class Post(models.Model):
    def __str__(self):
        return f'{self.text[:15]}'

    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='group',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )

    class Meta:
        ordering = ['-pub_date']
