# _*_ encoding:utf-8 _*_
from django.db import models

from datetime import datetime

from news.models import news
from products.models import *
from users.models import UserProfile

# Create your models here.
class comments(models.Model):
    news = models.ForeignKey(news,verbose_name=u"新闻")
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    comment = models.CharField(max_length=200,verbose_name=u"评论")
    towards = models.ForeignKey('self',verbose_name=u"回复",null=True,blank=True)
    add_time = models.DateTimeField(default=datetime.now,verbose_name=u"发表时间")

    class Meta:
        verbose_name = u"评论"
        verbose_name_plural = verbose_name


class news_log(models.Model):
    news = models.ForeignKey(news, verbose_name=u"新闻")
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"浏览时间")

    class Meta:
        verbose_name = u"新闻浏览"
        verbose_name_plural = verbose_name


class product_log(models.Model):
    product = models.ForeignKey(agr_product, verbose_name=u"农产品")
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"浏览时间")

    class Meta:
        verbose_name = u"农产品浏览"
        verbose_name_plural = verbose_name


class recommend(models.Model):
    news = models.ForeignKey(news,verbose_name=u"新闻")
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    feedback = models.CharField(max_length=200,verbose_name=u"反馈")
    add_time = models.DateTimeField(default=datetime.now,verbose_name=u"生成时间")

    class Meta:
        verbose_name = u"新闻推荐"
        verbose_name_plural = verbose_name

class user_fav_news(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    news = models.ForeignKey(news,verbose_name=u"新闻")
    addtime = models.DateTimeField(default=datetime.now,verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"收藏新闻信息"
        verbose_name_plural = verbose_name

class user_fav_products(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    mf1 = models.ForeignKey(product_in_market,verbose_name=u"农产品-市场1",related_name="favmf1")
    mf2 = models.ForeignKey(product_in_market,verbose_name=u"农产品-市场2",null=True,related_name="favmf2")
    webtype = models.IntegerField(verbose_name=u"收藏类型",default=1)
    addtime = models.DateTimeField(default=datetime.now,verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"收藏农产品信息"
        verbose_name_plural = verbose_name