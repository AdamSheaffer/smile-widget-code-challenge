from django.contrib import admin

# Register your models here.
from .models import (
    GiftCard,
    PriceSchedule,
    Product,
    ProductPrice
)

admin.site.register(GiftCard)
admin.site.register(PriceSchedule)
admin.site.register(Product)
admin.site.register(ProductPrice)
