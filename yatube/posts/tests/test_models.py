from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
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
            text='Тестовый пост, длиной более пятнадцати символов',
        )

    def test_models_have_correct_object_names(self):
        """
        Проверка на правильное отображение поля __str__ в объектах моделей
        """
        post = PostModelTest.post
        group = PostModelTest.group

        str_names = {
            'group': 'Тестовая группа',
            'post': 'Тестовый пост, ',
        }
        self.assertEqual(group.title, str_names['group'])
        self.assertEqual(post.text[:15], str_names['post'])

    def test_verbose_names(self):
        post = PostModelTest.post
        field_verbose = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest():
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_names(self):
        post = PostModelTest.post
        field_help = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help.items():
            with self.subTest():
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
