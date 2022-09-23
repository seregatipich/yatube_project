import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Группа',
            description='Описание поста',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Текст поста',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_create_post(self):
        posts_count = Post.objects.count()

        form_data = {
            'group': self.group.pk,
            'text': self.post.text,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={
                'username': PostCreateFormTests.post.author
            }))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text=self.post.text,
            ).exists()
        )

    def test_edit_post(self):
        tasks_count = Post.objects.count()
        form_data = {
            'group': self.group.pk,
            'text': 'Отредактированный текст',
        }
        response = self.author_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[self.post.id]))
        self.assertTrue(
            Post.objects.filter(
                group=PostCreateFormTests.group,
                text='Отредактированный текст',
            ).exists()
        )
        self.assertEqual(Post.objects.count(), tasks_count)
