from django.contrib import admin

# Register your models here.
from .models import (
    GiftCard,
    Product,
    ProductPrice
)

admin.site.register(GiftCard)
admin.site.register(Product)
admin.site.register(ProductPrice)
