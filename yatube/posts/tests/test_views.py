from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from ..models import Post, Group
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
from django.conf import settings

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.text = 'Тестовый для третьего задания'
        cls.slug = 'test'
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin')
        group = Group.objects.create(
            title='Тестовая группа',
            slug=cls.slug,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.text,
            group=group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
                                          kwargs={'username': self.user.username}),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': 'test'}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_list_context(self):
        resp = self.authorized_client.get(reverse('posts:group_list',
                                                  kwargs={'slug': 'test'}))
        self.assertContains(resp, "<img")
        self.assertEqual(resp.context.get('group').slug, self.slug, 'Group_list')

    def test_post_detail_context(self):
        response = self.authorized_client.get(reverse('posts:post_detail',
                                                      kwargs={'post_id': self.post.pk}))
        self.assertContains(response, "<img")
        self.assertEqual(response.context.get('post').text,
                         self.text, 'Post_detail')

    def chek_context(self, adress):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        response = self.authorized_client.get(adress)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_or_edit_context(self):
        adress_context = {
            'create': reverse('posts:post_create'),
            'edit': reverse('posts:post_edit',
                            kwargs={'post_id': self.post.pk}),
        }
        for variable, adress in adress_context.items():
            self.chek_context(adress)

    def test_profile_context(self):
        response = self.authorized_client.get(reverse('posts:profile',
                                                      kwargs={'username': 'admin'}))
        self.assertContains(response, "<img")


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test')
        group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=group,
            )
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def chek_equal(self, adress):
        response = self.client.get(adress)
        return len(response.context['page_obj'])

    def test_paginator(self):
        context = {'username': self.user.username}
        url_names = {
            reverse('posts:index'): 10,
            reverse('posts:index') + '?page=2': 3,
            reverse('posts:profile',
                    kwargs=context): 10,
            reverse('posts:profile',
                    kwargs=context) + '?page=2': 3,
            reverse('posts:group_list',
                    kwargs={'slug': 'test'}): 10,
        }
        for adress, count in url_names.items():
            amount = self.chek_equal(adress)
            self.assertEqual(amount, count)
