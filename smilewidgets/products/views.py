from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from .models import Product


class ProductApi(APIView):

    def get(self, request):
        product_code = request.query_params.get('productCode', None)
        date_query = request.query_params.get('date', None)
        gift_code = request.query_params.get('gitCardCode', None)

        if product_code is None or date_query is None:
            missing_param_err = {'error': 'date and productCode are required'}
            return Response(missing_param_err, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.strptime(date_query, '%Y-%m-%d')
        except ValueError:
            date_format_err = {'error': 'date is not formatted correctly. Ex: 2018-03-14'}
            return Response(date_format_err, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(code=product_code)
        except Product.DoesNotExist:
            no_product_err = {'error': 'No product found matching {}'.format(product_code)}
            return Response(no_product_err, status=status.HTTP_404_NOT_FOUND)

        price_options = product.product_price.filter(date_start__lte=date, date_end__gte=date).order_by('price')
        price = price_options[0].price if price_options else None

        if price is None:
            no_price_error = {'error': 'No price found for {}'.format(product.name)}
            return Response(no_price_error, status=status.HTTP_404_NOT_FOUND)

        formatted = '${0:.2f}'.format(price / 100) if price else 'FREE!'

        return Response({'price': formatted})
