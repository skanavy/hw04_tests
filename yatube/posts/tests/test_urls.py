from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
HTTPStatus.OK == 200
HTTPStatus.NOT_FOUND == 404


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='NoName')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test_slug'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        guest = [reverse('posts:index'),
                 reverse('posts:groups',
                         kwargs={'slug': self.group.slug}),
                 reverse('posts:profile',
                         kwargs={'username': self.author}),
                 reverse('posts:post_detail',
                         kwargs={'post_id': self.post.id})]
        for url in guest:
            self.assertEqual(
                self.guest_client.get(url).status_code, HTTPStatus.OK)
        authorized = [reverse('posts:post_create'),
                      reverse('posts:post_edit',
                              kwargs={'pk': self.post.id})]
        for url in authorized:
            self.assertEqual(
                self.authorized_client.get(url).status_code, HTTPStatus.OK)

    def test_wrong_uri_returns_404(self):
        response = self.client.get('/wrong/url/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница /post/<post_id>/edit/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(reverse(
            'posts:post_edit', kwargs={'pk': self.post.id}))
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/')

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/profile.html': f'/profile/{self.author}/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/create_post.html': '/create/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
