# _*_ encoding:utf-8 _*_
from django.db import models

# Create your models here.
class product_category(models.Model):
    categoryid=models.IntegerField(verbose_name=u"种类ID",primary_key=True)
    categoryname=models.CharField(max_length=5,verbose_name=u"种类名称")

    class Meta:
        verbose_name = u"农产品种类"
        verbose_name_plural = verbose_name

class province(models.Model):
    provinceid = models.IntegerField(verbose_name=u"省份ID",primary_key=True)
    provincename = models.CharField(max_length=20,verbose_name=u"省份名称")

class market(models.Model):
    marketid=models.IntegerField(verbose_name=u"市场ID",primary_key=True)
    province = models.ForeignKey(province,verbose_name=u"省份")
    marketname = models.CharField(max_length=30, verbose_name=u"市场名称")

    class Meta:
        verbose_name = u"市场"
        verbose_name_plural = verbose_name


class agr_product(models.Model):
    productid=models.BigIntegerField(verbose_name=u"农产品ID",primary_key=True)
    category=models.ForeignKey(product_category,verbose_name=u"农产品种类")
    productname = models.CharField(max_length=20, verbose_name=u"农产品名称")

    class Meta:
        verbose_name = u"农产品"
        verbose_name_plural = verbose_name


class product_in_market(models.Model):
    product=models.ForeignKey(agr_product,verbose_name=u"农产品")
    market = models.ForeignKey(market, verbose_name=u"市场")


class date(models.Model):
    dateid = models.IntegerField(verbose_name=u"日期ID",primary_key=True)
    date=models.DateField(verbose_name=u"日期")
    year = models.IntegerField(verbose_name=u"年")
    month = models.IntegerField(verbose_name=u"月")
    monthday = models.IntegerField(verbose_name=u"日")
    weekday = models.IntegerField(verbose_name=u"星期几",null=True)

    class Meta:
        verbose_name = u"日期"
        verbose_name_plural = verbose_name


class product_price(models.Model):
    marketproduct = models.ForeignKey(product_in_market, verbose_name=u"农产品")
    date = models.ForeignKey(date, verbose_name=u"日期")
    price = models.DecimalField(verbose_name=u"价格",max_digits=6,decimal_places=2)

    class Meta:
        verbose_name = u"农产品价格"
        verbose_name_plural = verbose_name

class price_predict1(models.Model):
    id = models.IntegerField(verbose_name="ID",primary_key=True)
    marketproduct = models.ForeignKey(product_in_market, verbose_name=u"农产品")
    price = models.DecimalField(verbose_name=u"预测价格",max_digits=6,decimal_places=2)
    sequenceid = models.IntegerField(verbose_name=u"序列号",null=True)
    date = models.ForeignKey(date,verbose_name=u"日期id",null=True)

    class Meta:
        verbose_name = u"农产品价格预测1"
        verbose_name_plural = verbose_name

class price_predict2(models.Model):
    id = models.IntegerField(verbose_name="ID", primary_key=True)
    marketproduct = models.ForeignKey(product_in_market, verbose_name=u"农产品")
    price = models.DecimalField(verbose_name=u"预测价格",max_digits=6,decimal_places=2)
    sequenceid = models.IntegerField(verbose_name=u"序列号",null=True)
    date = models.ForeignKey(date, verbose_name=u"日期id",null=True)

    class Meta:
        verbose_name = u"农产品价格预测2"
        verbose_name_plural = verbose_name