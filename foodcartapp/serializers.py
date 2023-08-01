from rest_framework import serializers
from .models import Order, ProductQuantity, Product
from django.db import transaction


class ProductQuantitySerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(required=True, queryset=Product.objects.all())

    class Meta:
        model = ProductQuantity
        fields = ['quantity', 'product']

    def create(self, validated_data, order: Order):
        transaction.atomic()
        prodquantity = ProductQuantity.objects.create(
            product=validated_data.get('product'),
            quantity=validated_data.get('quantity'),
            order=order
        )
        return prodquantity



class CreateOrderSerializer(serializers.ModelSerializer):
    products = serializers.ListSerializer(
        child=ProductQuantitySerializer(required=False), allow_empty=False, allow_null=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'products', 'phonenumber', 'address']

    def create(self, validated_data):
        self._products = self.validated_data.pop('products')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for prod in self._products:
                prod['product'] = prod.get('product').id
                serializer = ProductQuantitySerializer(data=prod)
                serializer.is_valid(raise_exception=True)
                serializer.create(serializer.validated_data, order)

            return order
