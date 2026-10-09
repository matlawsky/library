from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from allauth.account.models import EmailAddress
from unittest.mock import patch


class AccountTests(TestCase):
    def test_signup_page(self):
        self.assertContains(self.client.get(reverse("account_signup")), "Sign up")
    def test_signup_post(self):
        response = self.client.post(reverse("account_signup"), {"username":"newreader", "email":"newreader@example.com", "password1":"Very-strong-pass-841", "password2":"Very-strong-pass-841"})
        self.assertEqual(response.status_code,302)
        self.assertTrue(get_user_model().objects.filter(username="newreader").exists())


class ProfileTests(TestCase):
    def test_anonymous_redirect(self):
        self.assertEqual(self.client.get(reverse("myaccount")).status_code,302)
    def test_profile_cannot_elevate(self):
        user = get_user_model().objects.create_user("reader","reader@example.com","testpass123")
        self.client.force_login(user)
        response = self.client.post(reverse("myaccount"),dict(username="renamed",first_name="A",last_name="B",is_staff=True,email="evil@example.com"))
        self.assertRedirects(response,reverse("myaccount"))
        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertEqual(user.email,"reader@example.com")


class EmailTests(TestCase):
    def test_new_email_is_not_automatically_verified(self):
        user = get_user_model().objects.create_user("reader","reader@example.com","Strong-pass-123")
        EmailAddress.objects.create(user=user,email=user.email,primary=True,verified=True)
        self.client.force_login(user)
        self.client.post(reverse("account_email"),{"email":"new@example.com","action_add":""})
        address = EmailAddress.objects.get(user=user,email="new@example.com")
        self.assertFalse(address.verified)
        user.refresh_from_db(); self.assertEqual(user.email,"reader@example.com")


class HealthTests(TestCase):
    def test_ready(self): self.assertEqual(self.client.get(reverse("health_ready")).status_code,200)
    def test_database_failure_is_503(self):
        with patch("library.health.connection.cursor",side_effect=RuntimeError("private error")):
            response=self.client.get(reverse("health_ready"))
        self.assertEqual(response.status_code,503)
        self.assertNotContains(response,"private error",status_code=503)


class CustomUserTest(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="test", email="test@email.com", password="testpass123"
        )
        self.assertEqual(user.username, "test")
        self.assertEqual(user.email, "test@email.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_staffuser(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="test_staff", email="test_staff@email.com", password="testpass123"
        )
        user.is_staff = True
        self.assertTrue(user.is_staff)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="superadmin", email="superadmin@email.com", password="testpass123"
        )
        self.assertEqual(admin_user.username, "superadmin")
        self.assertEqual(admin_user.email, "superadmin@email.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class SignupPageTests(TestCase):
    username = "newuser"
    email = "newuser@email.com"

    def setUp(self):
        url = reverse("account_signup")
        self.response = self.client.get(url)

    def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "account/signup.html")
        self.assertContains(self.response, "Sign up")
        self.assertNotContains(self.response, "It's not a correct page")

    def test_signup_form(self):
        new_user = get_user_model().objects.create_user(self.username, self.email)
        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(get_user_model().objects.all()[0].username, self.username)
        self.assertEqual(get_user_model().objects.all()[0].email, self.email)
