import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Post, Group, Follow, User
from django.core.cache import cache


User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='Stas')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='3',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URLs используют правильный шаблон"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args={self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    args={self.user.username}): 'posts/profile.html',
            reverse('posts:post_detail',
                    args={self.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    args={self.post.pk}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        cache.clear()
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_detail_context(self):
        """Тестирование контекста поста"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args={self.post.pk}))
        first_object = response.context['post']
        self.assertEqual(first_object.text, PostPagesTest.post.text)
        self.assertEqual(first_object.author, PostPagesTest.user)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.image, PostPagesTest.post.image)

    def test_post_edit_context(self):
        """Тестирование контекста изменения поста"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args={self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        first_object = response.context['is_edit']
        self.assertEqual(first_object, True)

    def test_post_create_context(self):
        """"Тестирование контекста создания поста"""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        cache.clear()
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_pages_after_post_create(self):
        """Тестирование контекста после создания поста"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args={self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    args={PostPagesTest.user}): 'posts/profile.html',
        }
        cache.clear()
        for reversed_names in templates_pages_names.keys():
            with self.subTest(reversed_names=reversed_names):
                response = self.authorized_client.get(reversed_names)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.text, self.post.text)
                self.assertEqual(first_object.author, PostPagesTest.user)
                self.assertEqual(first_object.group, self.group)
                self.assertEqual(first_object.image, PostPagesTest.post.image)

    def test_post_another_group(self):
        """Пост не попал в сторонюю группу"""
        post = Post.objects.create(
            author=PostPagesTest.user,
            text='Тестовый пост',
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', args={self.group.slug})
        )
        self.assertNotIn(post.text, response)

    def test_cache(self):
        """Тестирование кеширования главной страницы"""
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        Post.objects.create(
            author=self.user,
            text='Test'
        )
        response_edit = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response.content, response_edit.content)
        cache.clear()
        response_after = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(response_edit.content, response_after)


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug='test-slug',
            description='Тестовое описание',
        )
        for post in range(13):
            cls.post = Post.objects.create(
                text='Тестовый пост',
                author=cls.user,
                group=cls.group
            )

    def test_first_page_contains_ten_posts(self):
        """Количество постов на первой странице 10"""
        namespace_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        count_posts = 10
        for reverse_name in namespace_list:
            response = self.guest_client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), count_posts)

    def test_second_page_contains_ten_posts(self):
        """Количество постов на второй странице 3"""
        namespace_list = [
            reverse('posts:index') + "?page=2",
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + "?page=2",
            reverse('posts:profile',
                    kwargs={'username': self.user.username}) + "?page=2",
        ]
        count_posts = 3
        for reverse_name in namespace_list:
            response = self.guest_client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), count_posts)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Stas')
        cls.user2 = User.objects.create_user(username='Slava')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)

    def test_authorized_client_follow(self):
        """Авторизованный пользователь может подписываться"""
        self.assertFalse(Follow.objects.filter(
            user=self.user2,
            author=self.user
        ).exists())
        self.authorized_client2.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        self.assertTrue(Follow.objects.filter(
            user=self.user2,
            author=self.user
        ))

    def test_auth_client_unfollow(self):
        """Авторизованный пользователь может отписываться"""
        Follow.objects.create(
            user=self.user2,
            author=self.user
        )
        self.authorized_client2.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.user})
        )
        self.assertFalse(Follow.objects.filter(
            user=self.user2,
            author=self.user
        ).exists())

    def test_subscribe_posts(self):
        """Появление записи в ленте подписчиков"""
        Follow.objects.create(
            user=self.user2,
            author=self.user
        )
        post = Post.objects.create(
            author=self.user,
            text='Test',
        )
        response = self.authorized_client2.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(post, response.context['page_obj'][0])

    def test_nonsubscribe_posts(self):
        """Поста нет у не-подписчика"""
        self.assertFalse(Follow.objects.filter(
            user=self.user2,
            author=self.user
        ))
        post = Post.objects.create(
            author=self.user,
            text='Test2'
        )
        response = self.authorized_client2.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(post, response.context['page_obj'])
