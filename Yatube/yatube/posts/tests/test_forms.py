import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, Comment, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Stas')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='3',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_new_in_db(self):
        """Тестирование на создание новой записи в БД"""
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
        form_data = {
            'text': 'Тестовый пост',
            'image': uploaded,
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.last()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.group, self.group)
        self.assertEqual(post_edit.author, PostCreateFormTest.user)
        self.assertEqual(post_edit.image.name, 'posts/small.gif')

    def test_post_edit(self):
        """Тестирование изменения поста после редактирования"""
        group = Group.objects.create(
            title='Тестовая',
            slug='2',
            description='abc'
        )
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        form_data = {
            'text': 'Абракадабра',
            'group': group.id,
            'image': self.uploaded
        }
        post = Post.objects.last()
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post.pk
                    }),
            data=form_data,
            follow=True
        )
        post_edit = Post.objects.last()
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.author, PostCreateFormTest.user)
        self.assertEqual(post_edit.group, group)
        self.assertEqual(post_edit.image.size, self.uploaded.size)

    def test_comment_added_on_post_page(self):
        """Комментарий созданный чрез форму появляется в БД"""
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        post = Post.objects.last()
        form_data = {
            'text': 'Текст',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={
                        'post_id': post.pk
                    }),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Comment.objects.filter(
                text='Текст',
                author=PostCreateFormTest.user,
            ).exists()
        )

    def test_post_commenting_by_authorized(self):
        """Комментирование недоступно анонимному пользователю"""
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        post = Post.objects.last()
        form_data = {
            'text': 'Текст2 не появится',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={
                        'post_id': post.pk
                    }),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Comment.objects.filter(
                text='Текст2 не появится',
                author=PostCreateFormTest.user,
            ).exists()
        )
