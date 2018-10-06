from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from .models import Product, GiftCard


class ProductApi(APIView):

    def get(self, request):
        date_query = request.query_params.get('date', None)
        product_code = request.query_params.get('productCode', None)
        gift_code = request.query_params.get('giftCardCode', None)

        if product_code is None or date_query is None:
            missing_param_err = {'error': 'date and productCode are required'}
            return Response(missing_param_err, status=status.HTTP_400_BAD_REQUEST)

        try:
            date_searched = datetime.strptime(date_query, '%Y-%m-%d')
        except ValueError:
            date_format_err = {'error': 'date is not formatted correctly. Ex: 2018-03-14'}
            return Response(date_format_err, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(code=product_code)
        except Product.DoesNotExist:
            no_product_err = {'error': 'No product found matching {}'.format(product_code)}
            return Response(no_product_err, status=status.HTTP_404_NOT_FOUND)

        price_option = product.product_price.filter(
            date_start__lte=date_searched,
            date_end__gte=date_searched).order_by('price').first()
        price = price_option.price if price_option else None

        if price is None:
            no_price_error = {'error': 'No price found for {}'.format(product.name)}
            return Response(no_price_error, status=status.HTTP_404_NOT_FOUND)

        if gift_code is not None:
            card = GiftCard.objects.filter(
                code=gift_code,
                date_start__lte=date_searched).first()
            date_end = card.date_end if card and card.date_end else datetime.max
            is_valid = card and date_searched <= date_end
            gift_card_amount = card.amount if is_valid else 0
            price = price - gift_card_amount if price - gift_card_amount > 0 else 0

        formatted = round(price / 100, 2)

        return Response({'price': formatted})
