from django.test import TestCase

from ..models import Group, Post, User, QTY_POST_TEXT


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовая пост Тестовая пост Тестовая пост',
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(self.post.text[:QTY_POST_TEXT], str(self.post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual("Тестовая группа", str(self.group))
