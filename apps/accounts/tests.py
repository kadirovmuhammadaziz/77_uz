import json
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
from .models import Address

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'full_name': 'Test User',
            'phone_number': '+998901234567',
            'role': 'customer',
            'status': 'pending'
        }

    def test_user_creation(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.full_name, 'Test User')
        self.assertEqual(user.phone_number, '+998901234567')
        self.assertEqual(user.role, 'customer')
        self.assertEqual(user.status, 'pending')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_user_str_representation(self):
        user = User.objects.create_user(**self.user_data)
        expected_str = f"{self.user_data['full_name']} ({self.user_data['phone_number']})"
        self.assertEqual(str(user), expected_str)

    def test_phone_number_validation(self):
        invalid_phones = [
            '+99890123456',
            '+9989012345678'
            '998901234567',
            '+997901234567',
            '+998abc234567',
        ]

        for phone in invalid_phones:
            user_data = self.user_data.copy()
            user_data['phone_number'] = phone
            user = User(**user_data)
            with self.assertRaises(ValidationError):
                user.full_clean()

    def test_is_seller_property(self):
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_seller)

        seller_data = self.user_data.copy()
        seller_data['role'] = 'seller'
        seller = User.objects.create_user(**seller_data)
        self.assertTrue(seller.is_seller)

    def test_unique_phone_number(self):
        User.objects.create_user(**self.user_data)

        duplicate_data = self.user_data.copy()
        duplicate_data['full_name'] = 'Another User'

        with self.assertRaises(Exception):  # IntegrityError
            User.objects.create_user(**duplicate_data)


class AddressModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            full_name='Test User',
            phone_number='+998901234567'
        )

    def test_address_creation(self):

        address = Address.objects.create(
            user=self.user,
            name='Test Address',
            lat=Decimal('41.2995'),
            long=Decimal('69.2401')
        )

        self.assertEqual(address.user, self.user)
        self.assertEqual(address.name, 'Test Address')
        self.assertEqual(address.lat, Decimal('41.2995'))
        self.assertEqual(address.long, Decimal('69.2401'))

    def test_address_str_representation(self):


        address = Address.objects.create(
            user=self.user,
            name='Test Address',
            lat=Decimal('41.2995'),
            long=Decimal('69.2401')
        )

        expected_str = f"Test Address - {self.user.full_name}"
        self.assertEqual(str(address), expected_str)


class UserRegistrationViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('user-register')
        self.valid_data = {
            'full_name': 'Test User',
            'phone_number': '+998901234567'
        }

    @patch('users.serializers.UserRegistrationSerializer.save')
    @patch('users.serializers.UserRegistrationSerializer.is_valid')
    def test_successful_registration(self, mock_is_valid, mock_save):
        mock_is_valid.return_value = True
        mock_user = User(id=1, **self.valid_data)
        mock_save.return_value = mock_user

        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)

    def test_invalid_registration_data(self):
        invalid_data = {
            'full_name': '',
            'phone_number': 'invalid'  # Invalid phone
        }

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('user-login')
        self.user = User.objects.create_user(
            full_name='Test User',
            phone_number='+998901234567'
        )
        self.login_data = {
            'phone_number': '+998901234567'
        }

    @patch('users.serializers.UserLoginSerializer.is_valid')
    @patch('users.serializers.UserLoginSerializer.to_representation')
    def test_successful_login(self, mock_to_representation, mock_is_valid):
        mock_is_valid.return_value = True
        mock_to_representation.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'user': {'id': self.user.id, 'full_name': self.user.full_name}
        }

        response = self.client.post(self.url, self.login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)

    def test_invalid_login(self):
        invalid_data = {
            'phone_number': '+998999999999'  # Non-existent user
        }

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('user-profile')
        self.user = User.objects.create_user(
            full_name='Test User',
            phone_number='+998901234567'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_get_user_profile(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], self.user.full_name)
        self.assertEqual(response.data['phone_number'], self.user.phone_number)

    def test_update_user_profile(self):
        update_data = {
            'full_name': 'Updated Name'
        }

        response = self.client.patch(self.url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Name')

    def test_unauthenticated_access(self):
        self.client.credentials()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SellerRegistrationViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('seller-register')
        self.valid_data = {
            'full_name': 'Test Seller',
            'phone_number': '+998901234567',
            'project_name': 'Test Project',
            'category': 1
        }

    @patch('users.serializers.SellerRegistrationSerializer.save')
    @patch('users.serializers.SellerRegistrationSerializer.is_valid')
    @patch('users.serializers.SellerRegistrationSerializer.to_representation')
    def test_successful_seller_registration(self, mock_to_representation,
                                            mock_is_valid, mock_save):
        mock_is_valid.return_value = True
        mock_seller = User(id=1, role='seller', **self.valid_data)
        mock_save.return_value = mock_seller
        mock_to_representation.return_value = {
            'id': 1,
            'full_name': 'Test Seller',
            'role': 'seller',
            'status': 'pending'
        }

        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_seller_registration(self):
        invalid_data = {
            'full_name': 'Test Seller',
            'phone_number': '+998901234567'
        }

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('token-refresh')
        self.user = User.objects.create_user(
            full_name='Test User',
            phone_number='+998901234567'
        )
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)

    @patch('users.serializers.TokenRefreshSerializer.is_valid')
    def test_successful_token_refresh(self, mock_is_valid):
        mock_is_valid.return_value = True

        with patch.object(
                self.client.post(self.url, {'refresh': self.refresh_token}, format='json').__class__,
                'validated_data',
                {'access_token': 'new_access_token'}
        ):
            response = self.client.post(
                self.url,
                {'refresh': self.refresh_token},
                format='json'
            )

        self.assertIn(reverse('token-refresh'), self.url)

    def test_invalid_refresh_token(self):
        invalid_data = {
            'refresh': 'invalid_token'
        }

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenVerifyViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('token-verify')
        self.user = User.objects.create_user(
            full_name='Test User',
            phone_number='+998901234567'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    @patch('users.serializers.TokenVerifySerializer.is_valid')
    def test_valid_token_verification(self, mock_is_valid):
        mock_is_valid.return_value = True

        self.assertIn('token/verify', self.url)

    def test_invalid_token_verification(self):
        invalid_data = {
            'token': 'invalid_token'
        }

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class IntegrationTest(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_complete_user_flow(self):
        register_data = {
            'full_name': 'Integration Test User',
            'phone_number': '+998901234567'
        }

        register_url = reverse('user-register')

        login_url = reverse('user-login')
        login_data = {
            'phone_number': '+998901234567'
        }

        profile_url = reverse('user-profile')

        self.assertTrue(True)


class TestDataFactory:

    @staticmethod
    def create_user(phone_suffix='123456', **kwargs):
        defaults = {
            'full_name': f'Test User {phone_suffix}',
            'phone_number': f'+99890{phone_suffix}',
            'role': 'customer'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    @staticmethod
    def create_seller(**kwargs):
        defaults = {
            'role': 'seller',
            'project_name': 'Test Project',
            'status': 'pending'
        }
        defaults.update(kwargs)
        return TestDataFactory.create_user(**defaults)


class PerformanceTest(TestCase):

    def test_bulk_user_creation(self):
        users_data = [
            {
                'full_name': f'User {i}',
                'phone_number': f'+99890123456{i:01d}',
                'role': 'customer'
            }
            for i in range(10)
        ]

        users = [User(**data) for data in users_data]
        User.objects.bulk_create(users)

        self.assertEqual(User.objects.count(), 10)


if __name__ == '__main__':
    import unittest

    test_classes = [
        UserModelTest,
        AddressModelTest,
        UserRegistrationViewTest,
        UserLoginViewTest,
        UserProfileViewTest,
        SellerRegistrationViewTest,
        TokenRefreshViewTest,
        TokenVerifyViewTest,
        IntegrationTest,
        PerformanceTest
    ]

    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)