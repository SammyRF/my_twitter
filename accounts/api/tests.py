from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

BASE_URL = '/api/accounts/{}/'
LOGIN_URL = BASE_URL.format('login')
LOGOUT_URL = BASE_URL.format('logout')
SIGNUP_URL = BASE_URL.format('signup')
LOGIN_STATUS_URL = BASE_URL.format('login_status')

class AccountsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='admin',
            password='correct password',
            email='admin@admin.com'
        )

    def test_login(self):
        # test GET not allowed
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 405)

        # test with 'wrong password'
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # test failed login status
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # test with 'correct password'
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@admin.com')

        # test success login status
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # login first
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })

        # test login status
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # test logout with 'GET'
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # test logout
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # test login status
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        # test sign up with 'GET'
        response = self.client.get(SIGNUP_URL, {
            'username': 'guest',
            'password': 'guest',
            'email': 'guest@guest.com',
        })
        self.assertEqual(response.status_code, 405)

        # test wrong email
        response = self.client.post(SIGNUP_URL, {
            'username': 'guest',
            'password': 'guest',
            'email': 'wrong email',
        })
        self.assertEqual(response.status_code, 400)

        # test too short password
        response = self.client.post(SIGNUP_URL, {
            'username': 'guest',
            'password': 'pwd',
            'email': 'guest@guest.com',
        })
        self.assertEqual(response.status_code, 400)

        # test too long username
        response = self.client.post(SIGNUP_URL, {
            'username': 'user name is too long',
            'password': 'guest',
            'email': 'guest@guest.com',
        })
        self.assertEqual(response.status_code, 400)

        # sign up
        response = self.client.post(SIGNUP_URL, {
            'username': 'guest',
            'password': 'guest',
            'email': 'guest@guest.com',
        })
        self.assertEqual(response.status_code, 201)

        # test login status
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)