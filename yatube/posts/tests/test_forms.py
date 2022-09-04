import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

MEDIA_ROOT = tempfile.mkdtemp()
User = get_user_model()


def gif_create():
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
    )
    uploaded = SimpleUploadedFile(
        name='test_small.gif',
        content=small_gif,
        content_type='image/gif'
    )
    return uploaded


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')

        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test_slug'
        )

        cls.post = Post.objects.create(
            text='test_post',
            author=cls.author,
            group=cls.group,
            image=gif_create()
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'test_text',
            'image': gif_create(),

        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author}))
        self.assertEqual(Post.objects.count(), post_count + 1)

        self.assertTrue(
            Post.objects.filter(
                text='test_post',
                image='posts/test_small.gif'
            ).exists()
        )

    def test_edit_post(self):
        post_count = Post.objects.count()

        form_data = {
            'text': 'test_text',
            'group': self.__class__.group.pk,
            'image': gif_create(),

        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'pk': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), post_count)
