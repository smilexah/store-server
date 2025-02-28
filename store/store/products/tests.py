from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from products.models import Product, ProductCategory


class IndexViewTestCase(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store | Main Page')
        self.assertTemplateUsed(response, 'products/index.html')


class ProductListViewTestCase(TestCase):
    fixtures = ['categories.json', 'goods.json']

    def setUp(self):
        self.products = Product.objects.all()

    def test_product_list_view(self):
        response = self.client.get(reverse('products:index'))

        self._common_tests(response)

        self.assertEqual(list(response.context_data['object_list']), list(self.products[:3]))

    def test_list_with_category(self):
        category = ProductCategory.objects.first()
        response = self.client.get(reverse('products:category', kwargs={'category_id': category.id}))

        self._common_tests(response)

        self.assertEqual(list(response.context_data['object_list']),
                         list(self.products.filter(category_id=category.id)))

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store | Products')
        self.assertTemplateUsed(response, 'products/products.html')
