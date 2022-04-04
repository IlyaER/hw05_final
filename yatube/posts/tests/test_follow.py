from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, User


class FollowTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_follower = User.objects.create_user(username='user follower')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 1',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_follower)

    def test_auth_user_follow_unfollow(self):
        not_followed_posts = Post.objects.filter(
            author__following__user=self.user_follower
        ).count()
        follow_user = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        self.assertRedirects(
            follow_user,
            reverse('posts:follow_index'),
            msg_prefix='Авторизация не работает'
        )
        followed_posts = Post.objects.filter(
            author__following__user=self.user_follower
        ).count()
        self.assertEqual(
            not_followed_posts + 1,
            followed_posts,
            'Подписка на автора не работает'
        )
        unfollow_user = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user}
            )
        )
        self.assertRedirects(
            unfollow_user,
            reverse('posts:follow_index'),
            msg_prefix='Отписка не работает'
        )
        unfollowed_posts = Post.objects.filter(
            author__following__user=self.user_follower
        ).count()
        self.assertEqual(
            not_followed_posts,
            unfollowed_posts,
            'Отписка от автора не работает'
        )
