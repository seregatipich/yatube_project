from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='тайтл')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Slug')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Text')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='pub_date')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='author'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
        verbose_name='group'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
