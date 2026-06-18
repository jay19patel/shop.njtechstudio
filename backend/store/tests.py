from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from .models import Category, Order, Product


class StoreAPITests(TestCase):
    """Test suite for store API endpoints."""

    def test_order_checkout_normalizes_status_and_payment(self) -> None:
        """Verify checking out an order registers and normalizes properties correctly."""
        user = User.objects.create_user(
            username='customer@example.com',
            email='customer@example.com',
            password='secure-password',
        )
        category = Category.objects.create(name='Home', slug='home')
        product = Product.objects.create(
            category=category,
            name='Artisan Soap',
            slug='artisan-soap',
            description='Handmade',
            base_price='249.00',
            available_quantity=3,
        )
        client = APIClient()
        client.force_authenticate(user)

        response = client.post('/api/orders/', {
            'customer_name': 'Customer',
            'customer_email': user.email,
            'shipping_address': 'Main Street',
            'total_amount': '249.00',
            'status': 'pending',
            'payment_status': 'received',
            'upi_transaction_id': 'UPI-TEST-249',
            'items': [{'product_id': product.pk, 'quantity': 1, 'price': '249.00'}],
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertEqual(response.data['payment_status'], 'RECEIVED')
        self.assertEqual(response.data['payment_reference'], f"PAY-NJ-{response.data['id']:06d}")
        self.assertEqual(response.data['upi_transaction_id'], 'UPI-TEST-249')
