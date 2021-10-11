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
        post = Post.objects.last()
        context = {'username': self.user.username}
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs=context))
        self.assertEqual(Post.objects.count(), count_post + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user, 'Author')

    def test_change_post(self):
        form_data_new = {
            'text': 'Изменили текст'
        }
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data_new,
        )

        self.assertEqual(Post.objects.last().text,
                         form_data_new['text'])

    def test_add_comment(self):
        text_comment = "Test comment"
        form_comment = {
            'text': text_comment
        }
        post = Post.objects.create(
            text='Test text',
            author=self.user
        )
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.pk}),
            data=form_comment
        )
        self.assertEqual(post.comments.last().text, text_comment)
