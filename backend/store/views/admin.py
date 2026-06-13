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

        # User stats
        total_users = User.objects.count()
        superusers = User.objects.filter(is_superuser=True).count()
        regular_users = total_users - superusers

        # Last 7 days chart data
        seven_days_ago = timezone.now() - timedelta(days=7)
        daily_stats = (
            Order.objects
            .filter(created_at__gte=seven_days_ago)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(
                revenue=Sum('total_amount', filter=Q(payment_status='VERIFIED')),
                orders=Count('id'),
            )
            .order_by('date')
        )
        chart_data = [
            {
                'date':    stat['date'].strftime('%d %b'),
                'revenue': float(stat['revenue'] or 0),
                'orders':  stat['orders'],
            }
            for stat in daily_stats
        ]

        # Category sales breakdown
        from ..models import Category
        category_sales = (
            Order.objects
            .filter(payment_status='VERIFIED')
            .values('items__product__category__name')
            .annotate(total=Sum('items__quantity'))
            .order_by('-total')[:5]
        )
        category_data = [
            {'category': cat['items__product__category__name'] or 'Uncategorized', 'sales': cat['total']}
            for cat in category_sales
        ]

        total_messages  = ContactMessage.objects.count()
        unread_messages = ContactMessage.objects.filter(is_read=False).count()
        return Response({
            'total_products':  total_products,
            'total_orders':    total_orders,
            'pending_orders':  pending_orders,
            'total_revenue':   float(total_revenue),
            'total_users':     total_users,
            'superusers':      superusers,
            'regular_users':   regular_users,
            'chart_data':      chart_data,
            'category_data':   category_data,
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


class ContactMessageViewSet(viewsets.ModelViewSet):
    """Public creation of contact messages; admin-only read/update/delete."""

    serializer_class = ContactMessageSerializer
    queryset         = ContactMessage.objects.all().order_by('-created_at')

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
