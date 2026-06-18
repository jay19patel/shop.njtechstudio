from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from unittest.mock import MagicMock, patch
from typing import Any

from store.models import Category, Product
from insights.models import ProductEmbedding, CategoryEmbedding, UserSemanticProfile
from insights.services.request_parser import RequestParserService
from insights.services.recommendation import RecommendationService

User = get_user_model()


class RequestParserServiceTests(TestCase):
    """Test suite for RequestParserService helper methods."""

    def setUp(self) -> None:
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test'
        )

    def test_get_client_ip_with_x_forwarded_for(self) -> None:
        """Verify get_client_ip extracts IP correctly from HTTP_X_FORWARDED_FOR header."""
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='192.168.1.1, 10.0.0.1')
        ip = RequestParserService.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_with_remote_addr(self) -> None:
        """Verify get_client_ip extracts IP correctly from REMOTE_ADDR fallback."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        ip = RequestParserService.get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')

    def test_get_user_agent(self) -> None:
        """Verify get_user_agent extracts HTTP_USER_AGENT header."""
        request = self.factory.get('/', HTTP_USER_AGENT='TestAgent/1.0')
        agent = RequestParserService.get_user_agent(request)
        self.assertEqual(agent, 'TestAgent/1.0')

    def test_extract_user_info(self) -> None:
        """Verify extract_user_info aggregates client and user properties."""
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='1.2.3.4', HTTP_USER_AGENT='TestAgent/1.0')
        info = RequestParserService.extract_user_info(request, self.user)
        self.assertEqual(info['email'], 'test@example.com')
        self.assertEqual(info['name'], 'Test')
        self.assertEqual(info['ip_address'], '1.2.3.4')
        self.assertEqual(info['user_agent'], 'TestAgent/1.0')


class RecommendationServiceTests(TestCase):
    """Test suite for RecommendationService class-based helper methods."""

    def setUp(self) -> None:
        """Set up test database records."""
        self.user = User.objects.create_user(
            username='recuser',
            email='rec@example.com',
            password='testpassword'
        )
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            category=self.category,
            name='Smartphone',
            slug='smartphone',
            description='A smart phone',
            base_price=599.99,
            available_quantity=10,
            is_active=True
        )

        # Mock embedding vectors
        self.p_vector = [0.1] * 768
        self.c_vector = [0.2] * 768

        ProductEmbedding.objects.update_or_create(
            product=self.product,
            defaults={
                'embedding_vector': self.p_vector,
                'embedding_source': 'ollama'
            }
        )
        CategoryEmbedding.objects.update_or_create(
            category=self.category,
            defaults={
                'embedding_vector': self.c_vector
            }
        )

    def test_normalize_vector(self) -> None:
        """Verify L2 normalization transforms vector correctly to unit length."""
        vector = [3.0, 4.0]
        normalized = RecommendationService._normalize_vector(vector)
        self.assertAlmostEqual(normalized[0], 0.6)
        self.assertAlmostEqual(normalized[1], 0.8)

    def test_dot_product(self) -> None:
        """Verify dot product calculations."""
        v1 = [1.0, 2.0, 3.0]
        v2 = [4.0, 5.0, 6.0]
        dot = RecommendationService._dot_product(v1, v2)
        # 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32
        self.assertEqual(dot, 32.0)

    def test_update_user_profile_first_interaction(self) -> None:
        """Verify first event correctly sets up user semantic profile."""
        RecommendationService.update_user_profile(
            user_id=self.user.id,
            product_id=self.product.id,
            event_type='PRODUCT_VIEWED'
        )

        profile = UserSemanticProfile.objects.get(user=self.user)
        self.assertIsNotNone(profile.preference_vector)
        # Weight for PRODUCT_VIEWED is 1.0. Check category and product scores.
        self.assertEqual(profile.category_interests[str(self.category.id)], 1.0)
        self.assertEqual(profile.product_interests[str(self.product.id)], 1.0)

    def test_get_user_interests_data_semantic(self) -> None:
        """Verify semantic category and product recommendations are returned when preference_vector is set."""
        profile = UserSemanticProfile.objects.create(
            user=self.user,
            preference_vector=self.p_vector,
            category_interests={},
            product_interests={}
        )

        data = RecommendationService.get_user_interests_data(self.user.id)
        
        top_cats = data['top_categories']
        top_prods = data['top_products']

        self.assertEqual(len(top_cats), 1)
        self.assertEqual(top_cats[0]['category_id'], self.category.id)
        self.assertEqual(top_cats[0]['name'], 'Electronics')
        self.assertGreater(top_cats[0]['score'], 0.0)

        self.assertEqual(len(top_prods), 1)
        self.assertEqual(top_prods[0]['product_id'], self.product.id)
        self.assertEqual(top_prods[0]['name'], 'Smartphone')
        self.assertGreater(top_prods[0]['score'], 0.0)

    def test_get_user_interests_data_fallback(self) -> None:
        """Verify raw scores fallback when preference_vector is not set."""
        profile = UserSemanticProfile.objects.create(
            user=self.user,
            preference_vector=None,
            category_interests={str(self.category.id): 5.5},
            product_interests={str(self.product.id): 10.0}
        )

        data = RecommendationService.get_user_interests_data(self.user.id)
        
        top_cats = data['top_categories']
        top_prods = data['top_products']

        self.assertEqual(len(top_cats), 1)
        self.assertEqual(top_cats[0]['category_id'], self.category.id)
        self.assertEqual(top_cats[0]['name'], 'Electronics')
        self.assertEqual(top_cats[0]['score'], 5.5)

        self.assertEqual(len(top_prods), 1)
        self.assertEqual(top_prods[0]['product_id'], self.product.id)
        self.assertEqual(top_prods[0]['name'], 'Smartphone')
        self.assertEqual(top_prods[0]['score'], 10.0)

    def test_get_top_products(self) -> None:
        """Verify retrieving semantically similar products for a user profile."""
        profile = UserSemanticProfile.objects.create(
            user=self.user,
            preference_vector=self.p_vector,
            category_interests={},
            product_interests={}
        )

        similar_products = RecommendationService.get_top_products(self.user.id, limit=5)
        self.assertEqual(len(similar_products), 1)
        self.assertEqual(similar_products[0]['product_id'], self.product.id)
        self.assertEqual(similar_products[0]['name'], 'Smartphone')
        self.assertGreater(similar_products[0]['score'], 0.0)

    def test_get_similar_categories(self) -> None:
        """Verify category similarity retrieval via embeddings."""
        cat2 = Category.objects.create(name='Appliances', slug='appliances')
        CategoryEmbedding.objects.update_or_create(category=cat2, defaults={'embedding_vector': self.c_vector})

        similar_cats = RecommendationService.get_similar_categories(self.category.id, limit=5)
        self.assertEqual(len(similar_cats), 1)
        self.assertEqual(similar_cats[0]['category_id'], cat2.id)
        self.assertEqual(similar_cats[0]['name'], 'Appliances')
        self.assertGreater(similar_cats[0]['score'], 0.0)
