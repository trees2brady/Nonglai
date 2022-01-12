# _*_ encoding:utf-8 _*_
from django.db import models

# Create your models here.
class tag(models.Model):
    tagid=models.IntegerField(verbose_name=u"新闻模块ID",primary_key=True)
    tagname=models.CharField(max_length=5,verbose_name=u"新闻模块名")

    class Meta:
        verbose_name = u"新闻模块"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.tagname


class news(models.Model):
    newsid=models.IntegerField(verbose_name=u"新闻ID",primary_key=True)
    newstag=models.ForeignKey(tag,verbose_name=u"新闻模块")
    title = models.CharField(max_length=50, verbose_name=u"新闻标题")
    url = models.CharField(null=True,max_length=200,verbose_name=u"新闻URL")
    newsdate = models.DateTimeField(null=True,verbose_name=u"发布时间")
    resource = models.CharField(max_length=20,null=True,verbose_name=u"新闻来源")
    newscontent = models.TextField(default="",verbose_name=u"新闻主体")

    class Meta:
        verbose_name = u"新闻"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class knearest(models.Model):
    id = models.IntegerField(verbose_name="ID",primary_key=True)
    first = models.IntegerField(verbose_name="first")
    second = models.IntegerField(verbose_name="second")
    third = models.IntegerField(verbose_name="third")
    fourth = models.IntegerField(verbose_name="fourth")
    fifth = models.IntegerField(verbose_name="fifth")

    class Meta:
        verbose_name = u"最近5个新闻"
        verbose_name_plural = verbose_name


class postings(models.Model):
    term = models.CharField(max_length=255,primary_key=True,verbose_name=u"词项")
    df = models.IntegerField(verbose_name=u"出现频数")
    docs = models.TextField(verbose_name=u"出处时间")

    class Meta:
        verbose_name = u"排序条件"
        verbose_name_plural = verbose_name