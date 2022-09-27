import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )

        uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data={'text': 'Текст комментария'},
            follow=True,
        )
        self.comment = Comment.objects.first()

    def test_new_post_created_in_database(self):
        '''Проверка создания поста в базе данных.'''
        posts_count = Post.objects.count()

        uploaded = SimpleUploadedFile(
            name='small.gif', content=self.small_gif, content_type='image/gif'
        )

        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text,
                         form_data['text'])
        self.assertEqual(post.author.username,
                         self.post.author.username)
        self.assertIsNone(post.group)
        self.assertTrue(
            Post.objects.filter(text=self.post.text, image=self.post.image)
                .exists()
        )

    def test_post_edited_in_database(self):
        '''Проверка редактирования поста в базе данных.'''
        posts_count = Post.objects.count()

        uploaded = SimpleUploadedFile(
            name='small.gif', content=self.small_gif, content_type='image/gif'
        )

        post_id = self.post.pk
        form_data_edited = {
            'text': 'Отредактированный текст для теста',
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_data_edited,
            follow=True
        )
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text=form_data_edited.get('text')).exists())
        self.assertNotEqual(post.text,
                            self.post.text)
        self.assertEqual(post.author.username,
                         self.post.author.username)

    def test_new_comment_created_in_database(self):
        '''Проверка создания комментария в базе данных.'''
        comment_count = Comment.objects.count()
        post_id = self.post.pk
        form_comment = {'text': 'Текст комментария'}
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_comment,
            follow=True,
        )
        comment = Comment.objects.first()
        self.assertEqual(comment.text, self.comment.text)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_new_comment_not_created_in_database(self):
        '''у guest_client не должно быть возможности комментировать.'''
        comment_count = Comment.objects.count()
        post_id = self.post.pk
        form_comment = {
            'text': 'Текст комментария',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_comment,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count)
