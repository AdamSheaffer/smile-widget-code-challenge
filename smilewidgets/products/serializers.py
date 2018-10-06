from rest_framework import serializers

from .models import (
    Product,
    ProductPrice
)


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    product_price = ProductPriceSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'
