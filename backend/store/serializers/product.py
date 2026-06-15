from rest_framework import serializers
from ..models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """Recursive category serializer — includes nested children."""

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image_url', 'parent', 'children', 'created_at', 'updated_at']

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_primary']



class SimpleProductSerializer(serializers.ModelSerializer):
    """Lightweight product summary used inside Cart / Order item serializers."""

    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'base_price', 'primary_image', 'discount_percentage', 'available_quantity']

    def get_primary_image(self, obj) -> str | None:
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        return img.image_url if img else None


class ProductSerializer(serializers.ModelSerializer):
    """Full product serializer with nested category, images and variants."""

    category    = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    images        = ProductImageSerializer(many=True, read_only=True)

    price_value   = serializers.DecimalField(source='base_price', max_digits=10, decimal_places=2, read_only=True)
    price         = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'base_price', 'price_value', 'price',
            'is_active', 'category', 'category_id', 'images', 'primary_image',
            'discount_percentage', 'available_quantity', 'created_at', 'updated_at',
        ]

    def get_price(self, obj) -> str:
        return f"₹{obj.base_price}"

    def get_primary_image(self, obj) -> str | None:
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        return img.image_url if img else None
