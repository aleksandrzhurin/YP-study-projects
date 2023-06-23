from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache
from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='123')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user2 = User.objects.create_user(username='stas')
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='3',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_home_url(self):
        """Testing homepage"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url(self):
        """Testing group page"""
        response = self.guest_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url(self):
        """Testing user profile"""
        response = self.guest_client.get(f'/profile/{self.user.username}/')
        self.assertEqual(response.status_code, 200)

    def test_post_url(self):
        """Testing post page"""
        response = self.guest_client.get(f'/posts/{self.post.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url(self):
        """Testing post edit by author"""
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_urls_correct(self):
        """Testing templates on correctly work"""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/dasfasd/': 'core/404.html',
        }
        cache.clear()
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_wrong_uri_returns_404(self):
        """Запрос к несуществующей странице вернёт ошибку 404."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_auth_user(self):
        """Создание поста доступно авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_noauthor_user(self):
        """Cтраница редактирования поста недоступна не-автору"""
        response = self.authorized_client2.get(f'/posts/{self.post.pk}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.pk}/')

    def test_anonim_user(self):
        """Create недоступна неавторизованному пользователю"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_anonim_user(self):
        """Edit недоступна неавторизованному пользователю"""
        response = self.guest_client.get(f'/posts/{self.post.pk}/edit/',
                                         follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.pk}/edit/'
        )
