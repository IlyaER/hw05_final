import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 1',
            group=cls.group,
            image=uploaded,
        )
        cls.views = {
            'posts:index':
                ['posts/index.html', {}],
            'posts:group_posts':
                ['posts/group_list.html', {'slug': cls.group.slug}],
            'posts:profile':
                ['posts/profile.html', {'username': cls.user}],
            'posts:post_detail':
                ['posts/post_detail.html', {'post_id': cls.post.id}],
            'posts:post_edit':
                ['posts/create_post.html', {'post_id': cls.post.id}],
            'posts:post_create':
                ['posts/create_post.html', {}],
        }

        cls.index_views = {
            'posts:index': {},
            'posts:group_posts': {'slug': cls.group.slug},
            'posts:profile': {'username': cls.user},
        }

        cls.post_views = {
            'posts:post_edit': {'post_id': cls.post.id},
            'posts:post_create': {},
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_uses_correct_template(self):
        """Проверка правильных html-шаблонов."""
        for reversed, arg_list in self.views.items():
            with self.subTest():
                response = self.authorized_client.get(
                    reverse(
                        reversed,
                        kwargs=arg_list[1]
                    )
                )
                self.assertTemplateUsed(
                    response,
                    arg_list[0],
                    f'ашыпка в {response} {arg_list[0]}'
                )

    def test_post_index_page_context(self):
        """Проверка контекста общих страниц."""
        for reversed, arg_list in self.index_views.items():
            response = self.authorized_client.get(
                reverse(
                    reversed,
                    kwargs=arg_list
                )
            )
            first_object = response.context['page_obj'][0]
            context_objects = {
                self.post.author.id: first_object.author.id,
                self.post.text: first_object.text,
                self.group.slug: first_object.group.slug,
                self.post.id: first_object.id,
                self.post.image: first_object.image,
            }
            for reverse_name, response_name in context_objects.items():
                with self.subTest(reverse_name=reverse_name):
                    self.assertEqual(response_name, reverse_name)

    def test_post_detail_context(self):
        """Проверка контекста страницы поста."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(response.context['post'].pk, self.post.id)

    def test_post_create_context(self):
        """Проверка контекста страниц создания/редактирования поста."""
        for reversed, arg_list in self.post_views.items():
            response = self.authorized_client.get(
                reverse(
                    reversed,
                    kwargs=arg_list
                )
            )
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.models.ModelChoiceField,
                'image': forms.fields.ImageField
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    """Проверка паджинатора."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(1, 16):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            )

        cls.pag_views = {
            'posts:index': {},
            'posts:group_posts': {'slug': cls.group.slug},
            'posts:profile': {'username': cls.user},
        }

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        for reversed, arg_list in self.pag_views.items():
            with self.subTest():
                response = self.guest_client.get(reverse(
                    reversed,
                    kwargs=arg_list
                )
                )
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_less_records(self):
        for reversed, arg_list in self.pag_views.items():
            with self.subTest():
                response = self.guest_client.get(reverse(
                    reversed,
                    kwargs=arg_list
                ) + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 5)


class GroupViewsTests(TestCase):
    """Проверка на правильное отображение поста с группой"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Вторая Тестовая группа',
            slug='2nd-test-slug',
            description='Второе Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 1',
            group=cls.group
        )
        cls.another_post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 2',
            group=cls.another_group
        )
        cls.index_views = {
            'posts:index': {},
            'posts:group_posts': {'slug': cls.group.slug},
            'posts:profile': {'username': cls.user},
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_check_if_new_post_with_group_shown_on_pages(self):
        for reversed, arg_list in self.index_views.items():
            response = self.authorized_client.get(
                reverse(
                    reversed,
                    kwargs=arg_list
                )
            )
            for obj in response.context['page_obj']:
                if obj.group.slug == self.group.slug:
                    with self.subTest():
                        self.assertEqual(obj.group.slug, self.group.slug)

    def test_check_group_post_only_on_own_group_page(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.another_group.slug}
            )
        )
        self.assertNotEqual(
            response.context.get('page_obj')[0].group.slug,
            self.group.slug
        )
