import shutil
import tempfile
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from ..models import Group, Post, Comment
from .test_forms import gif_create
MEDIA_ROOT = tempfile.mkdtemp()
User = get_user_model()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TaskViewTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='StasBasov')
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
        cls.comment = Comment.objects.create(
            text='test_comment',
            author=cls.author,
            post=cls.post,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:groups', kwargs={'slug': self.group.slug}
                        ),
            'posts/post_detail.html': (
                reverse('posts:post_detail',
                        kwargs={'post_id': self.post.id})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': self.author})
            ),
            'posts/create_post.html': (
                reverse('posts:post_create')
            ),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def assert_post_response(self, response):
        """Проверяем Context"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        self.assert_post_response(response)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'pk': self.post.pk}))
        self.assert_post_response(response)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context['post'].text, 'test_post')
        self.assertEqual(response.context['post'].group, self.group)
        self.assertEqual(response.context['comments'][0].text, self.comment.text)

    def post_check(self, response):
        post = response.context['page_obj'][0]
        self.assertEqual(post.id, self.post.pk)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, self.post.image)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.post_check(response)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:groups', kwargs={'slug': self.group.slug})
        )
        group = response.context['group']
        self.assertEqual(group, self.group)
        self.post_check(response)

    def test_profile_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.author})
        )
        author = response.context['author']
        self.assertEqual(author, self.author)
        self.post_check(response)

    def test_index_page_list_eq_1(self):
        cache.clear()
        """На страницу index передаётся ожидаемое количество объектов."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get(
            'page_obj'
        ).object_list), 1)

    def test_group_page_list_eq_1(self):
        """На страницу group передаётся ожидаемое количество объектов."""
        response = self.authorized_client.get(
            reverse('posts:groups', kwargs={'slug': self.group.slug})
        )
        correct_post = response.context.get('page_obj').object_list[0]
        self.assertEqual(len(
            response.context.get('page_obj').object_list), 1)
        self.assertEqual(correct_post, self.post)

    def test_profile_page_list_eq_1(self):
        """На страницу profile передаётся ожидаемое количество объектов."""

        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.author})
        )
        correct_post = response.context.get('page_obj').object_list[0]
        self.assertEqual(
            len(response.context.get('page_obj').object_list), 1)
        self.assertEqual(correct_post, self.post)

    def test_cache_index(self):
        """Проверка очищения кэша на index."""
        response = self.guest_client.get(reverse('posts:index')).content
        Post.objects.create(
            text='test_new_post',
            author=self.author,
        )
        no_cache = self.guest_client.get(reverse('posts:index')).content
        self.assertEqual(response, no_cache, 'Количество постов отличается')
        cache.clear()
        cached = self.guest_client.get(reverse('posts:index')).content
        self.assertNotEqual(response, cached, 'Количество постов одинаково')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='StasBasov')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test-slug'
        )

    def setUp(self):
        posts = [
            Post(
                text=f'text{post}',
                author=self.author,
                group=self.group,
            )
            for post in range(13)
        ]
        Post.objects.bulk_create(posts)

    def test_first_page_contains_ten_records(self):
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), settings.MAX_POSTS)

    def test_second_page_contains_three_records(self):
        cache.clear()
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

