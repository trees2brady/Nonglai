# _*_ encoding:utf-8 _*_

from django.conf.urls import url
from .views import *

app_name = 'products'
urlpatterns = [
    url(r'^price_inquiry/', Price_inquiry.as_view(), name="price_inquiry"),
    # url(r'^price_analysis/', Price_analysis.as_view(), name="price_analysis"),
    url(r'^price_analysis1/', Price_analysis1.as_view(), name="price_analysis1"),
    url(r'^price_analysis2/', Price_analysis2.as_view(), name="price_analysis2"),
    url(r'^price_analysis3/', Price_analysis3.as_view(), name="price_analysis3"),
    url(r'^price_analysis4/', Price_analysis4.as_view(), name="price_analysis4"),
    url(r'^fav_product/', FavProductView.as_view(), name="fav_product"),
    url(r'^price_predict/', Price_predict.as_view(), name="price_predict"),
]