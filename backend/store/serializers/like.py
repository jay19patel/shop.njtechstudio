from rest_framework import serializers
from store.models import Like, Product


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'product', 'price_at_like', 'created_at']
        read_only_fields = ['id', 'price_at_like', 'created_at']


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
    """Serializer for getting user's liked products with price snapshot"""
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    product_image = serializers.SerializerMethodField()
    current_price = serializers.SerializerMethodField()
    price_when_liked = serializers.SerializerMethodField()
    liked_date = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'product_id', 'product_name', 'product_slug', 'product_image', 'current_price', 'price_when_liked', 'liked_date']
        read_only_fields = ['id', 'product_id', 'product_name', 'product_slug', 'product_image', 'current_price', 'price_when_liked', 'liked_date']

    def get_product_image(self, obj):
        """Get primary image from related product"""
        try:
            if obj.product and obj.product.images.exists():
                primary = obj.product.images.filter(is_primary=True).first()
                return primary.image_url if primary else obj.product.images.first().image_url
        except Exception:
            pass
        return None

    def get_current_price(self, obj):
        """Calculate current effective price with discount"""
        try:
            product = obj.product
            if product.discount_percentage > 0:
                return float(product.base_price * (100 - product.discount_percentage) / 100)
            return float(product.base_price)
        except Exception:
            return None

    def get_price_when_liked(self, obj):
        """Get price snapshot when product was liked"""
        try:
            if obj.price_at_like:
                return float(obj.price_at_like)
        except Exception:
            pass
        return None
