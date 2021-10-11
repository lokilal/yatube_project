from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from ..models import Post, Group, Comment, Follow
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
from django.conf import settings

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = 'Тестовый текст'
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin')
        cls.user_follow = User.objects.create_user(username='lokilal')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.text,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=cls.text,
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.post.author,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def context_page_test(self, test_post):
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.group.id, self.group.id)
        self.assertEqual(test_post.image, self.post.image)

    def test_pages_uses_correct_template(self):
        post_id = self.post.pk
        user = self.user.username
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              kwargs={'post_id': post_id}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': user}),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': self.group.slug}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_list_context(self):
        resp = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.context_page_test(resp.context['page_obj'][0])

    def test_post_detail_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.context_page_test(response.context['post'])
        self.assertEqual(response.context['comments'][0].text,
                         self.text, 'Comment')

    def test_post_create_or_edit_context(self):
        adress_context = [reverse('posts:post_create'),
                          reverse('posts:post_edit',
                                  kwargs={'post_id': self.post.pk}),
                          ]
        for adress in adress_context:
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            response = self.authorized_client.get(adress)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_profile_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['profile'], self.user, 'Profile')
        self.context_page_test(response.context['page_obj'][0])

    def test_index_page_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.context_page_test(response.context['page_obj'][0])

    def test_profile_follow(self):
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={
                        'username': self.user.username
                    }))
        self.assertEqual(self.user.follower.count(), Follow.objects.count())

    def test_profile_unfollow(self):
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={
                        'username': self.user.username
                    }))
        self.assertEqual(self.user.follower.count(), Follow.objects.count())

    def test_switcher_page_contains_post(self):
        follower = self.authorized_client.get(reverse(
            'posts:follow_index'
        ))
        self.assertEqual(follower.context['page_obj'][0], self.post)

    def test_switcher_for_unfollower(self):
        unfollower = self.guest_client.get(reverse(
            'posts:follow_index'))
        follower = self.authorized_client.get(reverse(
            'posts:follow_index'
        ))
        self.assertNotEqual(unfollower, follower)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test')
        cls.slug = 'test'
        group = Group.objects.create(
            title='Тестовая группа',
            slug=cls.slug,
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
                    kwargs={'slug': self.slug}): 10,
            reverse('posts:group_list',
                    kwargs={'slug': self.slug}) + '?page=2': 3,
        }
        for adress, count in url_names.items():
            response = self.client.get(adress)
            amount = len(response.context['page_obj'])
            self.assertEqual(amount, count)
