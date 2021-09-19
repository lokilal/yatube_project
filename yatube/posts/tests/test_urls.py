from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin')
        Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )
        Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/post_detail.html': '/posts/1/',
            'posts/profile.html': f'/profile/{self.user}/',
            'posts/group_list.html': '/group/test/',
            'posts/create_post.html': '/create/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
        access = {
            '/': 200,
            '/posts/1/': 200,
            f'/profile/{self.user}/': 200,
            '/group/test/': 200,
        }
        for adress, code in access.items():
            with self.subTest(code=code):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, code, f'Problem{adress}')

    def access_authorized_client(self):
        response = self.authorized_client.get('create/')
        self.assertEqual(response.status_code, 200, 'Проблемы с авторизацией пользователя')

    def change_posts(self):
        response = self.user.get('posts/1/edit/')
        self.assertEqual(response.status_code, 200, 'Проблемы с изменением')


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
