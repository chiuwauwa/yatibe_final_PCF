from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from django.core.paginator import Paginator
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User, Follow
from yatube.settings import QTY_POST_TEST, QTY_POSTS_PAGE
from ..forms import PostForm


class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='1')
        cls.user2 = User.objects.create_user(username='2')

        cls.group = Group.objects.create(
            title='Тестовая группа1',
            slug='test_slug',
            description='Тестовое описание1',
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

        for i in range(QTY_POST_TEST - 2):
            if i % 2 != 0:
                Post.objects.create(
                    pk=i,
                    author=cls.user,
                    text='Тестовая пост1',
                    group=cls.group,
                )
                Post.objects.create(
                    pk=i + 1,
                    author=cls.user2,
                    text='Тестовый текст2',
                )

        cls.post = Post.objects.create(
            pk=QTY_POST_TEST - 1,
            author=cls.user,
            text='Тестовая пост1',
            group=cls.group,
            image=uploaded,
        )
        cls.post2 = Post.objects.create(
            pk=QTY_POST_TEST,
            author=cls.user2,
            text='Тестовый текст2',
        )

        cls.guest_client = Client()

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)

    def test_use_template(self):
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': '1'}): 'posts/create_post.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': '1'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'}): 'posts/posts_detail.html',
            '/undefined/': 'core/404.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_index(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), QTY_POSTS_PAGE)
        self.assertIsInstance(response.context['page_obj'].paginator,
                              Paginator)
        self.assertEqual(response.context['page_obj'][0].text,
                         self.post2.text)
        self.assertEqual(response.context['page_obj'][1].image,
                         self.post.image)

        response = self.authorized_client.get(reverse
                                              ('posts:index'), {'page': '2'})
        self.assertEqual(response.context['page_obj'][1].text,
                         self.post.text)

    def test_context_index_cache(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), QTY_POSTS_PAGE)
        self.assertEqual(response.context['page_obj'][0].text,
                         self.post2.text)
        post = Post.objects.create(
            pk=QTY_POST_TEST + 1,
            author=self.user2,
            text='Тестирование кеша',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIsNone(response.context)
        self.assertNotContains(response, 'Тестирование кеша')

        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'][0].text, post.text)

        post.delete()

        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIsNone(response.context)
        self.assertContains(response, 'Тестирование кеша')

    def test_context_group(self):
        response = self.authorized_client.get(reverse
                                              ('posts:group_list',
                                               kwargs={'slug': 'test_slug'}))
        self.assertEqual(len(response.context['page_obj']), QTY_POST_TEST / 2)
        self.assertIsInstance(response.context['page_obj'].paginator,
                              Paginator)
        self.assertEqual(response.context['page_obj'][0].image,
                         self.post.image)
        self.assertEqual(response.context['page_obj'][0].text,
                         self.post.text)

    def test_context_profile(self):
        response = self.authorized_client.get(reverse
                                              ('posts:profile',
                                               kwargs={'username': '1'}))
        self.assertEqual(len(response.context['page_obj']), QTY_POST_TEST / 2)
        self.assertIsInstance(response.context['page_obj'].paginator,
                              Paginator)
        self.assertEqual(response.context['page_obj'][0].image,
                         self.post.image)
        self.assertEqual(response.context['page_obj'][0].text,
                         self.post.text)

    def test_context_detail(self):
        response = self.authorized_client.get(reverse('posts:post_detail',
                                                      kwargs={'post_id': '1'}))
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertTrue(response.context['can_edit'])

        response = self.guest_client.get(reverse('posts:post_detail',
                                                 kwargs={'post_id': '1'}))
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertFalse(response.context['post'].image)
        self.assertFalse(response.context['can_edit'])

    def test_context_edit(self):
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id': '1'}))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertTrue(response.context['is_edit'])

    def test_context_create(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertNotIn("is_edit", response.context.keys())

    def test_follow_unfollow(self):
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.user2
        ).exists())

        self.authorized_client.get(reverse('posts:profile_follow',
                                   kwargs={'username': '2'}))
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=self.user2
        ).exists())
        self.assertFalse(Follow.objects.filter(
            user=self.user2,
            author=self.user,
        ).exists())

        self.authorized_client.get(reverse('posts:profile_unfollow',
                                   kwargs={'username': '2'}))
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.user2
        ).exists())

        response = self.guest_client.get(reverse('posts:profile_follow',
                                                 kwargs={'username': '2'}))
        self.assertEqual(response['Location'],
                         '/auth/login/?next=/profile/2/follow/')

        response = self.guest_client.get(reverse('posts:profile_unfollow',
                                         kwargs={'username': '2'}))
        self.assertEqual(response['Location'],
                         '/auth/login/?next=/profile/2/unfollow/')

    def test_follow_page(self):
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)

        response = self.authorized_client2.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)

        self.authorized_client.get(reverse('posts:profile_follow',
                                   kwargs={'username': '2'}))

        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 8)

        response = self.authorized_client2.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_404(self):
        response = self.guest_client.get('/undefined/')
        self.assertTemplateUsed(response, 'core/404.html')
