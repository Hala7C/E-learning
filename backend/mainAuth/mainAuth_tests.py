"""
TDD suite for the mainAuth app: registration, login, 2FA, logout,
and admin-only endpoints.

Run with:  python manage.py test mainAuth

These tests describe the *intended* contract. A few will fail against
the code as currently written until the accompanying fixes are applied:

  - services.getLoginUserService is unsafe/broken (see
    LegacyLoginServiceIsUnsafeTests) and should be deleted or replaced
    with django.contrib.auth.authenticate().
  - UserRegistrationSerializer.to_representation silently returns None
    when no Trainer exists yet.
"""
from unittest.mock import MagicMock

import pyotp
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from mainAuth.models import CustomUser


def ensure_default_groups():
    """
    The post_save signal in mainAuth/signals.py does
    Group.objects.get(name="Student") unconditionally, so every test
    that creates a user needs this group to exist first or user
    creation raises Group.DoesNotExist. Centralized here so the
    fixture requirement lives in one place instead of every setUp().
    """
    Group.objects.get_or_create(name="Student")


class RegistrationTests(APITestCase):
    def setUp(self):
        ensure_default_groups()

    def test_register_creates_user_and_assigns_student_group(self):
        payload = {
            "email": "student@example.com",
            "password": "StrongPass1!",
            "re_password": "StrongPass1!",
            "first_name": "Ada",
            "last_name": "Lovelace",
        }
        response = self.client.post("/auth/users/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        user = CustomUser.objects.get(email="student@example.com")
        self.assertTrue(user.groups.filter(name="Student").exists())
        self.assertTrue(hasattr(user, "student_profile"))

    def test_register_rejects_weak_password(self):
        payload = {
            "email": "weak@example.com",
            "password": "weak",
            "re_password": "weak",
            "first_name": "A",
            "last_name": "B",
        }
        response = self.client.post("/auth/users/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(CustomUser.objects.filter(email="weak@example.com").exists())

    def test_register_mismatched_passwords_rejected(self):
        payload = {
            "email": "mismatch@example.com",
            "password": "StrongPass1!",
            "re_password": "Different1!",
            "first_name": "A",
            "last_name": "B",
        }
        response = self.client.post("/auth/users/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email_rejected(self):
        CustomUser.objects.create_user(
            email="dup@example.com", first_name="A", last_name="B", password="StrongPass1!"
        )
        payload = {
            "email": "dup@example.com",
            "password": "StrongPass1!",
            "re_password": "StrongPass1!",
            "first_name": "C",
            "last_name": "D",
        }
        response = self.client.post("/auth/users/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        ensure_default_groups()
        self.user = CustomUser.objects.create_user(
            email="login@example.com", first_name="A", last_name="B", password="StrongPass1!"
        )

    def test_login_with_correct_credentials_returns_token(self):
        response = self.client.post(
            "/auth/token/login/",
            {"email": "login@example.com", "password": "StrongPass1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("auth_token", response.data)

    def test_login_with_wrong_password_rejected(self):
        response = self.client.post(
            "/auth/token/login/",
            {"email": "login@example.com", "password": "WrongPass1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_unknown_email_rejected(self):
        response = self.client.post(
            "/auth/token/login/",
            {"email": "nobody@example.com", "password": "StrongPass1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LegacyLoginServiceIsUnsafeTests(TestCase):
    """
    Documents why mainAuth.services.getLoginUserService must not be
    wired into a view as-is: it filters on `username=` (CustomUser has
    no such field — USERNAME_FIELD is 'email') and compares the raw
    request password directly against the hashed `password` column, so
    it can never return a real match. It's currently unused by any URL;
    this test exists so nobody "fixes" the always-None return value by
    accidentally making it compare plaintext passwords.
    """

    def test_raw_password_never_matches_hashed_password(self):
        from mainAuth.services import getLoginUserService

        ensure_default_groups()
        CustomUser.objects.create_user(
            email="unsafe@example.com", first_name="A", last_name="B", password="StrongPass1!"
        )
        request = MagicMock()
        request.data = {"email": "unsafe@example.com", "password": "StrongPass1!"}
        self.assertIsNone(getLoginUserService(request))


class TwoFactorAuthTests(APITestCase):
    def setUp(self):
        ensure_default_groups()
        self.user = CustomUser.objects.create_user(
            email="twofa@example.com", first_name="A", last_name="B", password="StrongPass1!"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_set_2fa_requires_authentication(self):
        self.client.credentials()
        response = self.client.post("/en/api/admin/set-two-factor-auth/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_set_2fa_returns_qr_code_and_stores_secret(self):
        response = self.client.post("/en/api/admin/set-two-factor-auth/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("qr_code", response.data)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.otp_base32)

    def test_verify_2fa_with_correct_otp_succeeds_and_marks_logged_in(self):
        setup_response = self.client.post("/en/api/admin/set-two-factor-auth/")
        self.assertEqual(setup_response.status_code, status.HTTP_200_OK, setup_response.data)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.otp_base32, "2FA setup succeeded but otp_base32 was never saved.")
        otp = pyotp.TOTP(self.user.otp_base32).now()

        response = self.client.post(
            "/en/api/admin/verify-two-factor-auth/", {"otp": otp}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["otp_verified"])
        self.user.refresh_from_db()
        self.assertTrue(self.user.logged_in)

    def test_verify_2fa_with_wrong_otp_rejected(self):
        setup_response = self.client.post("/en/api/admin/set-two-factor-auth/")
        self.assertEqual(setup_response.status_code, status.HTTP_200_OK, setup_response.data)
        response = self.client.post(
            "/en/api/admin/verify-two-factor-auth/", {"otp": "000000"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_2fa_before_setup_rejected(self):
        response = self.client.post(
            "/en/api/admin/verify-two-factor-auth/", {"otp": "000000"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTests(APITestCase):
    def setUp(self):
        ensure_default_groups()
        self.user = CustomUser.objects.create_user(
            email="logout@example.com", first_name="A", last_name="B", password="StrongPass1!"
        )
        self.user.logged_in = True
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_token_destroy_clears_logged_in_flag(self):
        response = self.client.post("/auth/token/logout/")
        self.assertIn(response.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))
        self.user.refresh_from_db()
        self.assertFalse(self.user.logged_in)

    def test_token_destroy_requires_authentication(self):
        self.client.credentials()
        response = self.client.post("/auth/token/logout/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminOnlyEndpointsTests(APITestCase):
    def setUp(self):
        ensure_default_groups()
        self.admin_group, _ = Group.objects.get_or_create(name="Admin")
        self.regular_user = CustomUser.objects.create_user(
            email="regular@example.com", first_name="A", last_name="B", password="StrongPass1!"
        )
        self.admin_user = CustomUser.objects.create_user(
            email="admin@example.com", first_name="C", last_name="D", password="StrongPass1!"
        )
        self.admin_user.groups.add(self.admin_group)

    def _auth_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_non_admin_cannot_list_groups(self):
        self._auth_as(self.regular_user)
        response = self.client.get("/en/api/admin/groups/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_groups(self):
        self._auth_as(self.admin_user)
        response = self.client.get("/en/api/admin/groups/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_list_permissions(self):
        response = self.client.get("/en/api/admin/permissions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)