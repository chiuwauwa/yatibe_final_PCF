from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class TestUrls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='1')
        cls.user_2 = User.objects.create_user(username='2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            pk=1,
            author=cls.user,
            text='Тестовая пост',
        )
        cls.guest_client = Client()

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.authorized_client_2 = Client()
        cls.authorized_client_2.force_login(cls.user_2)

    def runner(self, client, tests):
        for reverse_name, results in tests.items():
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = client.get(reverse_name)
                for (result_code, result) in results:
                    self.assertEqual(result_code, response.status_code)
                    if result_code == HTTPStatus.FOUND:
                        self.assertEqual(response['Location'], result)
                    else:
                        self.assertTemplateUsed(response, result)

    def test_guest(self):
        tests = {
            reverse('posts:index'): [
                (HTTPStatus.OK, 'posts/index.html')
            ],
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}): [
                (HTTPStatus.OK, 'posts/group_list.html')
            ],
            reverse('posts:profile', kwargs={'username': '1'}): [
                (HTTPStatus.OK, 'posts/profile.html')
            ],
            reverse('posts:post_detail', kwargs={'post_id': '1'}): [
                (HTTPStatus.OK, 'posts/posts_detail.html')
            ],
            reverse('posts:post_edit', kwargs={'post_id': '1'}): [
                (HTTPStatus.FOUND, '/auth/login/?next=/posts/1/edit/')
            ],
            reverse('posts:post_create'): [
                (HTTPStatus.FOUND, '/auth/login/?next=/create/')
            ],
            '/undefined/': [
                (HTTPStatus.NOT_FOUND, 'core/404.html')
            ],
            reverse('posts:follow_index'): [
                (HTTPStatus.FOUND, '/auth/login/?next=/follow/')
            ]
        }
        self.runner(self.guest_client, tests)

    def test_authorized(self):
        tests = {
            reverse('posts:index'): [
                (HTTPStatus.OK, 'posts/index.html')
            ],
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}): [
                (HTTPStatus.OK, 'posts/group_list.html')
            ],
            reverse('posts:profile', kwargs={'username': '1'}): [
                (HTTPStatus.OK, 'posts/profile.html')
            ],
            reverse('posts:post_detail', kwargs={'post_id': '1'}): [
                (HTTPStatus.OK, 'posts/posts_detail.html')
            ],
            reverse('posts:post_edit', kwargs={'post_id': '1'}): [
                (HTTPStatus.OK, 'posts/create_post.html')
            ],
            reverse('posts:post_create'): [
                (HTTPStatus.OK, 'posts/create_post.html')
            ],
            '/undefined/': [
                (HTTPStatus.NOT_FOUND, 'core/404.html')
            ],
            reverse('posts:follow_index'): [
                (HTTPStatus.OK, 'posts/follow.html')
            ]
        }
        self.runner(self.authorized_client, tests)

    def test_authorized_2(self):
        tests = {
            reverse('posts:index'): [
                (HTTPStatus.OK, 'posts/index.html')
            ],
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}): [
                (HTTPStatus.OK, 'posts/group_list.html')
            ],
            reverse('posts:profile', kwargs={'username': '1'}): [
                (HTTPStatus.OK, 'posts/profile.html')
            ],
            reverse('posts:post_detail', kwargs={'post_id': '1'}): [
                (HTTPStatus.OK, 'posts/posts_detail.html')
            ],
            reverse('posts:post_edit', kwargs={'post_id': '1'}): [
                (HTTPStatus.FOUND, reverse('posts:post_detail',
                                           kwargs={'post_id': '1'}))
            ],
            reverse('posts:post_create'): [
                (HTTPStatus.OK, 'posts/create_post.html')
            ],
            '/undefined/': [
                (HTTPStatus.NOT_FOUND, 'core/404.html')
            ],
            reverse('posts:follow_index'): [
                (HTTPStatus.OK, 'posts/follow.html')
            ]
        }
        self.runner(self.authorized_client_2, tests)
