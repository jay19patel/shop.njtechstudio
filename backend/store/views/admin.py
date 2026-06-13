"""Admin-only views: dashboard stats and contact message management."""
import logging
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import permissions, views, viewsets
from rest_framework.response import Response

from ..models import ContactMessage, Order, Product
from ..serializers import ContactMessageSerializer

logger = logging.getLogger(__name__)


class AdminDashboardStatsView(views.APIView):
    """Aggregated KPI stats + 7-day revenue chart for the admin dashboard."""

    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_products  = Product.objects.count()
        total_orders    = Order.objects.count()
        pending_orders  = Order.objects.filter(status='PENDING').count()
        total_revenue   = (
            Order.objects
            .filter(payment_status='VERIFIED')
            .aggregate(total=Sum('total_amount'))['total'] or 0
        )

        total_messages  = ContactMessage.objects.count()
        unread_messages = ContactMessage.objects.filter(is_read=False).count()
        return Response({
            'total_products':  total_products,
            'total_orders':    total_orders,
            'pending_orders':  pending_orders,
            'total_revenue':   float(total_revenue),
            'total_messages':  total_messages,
            'unread_messages': unread_messages,
            'read_messages':   total_messages - unread_messages,
        })


class AdminCategoryViewSet(viewsets.ModelViewSet):
    """Admin full CRUD for categories."""

    from ..serializers import CategorySerializer
    serializer_class = CategorySerializer
    queryset = None
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        from ..models import Category
        return Category.objects.all().order_by('name')


class AdminUsersViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin read-only view for all users."""

    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        from rest_framework import serializers
        class UserSerializer(serializers.ModelSerializer):
            class Meta:
                model = User
                fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined']
        return UserSerializer


class ContactMessageViewSet(viewsets.ModelViewSet):
    """Public creation of contact messages; admin-only read/update/delete."""

    serializer_class = ContactMessageSerializer
    queryset         = ContactMessage.objects.all().order_by('-created_at')

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
