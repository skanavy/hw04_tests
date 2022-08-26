from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse, reverse_lazy

from ..models import Group, Post

User = get_user_model()


class TaskCreateFormTests(TestCase):
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
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        post_count = Post.objects.count()

        form_data = {
            'text': 'test_text',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={'username': self.author}))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        post_count = Post.objects.count()

        form_data = {
            'text': 'test_text',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'pk': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), post_count)


