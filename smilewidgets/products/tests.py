from django.test import TestCase
from rest_framework.test import APIClient
from datetime import timedelta, datetime
from .models import GiftCard, Product, ProductPrice


class PriceApiTestCase(TestCase):
    def setUp(self):
        self.sm_widget = Product.objects.create(name='Small Widget', code='sm_widget')
        self.big_widget = Product.objects.create(name='Big Widget', code='big_widget')

        self.gc_250 = GiftCard.objects.create(
            code='250OFF',
            amount=25000,
            date_start='2018-12-01',
            date_end='2019-01-01'
        )
        self.gc_50 = GiftCard.objects.create(
            code='50OFF',
            amount=5000,
            date_start='2018-07-01'
        )
        self.gc_10 = GiftCard.objects.create(
            code='10OFF',
            amount=1000,
            date_start='2018-07-01'
        )

        self.sm_2019_price = ProductPrice.objects.create(
            price=12500,
            date_start='2019-01-01',
            date_end='9999-12-31',
            description='2019 Prices',
            product=self.sm_widget
        )

        self.sm_sale_price = ProductPrice.objects.create(
            price=0,
            date_start='2018-11-23',
            date_end='2018-11-25',
            description='Black Friday Prices',
            product=self.sm_widget
        )

        self.sm_standard_price = ProductPrice.objects.create(
            price=0,
            date_start='0001-01-01',
            date_end='2018-12-31',
            description='Standard Prices',
            product=self.sm_widget
        )

        self.bg_2019_price = ProductPrice.objects.create(
            price=120000,
            date_start='2019-01-01',
            date_end='9999-12-31',
            description='2019 Prices',
            product=self.big_widget
        )

        self.bg_sale_price = ProductPrice.objects.create(
            price=80000,
            date_start='2018-11-23',
            date_end='2018-11-25',
            description='Black Friday Prices',
            product=self.big_widget

        )

        self.bg_standard_price = ProductPrice.objects.create(
            price=100000,
            date_start='0001-01-01',
            date_end='2018-12-31',
            description='Standard Prices',
            product=self.big_widget
        )

        self.client = APIClient()

    @staticmethod
    def convert_to_dollars(cents):
        return round(cents / 100, 2)

    def test_big_widget_standard_prices(self):
        """
        Check happy path searching just product code and date for big widget
        """
        params = {'date': '2018-10-07', 'productCode': self.big_widget.code}
        response = self.client.get('/api/get-price', params, format='json')
        expected_price = PriceApiTestCase.convert_to_dollars(self.bg_standard_price.price)
        self.assertEqual(response.data, {'price': expected_price})

    def test_sm_widget_standard_prices(self):
        """
        Check happy path searching just product code and date for small widget
        """
        params = {'date': '2018-10-07', 'productCode': self.sm_widget.code}
        response = self.client.get('/api/get-price', params, format='json')
        expected_price = PriceApiTestCase.convert_to_dollars(self.sm_standard_price.price)
        self.assertEqual(response.data, {'price': expected_price})

    def test_prices_last_day(self):
        """
        Confirm that the last day of pricing is inclusive
        """
        params = {'date': '2018-12-31', 'productCode': self.big_widget.code}
        response = self.client.get('/api/get-price', params, format='json')
        expected_price = PriceApiTestCase.convert_to_dollars(self.bg_standard_price.price)
        self.assertEqual(response.data, {'price': expected_price})

    def test_prices_first_day(self):
        """
        Confirm that the first day of pricing is inclusive
        """
        params = {'date': self.bg_2019_price.date_start, 'productCode': self.big_widget.code}
        response = self.client.get('/api/get-price', params, format='json')
        expected_price = PriceApiTestCase.convert_to_dollars(self.bg_2019_price.price)
        self.assertEqual(response.data, {'price': expected_price})

    def test_date_with_multiple_options_returns_lowest(self):
        """
        Confirm that the lowest price is returned if a date queried matches multiple prices
        """
        params = {'date': self.bg_sale_price.date_start, 'productCode': self.big_widget.code}
        response = self.client.get('/api/get-price', params, format='json')
        expected_price = PriceApiTestCase.convert_to_dollars(self.bg_sale_price.price)
        self.assertEqual(response.data, {'price': expected_price})

    def test_valid_gift_code_adds_discount(self):
        """
        Confirm that a valid discount code adds a discount on to the price
        """
        params = {
            'date': '2018-10-7',
            'productCode': self.big_widget.code,
            'giftCardCode': self.gc_50.code
        }
        response = self.client.get('/api/get-price', params, format='json')
        expected_price = PriceApiTestCase.convert_to_dollars(self.bg_standard_price.price - self.gc_50.amount)
        self.assertEqual(response.data, {'price': expected_price})

    def test_gift_code_start_date_inclusiveness(self):
        """
        Confirm that a discount code start date is valid
        """
        params = {
            'date': self.gc_250.date_start,
            'productCode': self.big_widget.code,
            'giftCardCode': self.gc_250.code
        }
        response = self.client.get('/api/get-price', params, format='json')
        expected_price = PriceApiTestCase.convert_to_dollars(self.bg_standard_price.price - self.gc_250.amount)
        self.assertEqual(response.data, {'price': expected_price})

    def test_gift_code_end_date_inclusiveness(self):
        """
        Confirm that a discount code end date is valid
        """
        params = {
            'date': self.gc_250.date_end,
            'productCode': self.big_widget.code,
            'giftCardCode': self.gc_250.code
        }
        response = self.client.get('/api/get-price', params, format='json')
        expected_price = PriceApiTestCase.convert_to_dollars(self.bg_2019_price.price - self.gc_250.amount)
        self.assertEqual(response.data, {'price': expected_price})

    def test_invalid_gift_code_does_not_affect_price(self):
        """
        Confirm that a bad discount code does not affect the price
        """
        params = {
            'date': self.bg_standard_price.date_end,
            'productCode': self.big_widget.code,
            'giftCardCode': 'Bogus Code'
        }
        response = self.client.get('/api/get-price', params, format='json')
        expected_price = PriceApiTestCase.convert_to_dollars(self.bg_standard_price.price)
        self.assertEqual(response.data, {'price': expected_price})

    def test_expired_gift_code_does_not_affect_price(self):
        """
        Confirm that a discount code does not affect the price if the code has expired
        """
        last_sale_date = datetime.strptime(self.gc_250.date_end, '%Y-%m-%d')
        expired_date = last_sale_date + timedelta(days=1)
        params = {
            'date': expired_date.strftime('%Y-%m-%d'),
            'productCode': self.big_widget.code,
            'giftCardCode': self.gc_250.code
        }
        response = self.client.get('/api/get-price', params, format='json')
        expected_price = PriceApiTestCase.convert_to_dollars(self.bg_2019_price.price)
        self.assertEqual(response.data, {'price': expected_price})

    def test_gift_code_does_not_take_price_below_zero(self):
        """
        If a gift card amount is more than the product price, confirm price is zero
        """
        params = {
            'date': self.gc_250.date_start,
            'productCode': self.sm_widget.code,
            'giftCardCode': self.gc_250.code
        }
        response = self.client.get('/api/get-price', params, format='json')
        expected_price = 0
        self.assertEqual(response.data, {'price': expected_price})

