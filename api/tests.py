from datetime import timezone

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from orders.models import OrderStatus, Order
from products.models import ProductCategory, Product, Basket
from users.models import User, EmailVerification, EmailVerificationStatus


class UserAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        cls.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        cls.url_list = reverse('user-list')
        cls.url_detail = reverse('user-detail', args=[cls.user.id])

    def test_user_list_unauthenticated(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_list_regular_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both users

    def test_user_retrieve_self(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_user_retrieve_other_user(self):
        other_user = User.objects.create_user(username='other', password='otherpass')
        self.client.force_authenticate(user=self.user)
        url = reverse('user-detail', args=[other_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_retrieve_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EmailVerificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.verification = EmailVerification.objects.create(
            user=self.user,
            expiration=timezone.now() + timezone.timedelta(hours=24)
        )
        self.url_list = reverse('emailverification-list')
        self.url_detail = reverse('emailverification-detail', args=[self.verification.id])
        self.url_resend = reverse('emailverification-resend', args=[self.verification.id])
        self.url_verify = reverse('emailverification-verify', args=[self.verification.id])

    def test_list_verifications_own_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_resend_unauthenticated(self):
        response = self.client.post(self.url_resend)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_resend_wrong_user(self):
        other_user = User.objects.create_user(username='other', password='otherpass')
        self.client.force_authenticate(user=other_user)
        response = self.client.post(self.url_resend)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verify_success(self):
        response = self.client.post(self.url_verify)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.verification.refresh_from_db()
        self.assertEqual(self.verification.status, EmailVerificationStatus.VERIFIED.name)
        self.assertTrue(self.user.is_verified_email)

    def test_verify_expired(self):
        self.verification.expiration = timezone.now() - timezone.timedelta(hours=1)
        self.verification.save()
        response = self.client.post(self.url_verify)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = ProductCategory.objects.create(name='Electronics')
        cls.product = Product.objects.create(
            name='Smartphone',
            price=999.99,
            quantity=10,
            category=cls.category
        )
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.admin = User.objects.create_superuser(username='admin', password='adminpass')
        cls.url_list = reverse('product-list')
        cls.url_detail = reverse('product-detail', args=[cls.product.id])

    def test_product_list_unauthenticated(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_create_regular_user(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Laptop', 'price': 1299.99, 'quantity': 5, 'category': self.category.id}
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_create_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Laptop', 'price': 1299.99, 'quantity': 5, 'category': self.category.id}
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BasketAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='other', password='otherpass')
        self.category = ProductCategory.objects.create(name='Books')
        self.product = Product.objects.create(
            name='Django for Beginners',
            price=39.99,
            quantity=5,
            category=self.category
        )
        self.basket = Basket.objects.create(user=self.user, product=self.product, quantity=1)
        self.url_list = reverse('basket-list')
        self.url_detail = reverse('basket-detail', args=[self.basket.id])

    def test_basket_list_unauthenticated(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_basket_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_basket_list_other_user(self):
        Basket.objects.create(user=self.other_user, product=self.product, quantity=2)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_list)
        self.assertEqual(len(response.data), 1)  # Should only see own items

    def test_basket_create_valid(self):
        self.client.force_authenticate(user=self.user)
        data = {'product_id': self.product.id}
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Basket.objects.count(), 2)  # Original + new

    def test_basket_create_invalid_product(self):
        self.client.force_authenticate(user=self.user)
        data = {'product_id': 999}  # Non-existent product
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(name='Test Product', price=10.99, quantity=10)
        self.basket = Basket.objects.create(user=self.user, product=self.product, quantity=2)
        self.order = Order.objects.create(
            initiator=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St'
        )
        self.url_list = reverse('order-list')
        self.url_detail = reverse('order-detail', args=[self.order.id])
        self.url_pay = reverse('order-pay', args=[self.order.id])

    def test_order_create_unauthenticated(self):
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'address': '456 Oak Ave'
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_create_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'address': '456 Oak Ave'
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['initiator'], self.user.id)

    def test_order_pay_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url_pay)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.PAID)

    def test_order_pay_already_paid(self):
        self.order.status = OrderStatus.PAID
        self.order.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url_pay)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
