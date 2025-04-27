from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from social.models import Profile
from social.serializers import ProfileListSerializer, ProfileSerializer

PROFILES_URL = reverse("social:profile-list")


def create_temp_user():
    user = get_user_model().objects.create_user(
        email="user_temp@social.com",
        password="1qazcde3",
        first_name="user_temp_name",
        last_name="user_temp_surname",
    )
    return user


def get_profile_detail_url(profile_id):
    return reverse("social:profile-detail", args=[profile_id])


class UnauthorizedUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_profile_list(self):
        res = self.client.get(PROFILES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_detail(self):
        url = get_profile_detail_url(1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = get_user_model().objects.create_user(
            email="user_1@social.com",
            password="1qazcde3",
            first_name="user_1_name",
            last_name="user_1_surname",
        )
        cls.user_2 = get_user_model().objects.create_user(
            email="user_2@social.com",
            password="1qazcde3",
            first_name="user_2_name",
            last_name="user_2_surname",
        )
        cls.user_3 = get_user_model().objects.create_user(
            email="user_3@social.com",
            password="1qazcde3",
            first_name="user_3_name",
            last_name="user_3_surname",
        )
        cls.profile_1 = Profile.objects.create(
            user=cls.user_1, country="USA", city="Boston"
        )
        cls.profile_2 = Profile.objects.create(
            user=cls.user_2, country="Ukraine", city="Kyiv"
        )
        cls.profile_3 = Profile.objects.create(
            user=cls.user_3, country="Poland", city="Wroclaw"
        )


class AuthorizedUserTests(ProfileAPITestCase):
    def setUp(self):
        self.user_temp = create_temp_user()
        self.profile_temp = Profile.objects.create(user=self.user_temp)

        self.client = APIClient()
        self.test_user = get_user_model().objects.create_user(
            email="user@test.com",
            password="1qazcde3",
            first_name="test_name",
            last_name="test_surname",
        )
        self.client.force_authenticate(user=self.test_user)

    def test_profile_list(self):
        """Test that authorized users have access profile list"""
        res = self.client.get(PROFILES_URL)
        profiles = Profile.objects.all()
        serializer = ProfileListSerializer(profiles, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_profile_operation(self):
        """Test that authorized users can create/update/delete their profile"""
        # try to create profile
        res = self.client.post(PROFILES_URL, data=None)
        profile = Profile.objects.get(pk=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.test_user.profile, profile)

        # try to create profile twice
        res = self.client.post(PROFILES_URL, data=None)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # try to get own profile
        url = get_profile_detail_url(profile.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # try to update own profile
        payload = {
            "bio": "Test Bio",
            "country": "Test Country",
            "city": "Test City",
        }
        res = self.client.patch(url, payload)
        profile = Profile.objects.get(pk=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key in payload:
            self.assertEqual(payload[key], getattr(profile, key))

        # try to delete own profile
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_profile_filtering(self):
        """Test filtering by user full name, country and city"""
        res = self.client.get(PROFILES_URL + "?country=US")
        profiles = Profile.objects.filter(country__icontains="US")
        serializer = ProfileListSerializer(profiles, many=True)

        serialized_user_1 = ProfileListSerializer(self.user_1.profile).data
        serialized_user_2 = ProfileListSerializer(self.user_2.profile).data
        serialized_user_3 = ProfileListSerializer(self.user_3.profile).data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertIn(serialized_user_1, res.data)
        self.assertNotIn(serialized_user_2, res.data)
        self.assertNotIn(serialized_user_3, res.data)

        res = self.client.get(PROFILES_URL + "?city=Kyiv")
        profiles = Profile.objects.filter(city__icontains="Kyiv")
        serializer = ProfileListSerializer(profiles, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertNotIn(serialized_user_1, res.data)
        self.assertIn(serialized_user_2, res.data)
        self.assertNotIn(serialized_user_3, res.data)

        res = self.client.get(PROFILES_URL + "?name=user_3")
        profiles = Profile.objects.filter(
            Q(user__first_name__icontains="user_3")
            | Q(user__last_name__icontains="user_3")
        )
        serializer = ProfileListSerializer(profiles, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertNotIn(serialized_user_1, res.data)
        self.assertNotIn(serialized_user_2, res.data)
        self.assertIn(serialized_user_3, res.data)

    def test_profile_detail(self):
        """Test that user can get any profile but update/delete is forbidden"""
        # try to get another user profile
        url = get_profile_detail_url(self.profile_temp.id)
        res = self.client.get(url)
        serializer = ProfileSerializer(self.profile_temp)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

        # try to update another user profile
        payload = {
            "bio": "Test Bio",
            "country": "Test Country",
            "city": "Test City",
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # try to delete another user profile
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_following(self):
        """Test that users can follow and unfollow other users"""
        # try to follow user without created profile
        url = get_profile_detail_url(self.profile_temp.id) + "follow/"
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # try to create profile
        profile = Profile.objects.create(user=self.test_user)
        profile.save()

        # try to follow with profile
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # try to follow again the same user
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # check if user in followers
        url = get_profile_detail_url(self.profile_temp.id) + "followers/"
        res = self.client.get(url)
        followers = self.profile_temp.followers.all()
        follower_profiles = [f.follower for f in followers]

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(profile, follower_profiles)

        # check if temp_user in followings
        url = get_profile_detail_url(self.test_user.id) + "following/"
        res = self.client.get(url)
        followings = profile.following.all()
        followed_profiles = [f.following for f in followings]

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(self.profile_temp, followed_profiles)

        # try to follow by yourself
        url = get_profile_detail_url(self.test_user.id) + "follow/"
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # try to unfollow user
        url = get_profile_detail_url(self.profile_temp.id) + "unfollow/"
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # try to unfollow again
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # check if user in followers
        url = get_profile_detail_url(self.profile_temp.id) + "followers/"
        res = self.client.get(url)
        followers = self.profile_temp.followers.all()
        follower_profiles = [f.follower for f in followers]

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(profile, follower_profiles)

        # check if temp_user in followings
        url = get_profile_detail_url(self.test_user.id) + "following/"
        res = self.client.get(url)
        followings = profile.following.all()
        followed_profiles = [f.following for f in followings]

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.profile_temp, followed_profiles)


class AdminUserTest(TestCase):
    def setUp(self):
        self.user_temp = create_temp_user()
        self.profile_temp = Profile.objects.create(user=self.user_temp)

        self.client = APIClient()
        self.test_admin = get_user_model().objects.create_user(
            email="admin@test.com",
            password="1qazcde3",
            first_name="admin_name",
            last_name="admin_surname",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.test_admin)

    def test_profile_admin_access(self):
        """Test that admin can't change users profile, but can delete them"""
        # try to update user's data
        url = get_profile_detail_url(self.profile_temp.id)
        payload = {
            "bio": "Test Bio",
            "country": "Test Country",
            "city": "Test City",
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # try to delete user profile
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
