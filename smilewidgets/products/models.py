from django.db import models
from datetime import date

class Product(models.Model):
    name = models.CharField(max_length=25, help_text='Customer facing name of product')
    code = models.CharField(max_length=10, help_text='Internal facing reference to product')
    
    def __str__(self):
        return '{} - {}'.format(self.name, self.code)


class GiftCard(models.Model):
    code = models.CharField(max_length=30)
    amount = models.PositiveIntegerField(help_text='Value of gift card in cents')
    date_start = models.DateField()
    date_end = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return '{} - {}'.format(self.code, self.formatted_amount)
    
    @property
    def formatted_amount(self):
        return '${0:.2f}'.format(self.amount / 100)


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, related_name='product_price', on_delete=models.CASCADE)
    price = models.PositiveIntegerField(help_text='Price of product in cents')
    date_start = models.DateField(default=date.min)
    date_end = models.DateField(default=date.max)
    description = models.CharField(max_length=50, help_text='Customer facing price name')

    def __str__(self):
        return '{}: {}'.format(self.description, self.price / 100)
