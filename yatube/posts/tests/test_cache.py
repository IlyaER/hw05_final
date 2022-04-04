import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEST_CACHE_SETTING = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


class CacheTests(TestCase):

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
            text='Тестовый пост 1',
            group=cls.group,
        )
        cls.views = {
            'posts:index':
                'posts/index.html'}

    def setUp(self):
        self.guest_client = Client()

    #@override_settings(CACHES=TEST_CACHE_SETTING)
    def test_cache_index(self):
        """Проверка кеширования главной страницы."""
        posts_count = Post.objects.count()
        index_page_before = self.guest_client.get(reverse('posts:index')).content  # .content
        self.post.delete()
        index_page_cached = self.guest_client.get(reverse('posts:index')).content
        self.assertEqual(index_page_before, index_page_cached, 'Кеширование не работает')
        cache.clear()
        index_page_after = self.guest_client.get(reverse('posts:index')).content
        self.assertNotEqual(index_page_cached, index_page_after, 'Кеширование не работает')
