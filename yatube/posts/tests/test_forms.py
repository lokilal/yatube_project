from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post
from ..forms import PostForm

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='NoName')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.form_data = {
            'text': 'Тестовый Пост'
        }
        self.response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
        )

    def test_create_post(self):
        self.assertRedirects(self.response, reverse('posts:profile',
                                                    kwargs={'username': 'NoName'}))
        self.assertEqual(Post.objects.count(), 1)

    def test_change_post(self):
        form_data_to_change = {
            'text': 'Изменил текст'
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data_to_change,
        )
        self.assertTrue(Post.objects.filter(
            text='Изменил текст',
        ).exists())
