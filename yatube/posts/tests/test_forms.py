from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from ..forms import PostForm
from ..models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestAuthor')
        cls.test_group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test_slug',
        )
        cls.form = PostForm()
        cls.post = Post.objects.create(
            author=cls.user,
            text='Описание поста',
            group=cls.test_group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create_form(self):
        posts_count = Post.objects.count()
        post = Post.delete(self.post)
        form_data = {
            'text': 'Текст поста',
            'group': self.test_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group_id, form_data['group'])

    def test_authorized_user_edit_post(self):
        new_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug2'
        )
        form_data = {
            'text': 'post_text',
            'group': new_group.id
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        post = Post.objects.first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        self.assertTrue(post.text == form_data['text'])
        self.assertTrue(post.author == self.user)
        self.assertTrue(post.group_id == form_data['group'])

    def test_guest_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.test_group.id,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:post_create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)
