from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User, Comment


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группы',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.guest_client = Client()

        cls.user = User.objects.create_user(username='1')

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create(self):
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
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post = Post.objects.last()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)
        self.assertGreater(post.image.size, 0)

        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': response.context['page_obj'][0].pk})
        )
        self.assertEqual(response.context['post'].text, 'Данные из формы')

    def test_create_guest(self):
        form_data = {
            'text': 'Текст от гостя',
        }
        qty = Post.objects.count()
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(qty, Post.objects.count())
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0],
                         ('/auth/login/?next=/create/', HTTPStatus.FOUND))

    def test_edit(self):
        post = Post.objects.create(
            author=self.user,
            text='Step 1',
        )
        form_data = {
            'text': 'Специальный текст',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(pk=post.pk)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)

    def test_comment(self):
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text="Тестовый пост1",
        )
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True,
        )
        comment = Comment.objects.last()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, post)

    def test_comment_guest_client(self):
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text="Тестовый пост1",
        )
        form_data = {
            'text': 'Тестовый комментарий',
        }
        qty = Comment.objects.count()

        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.redirect_chain[0],
                         ('/auth/login/?next=/posts/1/comment/',
                          HTTPStatus.FOUND))
        self.assertEqual(qty, Comment.objects.count())
