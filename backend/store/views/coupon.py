from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Coupon

class ValidateCouponView(APIView):
    """
    Validates a coupon code and returns its discount percentage if valid and active.
    """
    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        if not code:
            return Response({"error": "Coupon code is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            coupon = Coupon.objects.get(code=code)
            if not coupon.is_active:
                return Response({"error": "This coupon code is no longer active."}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                "code": coupon.code,
                "discount_percentage": float(coupon.discount_percentage)
            }, status=status.HTTP_200_OK)
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon code."}, status=status.HTTP_404_NOT_FOUND)

class ActiveCouponsView(APIView):
    """
    Returns the most active coupon (e.g. highest discount).
    """
    def get(self, request):
        coupons = Coupon.objects.filter(is_active=True).order_by('-discount_percentage')
        if not coupons.exists():
            return Response({"error": "No active coupons."}, status=status.HTTP_404_NOT_FOUND)
        
        top_coupon = coupons.first()
        return Response({
            "code": top_coupon.code,
            "discount_percentage": float(top_coupon.discount_percentage)
        }, status=status.HTTP_200_OK)
