from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post, Group

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.user.username}),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
        access = {
            reverse('posts:index'): 200,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk}): 200,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): 200,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 200,
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.pk}): 302,
            reverse('posts:follow_index'): 302
        }

        for adress, code in access.items():
            with self.subTest(code=code):
                resp = self.guest_client.get(adress)
                self.assertEqual(resp.status_code, code, f'Problem {adress}')
