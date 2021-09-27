from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post

User = get_user_model()


class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        count_post = Post.objects.count()
        form_data = {
            'text': 'Тестовый Пост'
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        context = {'username': self.user.username}
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs=context))
        self.assertEqual(Post.objects.count(), count_post+1)
        self.assertEqual(Post.objects.get(pk=1).text, form_data['text'])

    def test_change_post(self):
        form_data = {
            'text': 'Тестовый Пост'
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
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
        self.assertNotEqual(Post.objects.get(pk=1).text, form_data['text'])
