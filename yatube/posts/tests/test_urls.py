from http import HTTPStatus
from django.test import Client, TestCase
from posts.models import Group, Post, User
from django.urls import reverse


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='test-slug',
            description='тестовое описание группы'
        )

        cls.user_author = User.objects.create_user(
            username='user_author')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.unauthorized_user = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user)
        self.authorized_user = Client()

    def test_author_user_urls_status_code(self):
        field_urls = {
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                args=(self.group.slug,)): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                args=('bad_slug',)): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                args=(self.user_author,)): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                args=(self.post.id,)): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                args=(self.post.id,)): HTTPStatus.OK,
            reverse(
                'posts:post_create'): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, response_code in field_urls.items():
            with self.subTest(url=url):
                status_code = self.post_author.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_unauthorized_user_urls_status_code(self):
        field_urls = {
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                args=(self.group.slug,)): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                args=('bad_slug',)): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                args=(self.user_author,)): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                args=(self.post.id,)): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                args=(self.post.id,)): HTTPStatus.FOUND,
            reverse(
                'posts:post_create'): HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, response_code in field_urls.items():
            with self.subTest(url=url):
                status_code = self.unauthorized_user.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_authorized_user_urls_status_code(self):
        field_urls = {
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                args=(self.group.slug,)): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                args=('bad_slug',)): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                args=(self.user_author,)): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                args=(self.post.id,)): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                args=(self.post.id,)): HTTPStatus.FOUND,
        }
        for url, response_code in field_urls.items():
            with self.subTest(url=url):
                status_code = self.authorized_user.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            reverse(
                'posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                args=(self.group.slug,)): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=(self.user_author,)): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                args=(self.post.id,)): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                args=(self.post.id,)): 'posts/create_post.html',
            reverse(
                'posts:post_create'): 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.post_author.get(adress)
                self.assertTemplateUsed(response, template)
