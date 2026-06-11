from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from django.shortcuts import get_object_or_404
from store.models import Like, Product
from store.serializers import LikeSerializer, UserLikesSerializer, ProductLikeSerializer


class LikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product likes.

    Endpoints:
    - POST /likes/ - Create a like
    - DELETE /likes/{id}/ - Delete a like
    - GET /likes/my-likes/ - Get current user's likes
    - POST /likes/toggle-like/ - Toggle like for a product
    """
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a like for a product"""
        product_id = request.data.get('product')
        if not product_id:
            raise ValidationError('product field is required')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound(f'Product with id {product_id} does not exist')

        like, created = Like.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            return Response(
                {'detail': 'You have already liked this product'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='toggle-like')
    def toggle_like(self, request):
        """Toggle like for a product"""
        product_id = request.data.get('product_id')
        if not product_id:
            raise ValidationError('product_id field is required')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound(f'Product with id {product_id} does not exist')

        like = Like.objects.filter(user=request.user, product=product)

        if like.exists():
            like.delete()
            return Response(
                {'liked': False, 'message': 'Like removed'},
                status=status.HTTP_200_OK
            )
        else:
            Like.objects.create(user=request.user, product=product)
            return Response(
                {'liked': True, 'message': 'Like added'},
                status=status.HTTP_201_CREATED
            )

    @action(detail=False, methods=['get'], url_path='my-likes')
    def my_likes(self, request):
        """Get current user's liked products"""
        likes = self.get_queryset()
        serializer = UserLikesSerializer(likes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='is-liked')
    def is_liked(self, request):
        """Check if a product is liked by current user"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            raise ValidationError('product_id query parameter is required')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound(f'Product with id {product_id} does not exist')

        is_liked = Like.objects.filter(user=request.user, product=product).exists()
        return Response({
            'product_id': product_id,
            'is_liked': is_liked,
            'likes_count': product.liked_by.count()
        })
