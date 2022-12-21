from django import forms

from django.test import Client, TestCase
from django.shortcuts import get_object_or_404

from django.urls import reverse
from posts.models import Group, Post, User

from django.conf import settings


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='test-slug',
            description='тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def show(self, response, post=False):
        if post is True:
            response.context.get('post'), post
        else:
            response.context.get('post'), self.post

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        for post in Post.objects.select_related('group'):
            self.assertEqual(response.context.get('post'), post)

    def test_group_list_pages_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', args=(self.group.slug,))
        )
        group = get_object_or_404(Group, slug=self.group.slug)
        first_objects = group.posts.all()
        for post in first_objects:
            self.assertEqual(response.context.get('post'), post)
        second_object = response.context.get('page_obj').object_list
        for post in second_object:
            self.assertEqual(response.context.get('post'), post)

    def test_profile_pages_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            args=(self.user,))
        )
        author = self.user
        first_objects = author.posts.all()
        for post in first_objects:
            self.assertEqual(response.context.get('post'), post)
        second_object = response.context.get('page_obj').object_list
        for post in second_object:
            self.assertEqual(response.context.get('post'), post)

    def test_post_detail_pages_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            args=(self.post.pk,))
        )
        self.assertEqual(response.context.get('post'), self.post)

    def test_post_edit_show_correct_context(self):
        response = (self.authorized_client.get(reverse(
            'posts:post_edit', args=(self.post.pk,)))
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_right_group_exists(self):
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        object = self.group.posts.filter(
            group=response.context.get('post').group
        )
        self.assertTrue(object.exists())
        response = self.authorized_client.get(reverse(
            'posts:group_list', args=(self.group.slug,))
        )
        object = self.group.posts.filter(
            group=response.context.get('post').group
        )
        self.assertTrue(object.exists())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='test-slug',
            description='тестовое описание группы'
        )
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=f'Тестовый текст{test}',
                    author=cls.user,
                    group=cls.group
                )
                for test in range(settings.TEST_OF_POST)
            ]
        )

    def test_first_page_contains(self):
        url_names = {
            reverse('posts:index'): settings.PAGE_LIMIT,
            reverse(
                'posts:group_list',
                args=(self.group.slug,)
            ): settings.PAGE_LIMIT,
            reverse(
                'posts:profile',
                args=[self.user]
            ): settings.PAGE_LIMIT,
        }
        for value, expected in url_names.items():
            with self.subTest(value=value):
                response = self.client.get(value + '?page=1')
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):
        url_names = {
            reverse(
                'posts:index'
            ): settings.PAGE_LIMIT_SECOND_PAGE,
            reverse(
                'posts:group_list',
                args=(self.group.slug,)
            ): settings.PAGE_LIMIT_SECOND_PAGE,
            reverse(
                'posts:profile',
                args=[self.user]
            ): settings.PAGE_LIMIT_SECOND_PAGE,
        }
        for value, expected in url_names.items():
            with self.subTest(value=value):
                response = self.client.get(value + '?page=2')
                self.assertEqual(len(response.context['page_obj']), expected)
