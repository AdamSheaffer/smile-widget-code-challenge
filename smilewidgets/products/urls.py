from django.conf.urls import url

from .views import ProductApi

urlpatterns = [
    url(r'^get-price$', ProductApi.as_view())
]
