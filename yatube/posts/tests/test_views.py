from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post, Group
from django import forms

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin')
        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
            )
        group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=cls.user,
            text='Тестовый для третьего задания',
            group=group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              kwargs={'post_id': 1}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': self.user}),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': 'test'}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_list_context(self):
        response = self.authorized_client.get(reverse('posts:group_list',
                                                      kwargs={'slug': 'test'}))
        self.assertEqual(response.context.get('group').slug, 'test', 'Group_list')

    def test_post_detail_context(self):
        response = self.authorized_client.get(reverse('posts:post_detail',
                                                      kwargs={'post_id': '1'}))

        self.assertEqual(response.context.get('post').text,
                         'Тестовый пост', 'Post_detail')

    def test_create_post_context(self):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id': 1}))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TaskPagesTests):
    def test_index_first_paginator(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_paginator(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_profile_first_paginator(self):
        response = self.client.get(reverse('posts:profile',
                                           kwargs={'username': self.user}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_paginator(self):
        context = {'username': self.user}
        response = self.client.get(reverse('posts:profile',
                                           kwargs=context) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_group_list_second_paginator(self):
        response = self.client.get(reverse('posts:group_list',
                                           kwargs={'slug': 'test'}))
        self.assertEqual(len(response.context['page_obj']), 1)
