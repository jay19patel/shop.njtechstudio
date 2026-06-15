from django.db import models
from django.contrib.auth.models import User
from .product import Product


class Cart(models.Model):
    """Shopping cart — belongs to a logged-in user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        owner = self.user.username if self.user else "anonymous"
        return f"Cart [{owner}]"


class CartItem(models.Model):
    """A single line item inside a cart."""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        price = self.product.base_price
        return price * self.quantity

    def __str__(self) -> str:
        return f"{self.quantity} × {self.product.name}"
