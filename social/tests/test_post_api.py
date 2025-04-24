from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from social.models import Profile, Post
from social.serializers import PostListSerializer, PostSerializer

POSTS_URL = reverse("social:post-list")


def get_post_detail_url(post_id):
    return reverse("social:post-detail", args=[post_id])


class UnauthorizedUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_profile_list(self):
        res = self.client.get(POSTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_detail(self):
        url = get_post_detail_url(1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PostAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_admin = get_user_model().objects.create_user(
            email="admin@social.com",
            password="1qazcde3",
            first_name="admin_name",
            last_name="admin_surname",
            is_staff=True,
        )
        cls.test_user = get_user_model().objects.create_user(
            email="test_user@social.com",
            password="1qazcde3",
            first_name="test_user_name",
            last_name="test_user_surname",
        )

        cls.profile_1 = Profile.objects.create(
            user=cls.test_admin, country="USA", city="Boston"
        )
        cls.profile_2 = Profile.objects.create(
            user=cls.test_user, country="Ukraine", city="Kyiv"
        )
        cls.post_1 = Post.objects.create(
            profile=cls.profile_1,
            title="Post_1",
            content="Post Content 1 #test",
        )
        cls.post_2 = Post.objects.create(
            profile=cls.profile_1,
            title="Post_2",
            content="Post Content 2",
        )
        cls.post_3 = Post.objects.create(
            profile=cls.profile_2,
            title="Post_3",
            content="Post Content 3 #test",
        )
        cls.post_4 = Post.objects.create(
            profile=cls.profile_2,
            title="Post_4",
            content="Post Content 4",
        )


class AuthorizedUserTests(PostAPITestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_user)

    def test_post_list(self):
        """Test that authorized users have access post list"""
        res = self.client.get(POSTS_URL)
        posts = Post.objects.all()
        serializer = PostListSerializer(posts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_post_operations(self):
        """Test that authorized users can create/update/delete their posts"""
        # try to create post without data
        res = self.client.post(POSTS_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # try to create post with payload
        payload = {
            "title": "Test",
            "content": "Test",
        }
        res = self.client.post(POSTS_URL, payload)
        post = Post.objects.get(pk=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(post, key))

        # try to get post detail
        url = get_post_detail_url(post.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # try to update post
        payload = {
            "title": "Test Post",
            "content": "Test Post Content",
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # try to delete own post
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_post_filtering(self):
        """test filtering ry title and hashtag"""
        res = self.client.get(POSTS_URL + "?hashtag=test")
        posts = Post.objects.filter(content__icontains="#test")
        serializer = PostListSerializer(posts, many=True)

        serialized_post_1 = PostListSerializer(self.post_1).data
        serialized_post_2 = PostListSerializer(self.post_2).data
        serialized_post_3 = PostListSerializer(self.post_3).data
        serialized_post_4 = PostListSerializer(self.post_4).data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertIn(serialized_post_1, res.data)
        self.assertNotIn(serialized_post_2, res.data)
        self.assertIn(serialized_post_3, res.data)
        self.assertNotIn(serialized_post_4, res.data)

        res = self.client.get(POSTS_URL + "?title=post_1")
        posts = Post.objects.filter(title__icontains="post_1")
        serializer = PostListSerializer(posts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertIn(serialized_post_1, res.data)
        self.assertNotIn(serialized_post_2, res.data)
        self.assertNotIn(serialized_post_3, res.data)
        self.assertNotIn(serialized_post_4, res.data)

    def test_post_detail(self):
        """Test that user can get any post detail"""
        # try to get post of another user
        url = get_post_detail_url(self.post_1.id)
        res = self.client.get(url)
        serializer = PostSerializer(self.post_1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

        # try to update another user post
        payload = {
            "title": "Post_5",
            "content": "Post Content 5",
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # try to delete another user post
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_me_endpoint(self):
        """Test endpoint that allows to get all user's posts"""
        res = self.client.get(POSTS_URL + "me/")
        posts = Post.objects.filter(profile__user=self.test_user)
        serializer = PostSerializer(posts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_feed_endpoint(self):
        """Test user subscription posts"""
        res = self.client.get(POSTS_URL + "feed/")
        followed_profiles = self.profile_2.following.values_list(
            "following", flat=True
        )
        posts = Post.objects.filter(profile__in=followed_profiles)
        serializer = PostSerializer(posts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminUserTest(PostAPITestCase):
    def setUp(self):
        self.test_post = Post.objects.create(
            profile=self.profile_2,
            title="Test Post",
            content="Test Post Content",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_admin)

    def test_post_admin_access(self):
        """Test that can't change users posts, but can delete them"""
        # try to update user's post
        url = get_post_detail_url(self.test_post.id)
        payload = {
            "title": "Post",
            "content": "Post Content",
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # try to delete user's post
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
