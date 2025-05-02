from products.models import Basket
from users.models import User


from enum import Enum
from django.db import models
from django.utils.functional import cached_property

class OrderStatus(Enum):
    CREATED = 0
    PAID = 1
    ON_WAY = 2
    DELIVERED = 3
    CANCELED = 4

    @classmethod
    def choices(cls):
        return [(status.value, status.name) for status in cls]

class Order(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=128)
    address = models.CharField(max_length=256)
    basket_history = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=OrderStatus.choices(), default=OrderStatus.CREATED)
    initiator = models.ForeignKey(to='users.User', on_delete=models.CASCADE)

    def __str__(self):
        return f'Order #{self.id}. {self.first_name} {self.last_name}'

    @cached_property
    def basket_history(self):
        baskets = Basket.objects.filter(user=self.initiator)
        return {
            'purchased_items': [basket.de_json() for basket in baskets],
            'total_sum': float(baskets.total_sum()),
        }

    def update_after_payment(self):
        self.status = OrderStatus.PAID
        self.save()

        baskets = Basket.objects.filter(user=self.initiator)
        self.basket_history = {
            'purchased_items': [basket.de_json() for basket in baskets],
            'total_sum': float(baskets.total_sum()),
        }

        baskets.update(is_purchased=True)
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name} for order #{self.order.id}'