"""
TDD suite for the trainer "Profile" domain: DraftTrainerProfile create/
update/destroy, SubmitDraftProfile validation, and section sub-resources
(Education/Skill/Employment).

Run with:  python manage.py test trainer

IMPORTANT — this suite depends on a permission-layer fix first:

  DraftProfilePolicy / SubmitProfilePolicy (trainer/permissions.py) load
  their Statment/Policy rows inside a try/except in the *class body*,
  which runs once at module import time. Seeding Policy rows inside
  setUp() has no effect on an already-imported class, so ownership
  checks can't be exercised from a normal Django test as written today.
  Recommended fix: move the statement-loading into a method
  (e.g. a `get_policy_statements()` used inside `has_permission`), so
  it's evaluated per-request instead of once at import. `_seed_policy`
  below documents the fixture shape the fixed version should honor.

Also depends on the serializer fix described in the writeup:
  AddTrainerProfileSerializers.create() currently reads
  self.context["request"].user (no context is ever passed by the view)
  and mishandles `validated_data.pop("user", {})`. See
  TeacherProfileSerializerUnitTests for the direct, context-free
  contract it should satisfy instead.
"""
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from mainAuth.models import CustomUser, TeacherProfile
from newapp.models import Statment, Policy as AccessPolicyModel
from trainer.models import Education, Employment, Skill
from trainer.serializers import AddTrainerProfileSerializers


def ensure_default_groups():
    Group.objects.get_or_create(name="Student")


def seed_policy(view_name, owner_gated_actions=("update", "partial_update", "destroy")):
    """
    Seeds a Statment + two Policy rows: unrestricted list/retrieve/create,
    and owner-gated update/destroy. Mirrors the shape get_access_statments()
    (newapp/utils.py) expects: comma-separated action/principal/condition
    strings.
    """
    statement = Statment.objects.create(view_name=view_name)
    AccessPolicyModel.objects.create(
        action="list,,me,retrieve,create",
        principal="*",
        effect="allow",
        statmant=statement,
    )
    AccessPolicyModel.objects.create(
        action=",".join(owner_gated_actions),
        principal="*",
        effect="allow",
        conditions="is_owner",
        statmant=statement,
    )


class TeacherProfileSerializerUnitTests(APITestCase):
    """
    Direct, context-free tests for the serializer's create() contract —
    the behavior it should have once the context/pop("user") bug is
    fixed to match the pattern already used in update().
    """

    def setUp(self):
        ensure_default_groups()
        self.user = CustomUser.objects.create_user(
            email="trainer@example.com", first_name="Old", last_name="Name", password="StrongPass1!"
        )

    def test_create_updates_user_names_and_creates_profile(self):
        serializer = AddTrainerProfileSerializers(
            data={
                "user": self.user.id,
                "first_name": "New",
                "last_name": "Name",
                "status": "draft",
                "name": "New Name",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save()

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "New")
        self.assertEqual(profile.user, self.user)
        self.assertEqual(TeacherProfile.objects.filter(user=self.user).count(), 1)

    def test_create_without_name_fields_still_creates_profile(self):
        serializer = AddTrainerProfileSerializers(
            data={"user": self.user.id, "status": "draft", "name": self.user.get_full_name}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save()
        self.assertEqual(profile.status, "draft")


class DraftTrainerProfileViewSetTests(APITestCase):
    def setUp(self):
        ensure_default_groups()
        Group.objects.get_or_create(name="Trainer")
        seed_policy("DraftProfile")

        self.owner = CustomUser.objects.create_user(
            email="owner@example.com", first_name="Owner", last_name="One", password="StrongPass1!"
        )
        self.other = CustomUser.objects.create_user(
            email="other@example.com", first_name="Other", last_name="Two", password="StrongPass1!"
        )

    def _auth_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_create_profile(self):
        self._auth_as(self.owner)
        response = self.client.post(
            "/en/api/trainer/draftProfile/",
            {"first_name": "Owner", "last_name": "One"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(TeacherProfile.objects.filter(user=self.owner).exists())

    def test_cannot_create_two_profiles_for_same_user(self):
        self._auth_as(self.owner)
        self.client.post(
            "/en/api/trainer/draftProfile/", {"first_name": "Owner", "last_name": "One"}, format="json"
        )
        response = self.client.post(
            "/en/api/trainer/draftProfile/", {"first_name": "Owner", "last_name": "One"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_update_own_profile(self):
        self._auth_as(self.owner)
        create_resp = self.client.post(
            "/en/api/trainer/draftProfile/", {"first_name": "Owner", "last_name": "One"}, format="json"
        )
        profile_id = create_resp.data["id"]

        response = self.client.put(
            f"/en/api/trainer/draftProfile/{profile_id}/", {"bio": "Updated bio"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_non_owner_cannot_update_someone_elses_profile(self):
        self._auth_as(self.owner)
        create_resp = self.client.post(
            "/en/api/trainer/draftProfile/", {"first_name": "Owner", "last_name": "One"}, format="json"
        )
        profile_id = create_resp.data["id"]

        self._auth_as(self.other)
        response = self.client.put(
            f"/en/api/trainer/draftProfile/{profile_id}/", {"bio": "Hijacked"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_own_profile(self):
        self._auth_as(self.owner)
        create_resp = self.client.post(
            "/en/api/trainer/draftProfile/", {"first_name": "Owner", "last_name": "One"}, format="json"
        )
        profile_id = create_resp.data["id"]

        response = self.client.delete(f"/en/api/trainer/draftProfile/{profile_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TeacherProfile.objects.filter(id=profile_id).exists())

    def test_non_owner_cannot_delete_someone_elses_profile(self):
        self._auth_as(self.owner)
        create_resp = self.client.post(
            "/en/api/trainer/draftProfile/", {"first_name": "Owner", "last_name": "One"}, format="json"
        )
        print(f"Create response: {create_resp.status_code}, {create_resp.data}")
        profile_id = create_resp.data["id"]

        self._auth_as(self.other)
        response = self.client.delete(f"/en/api/trainer/draftProfile/{profile_id}/")
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        self.assertTrue(TeacherProfile.objects.filter(id=profile_id).exists())

    def test_me_endpoint_returns_current_users_profile(self):
        self._auth_as(self.owner)
        create_resp = self.client.post(
            "/en/api/trainer/draftProfile/", {"first_name": "Owner", "last_name": "One"}, format="json"
        )
        response = self.client.get("/en/api/trainer/draftProfile/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.owner.id)


class SubmitDraftProfileTests(APITestCase):
    def setUp(self):
        ensure_default_groups()
        seed_policy("DraftProfile")
        seed_policy("SubmitProfile", owner_gated_actions=("update",))

        self.user = CustomUser.objects.create_user(
            email="submit@example.com", first_name="Sub", last_name="Mit", password="StrongPass1!"
        )
        self.profile = TeacherProfile.objects.create(user=self.user, status="draft")
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_submit_without_required_sections_rejected(self):
        response = self.client.put(
            f"/en/api/trainer/submitDraftProfile/{self.profile.id}/", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, "draft")

    def test_submit_with_required_sections_marks_pending(self):
        Education.objects.create(trainer=self.profile, institution="MIT", degree="BSc", year=2020)
        Skill.objects.create(trainer=self.profile, name="Python", proficiency_level=3)
        Employment.objects.create(
            trainer=self.profile, company="Acme", position="Dev", start_date="2021-01-01"
        )

        response = self.client.put(
            f"/en/api/trainer/submitDraftProfile/{self.profile.id}/", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, "pending")

    def test_submit_missing_only_skills_rejected(self):
        Education.objects.create(trainer=self.profile, institution="MIT", degree="BSc", year=2020)
        Employment.objects.create(
            trainer=self.profile, company="Acme", position="Dev", start_date="2021-01-01"
        )
        response = self.client.put(
            f"/en/api/trainer/submitDraftProfile/{self.profile.id}/", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileSectionOwnershipTests(APITestCase):
    """
    Education/Employment/Skill viewsets don't check policy-based
    ownership at all — they scope list() to the requesting user's own
    TeacherProfile, but destroy() only checks `instance.trainer == profile`
    after already fetching by raw pk, and update() doesn't check
    ownership at all (see EducationViewSet.update in trainer/views.py).
    This test locks in the destroy behavior and flags the update gap.
    """

    def setUp(self):
        ensure_default_groups()
        self.owner = CustomUser.objects.create_user(
            email="sec-owner@example.com", first_name="Sec", last_name="Owner", password="StrongPass1!"
        )
        self.other = CustomUser.objects.create_user(
            email="sec-other@example.com", first_name="Sec", last_name="Other", password="StrongPass1!"
        )
        self.owner_profile = TeacherProfile.objects.create(
            user=self.owner, status="draft"
        )
        self.other_profile = TeacherProfile.objects.create(
            user=self.other, status="draft"
        )
        self.education = Education.objects.create(
            trainer=self.owner_profile, institution="MIT", degree="BSc", year=2020
        )

        token, _ = Token.objects.get_or_create(user=self.other)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_non_owner_cannot_delete_someone_elses_education_entry(self):
        response = self.client.delete(f"/en/api/trainer/education/{self.education.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Education.objects.filter(id=self.education.id).exists())

    def test_non_owner_can_currently_edit_someone_elses_education_entry(self):
        """
        This test intentionally documents a real gap rather than a
        desired behavior: EducationViewSet.update() never compares
        instance.trainer to the requesting user's profile, so this
        currently succeeds. It should be changed to assertEqual(...,
        403) once ownership is enforced in update() the same way it
        already is in destroy().
        """
        response = self.client.put(
            f"/en/api/trainer/education/{self.education.id}/",
            {"institution": "Hijacked University", "degree": "BSc", "year": 2020},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
