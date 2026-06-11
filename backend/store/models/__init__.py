"""
store.models package
====================
Re-exports all model classes so that:
  - `from store.models import Order` still works everywhere
  - Django migrations (which reference 'store.models') remain valid
  - app_label is inherited from StoreConfig automatically
"""

from .category    import Category
from .product     import Product, ProductImage
from .cart        import Cart, CartItem
from .order       import Order, OrderItem
from .payment     import Payment
from .user_profile import Address, Contact
from .content     import Testimonial, ContactMessage, FAQ
from .email_log   import EmailLog
from .coupon      import Coupon

__all__ = [
    "Category",
    "Product", "ProductImage",
    "Cart", "CartItem",
    "Order", "OrderItem",
    "Payment",
    "Address", "Contact",
    "Coupon",
    "Testimonial", "FAQ",
    "ContactMessage",
    "EmailLog",
]
