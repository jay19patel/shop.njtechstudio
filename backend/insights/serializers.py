from rest_framework import serializers
from insights.models import ProductEmbedding
from store.models import Product


class ProductEmbeddingSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    vector_dimension = serializers.SerializerMethodField()

    class Meta:
        model = ProductEmbedding
        fields = [
            'product_id',
            'product_name',
            'embedding_name',
            'embedding_version',
            'embedding_source',
            'description',
            'vector_dimension',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_vector_dimension(self, obj):
        if obj.embedding_vector:
            return len(obj.embedding_vector)
        return None


class ProductSearchResultSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    similarity_score = serializers.FloatField()
    embedding_name = serializers.CharField()
    description = serializers.CharField()


class ProductSearchResponseSerializer(serializers.Serializer):
    query = serializers.CharField()
    total_results = serializers.IntegerField()
    limit = serializers.IntegerField()
    threshold = serializers.FloatField()
    results = ProductSearchResultSerializer(many=True)


class EmbeddingGenerationResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    embedding_name = serializers.CharField()
    embedding_version = serializers.CharField()
    created = serializers.BooleanField()
    vector_dimension = serializers.IntegerField()
