"""Cart views — sync, add item, and checkout."""
import logging

from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Cart, CartItem, Order, OrderItem, Product
from ..serializers import CartSerializer, CartItemSerializer, OrderSerializer
from ..signals import cart_item_added, order_created

logger = logging.getLogger(__name__)


class CartViewSet(viewsets.ModelViewSet):
    """Shopping cart CRUD + add-item action + checkout action."""

    serializer_class   = CartSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(
                Q(user=self.request.user) | Q(user__isnull=True)
            ).order_by('-created_at')
        return Cart.objects.all().order_by('-created_at')

    # ── sync entire cart ──

    def update(self, request, *args, **kwargs):
        """Replace all cart items from a frontend-provided list with stock validation."""
        cart = self.get_object()

        # Claim anonymous cart on login
        if request.user.is_authenticated and cart.user is None:
            cart.user = request.user
            cart.save()

        # Validate all items have sufficient stock before syncing
        for item_data in request.data.get('items', []):
            product_id = item_data.get('product')
            quantity = item_data.get('quantity', 1)
            try:
                product_obj = Product.objects.filter(id=product_id).first()
                if not product_obj:
                    return Response(
                        {'error': f'Product {product_id} not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                if product_obj.available_quantity < quantity:
                    return Response(
                        {'error': f'Insufficient stock for {product_obj.name}. Available: {product_obj.available_quantity}, Requested: {quantity}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                logger.warning("cart_sync_bad_product_id",
                               extra={"product_id": product_id})

        cart.items.all().delete()

        for item_data in request.data.get('items', []):
            product_id = item_data.get('product')
            quantity   = item_data.get('quantity', 1)
            try:
                product_obj = Product.objects.filter(id=product_id).first()
                if product_obj:
                    CartItem.objects.create(cart=cart, product=product_obj, quantity=quantity)
            except ValueError:
                logger.warning("cart_item_skipped_bad_product_id",
                               extra={"product_id": product_id})

        return Response(self.get_serializer(cart).data)

    # ── add single item ──

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Increment (or create) a cart item by product_id with stock validation."""
        cart       = self.get_object()
        product_id = request.data.get('product_id')
        quantity   = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'error': 'product_id is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get product and validate it exists
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({'error': f'Product {product_id} not found'},
                            status=status.HTTP_404_NOT_FOUND)

        # Check if enough stock is available
        if product.available_quantity < quantity:
            return Response(
                {'error': f'Insufficient stock. Available: {product.available_quantity}, Requested: {quantity}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item, created = CartItem.objects.get_or_create(
            cart=cart, product_id=product_id,
            defaults={'quantity': quantity}
        )
        if not created:
            # Check if adding more would exceed available stock
            total_qty = item.quantity + quantity
            if product.available_quantity < total_qty:
                return Response(
                    {'error': f'Cannot add {quantity} more. Only {product.available_quantity - item.quantity} left in stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.quantity += quantity
            item.save()

        # Emit cart item added signal (insights app listens and publishes to Kafka)
        if cart.user:
            cart_item_added.send(
                sender=self.__class__,
                request=request,
                user_id=cart.user.id,
                product_id=product.id,
                product_name=product.name,
                quantity=quantity,
                price=float(product.base_price),
            )

        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    # ── checkout ──

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def checkout(self, request, pk=None):
        """Convert a cart into a confirmed Order with inventory management."""
        cart             = self.get_object()
        shipping_address = request.data.get('shipping_address')

        if not shipping_address:
            return Response({'error': 'shipping_address is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        items = cart.items.all()
        if not items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate stock availability for all items
        for item in items:
            if item.product.available_quantity < item.quantity:
                return Response(
                    {'error': f'Insufficient stock for {item.product.name}. Available: {item.product.available_quantity}, Requested: {item.quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        total_amount = sum(item.total_price for item in items)
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            shipping_address=shipping_address,
        )

        # Create order items and decrease inventory
        order_items = []
        for item in items:
            order_items.append(OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.base_price,
            ))
            # Decrease product inventory
            item.product.available_quantity -= item.quantity
            item.product.save()
            logger.info("inventory_decreased",
                       extra={"product_id": item.product.id, "quantity": item.quantity, "remaining": item.product.available_quantity})

        OrderItem.objects.bulk_create(order_items)
        cart.items.all().delete()

        # Emit order created signal (insights app listens and publishes to Kafka)
        order_created.send(
            sender=self.__class__,
            request=request,
            user_id=request.user.id,
            order_id=order.id,
            total_amount=float(order.total_amount),
            items_count=len(items),
        )

        logger.info("cart_checkout_complete",
                    extra={"order_id": order.id, "user_id": request.user.id})
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
