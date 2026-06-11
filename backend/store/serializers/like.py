from rest_framework import serializers
from store.models import Like, Product


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'product', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductLikeSerializer(serializers.ModelSerializer):
    """Serializer for product with like information"""
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'likes_count', 'is_liked']

    def get_likes_count(self, obj):
        return obj.liked_by.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(user=request.user).exists()
        return False


class UserLikesSerializer(serializers.ModelSerializer):
    """Serializer for getting user's liked products"""
    product_id = serializers.IntegerField(source='product.id')
    product_name = serializers.CharField(source='product.name')
    product_image = serializers.CharField(source='product.image')
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)

    class Meta:
        model = Like
        fields = ['id', 'product_id', 'product_name', 'product_image', 'product_price', 'created_at']
        read_only_fields = ['id', 'created_at']
