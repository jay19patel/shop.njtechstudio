from django.db import models

class Coupon(models.Model):
    """A discount code that can be applied at checkout."""
    code = models.CharField(max_length=50, unique=True, help_text="e.g. DISCOUNT20")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="e.g. 20.00 for 20%")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.code} ({self.discount_percentage}%)"
