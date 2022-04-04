from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

        cls.urls = {
            reverse('posts:index'):
                [HTTPStatus.OK, HTTPStatus.OK],
            reverse('posts:group_posts', kwargs={'slug': cls.group.slug}):
                [HTTPStatus.OK, HTTPStatus.OK],
            reverse('posts:profile', kwargs={'username': cls.user}):
                [HTTPStatus.OK, HTTPStatus.OK],
            reverse('posts:post_detail', kwargs={'post_id': cls.post.id}):
                [HTTPStatus.OK, HTTPStatus.OK],
            reverse('posts:post_edit', kwargs={'post_id': cls.post.id}):
                [HTTPStatus.FOUND, HTTPStatus.OK],
            reverse('posts:post_create'):
                [HTTPStatus.FOUND, HTTPStatus.OK],
            '/unexisting_page/':
                [HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND],
        }

        cls.redirects = {
            reverse('posts:post_edit', kwargs={'post_id': cls.post.id}):
                f'/auth/login/?next=/posts/{cls.post.id}/edit/',
            reverse('posts:post_create'):
                '/auth/login/?next=/create/',
        }

        cls.templates = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': cls.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': cls.user}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': cls.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': cls.post.id}):
                'posts/create_post.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            '/unexisting_page/':
                '',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_at_desired_location_anon(self):
        """
        Проверка на доступность страниц
        для неавторизованного пользователя
        """
        for address, arg_list in self.urls.items():
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    arg_list[0],
                    f'Проблема с адресом {address}'
                )

    def test_redirects_for_anon(self):
        """
        Проверка на корректное перенаправление анонимного пользователя.
        """
        for address, arg_list in self.redirects.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow='True')
                self.assertRedirects(
                    response,
                    arg_list,
                    msg_prefix=f'Кривой редирект {arg_list}'
                )

    def test_url_at_desired_location_auth(self):
        """
        Проверка на доступность страниц
        для авторизованного пользователя
        """
        for address, arg_list in self.urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    arg_list[1],
                    f'Проблема с адресом {address}'
                )

    def test_url_uses_correct_template(self):
        """Проверка на корректные названия шаблонов"""
        for address, arg_list in self.templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                if arg_list:
                    self.assertTemplateUsed(
                        response,
                        arg_list,
                        f'Проблема с шаблоном {address}'
                    )
