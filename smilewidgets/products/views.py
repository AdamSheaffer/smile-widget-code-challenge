from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product


class ProductApi(APIView):

    def get(self, request):
        product_code = request.query_params.get('productCode')

        try:
            product = Product.objects.get(code=product_code)
        except Product.DoesNotExist:
            raise Http404

        return Response({
            'product': product.name
        })

