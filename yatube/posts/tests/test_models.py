from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='а'*30,
        )

    def setUp(self):
        self.guest_client = Client()

    def test_models_have_correct_object_names(self):
        post = PostModelTest.post
        text_post = str(post)
        self.assertEqual(text_post, post.text[:15])


class TestGroup(PostModelTest):
    def test_group(self):
        task_group = PostModelTest.group
        title_group = task_group.title
        self.assertEqual(title_group, task_group.title)

