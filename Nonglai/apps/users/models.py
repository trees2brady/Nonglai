# _*_ encoding:utf-8 _*_
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

class UserProfile(AbstractUser):
    nick_name = models.CharField(max_length=50, verbose_name=u'昵称', default=u"" )
    birthday = models.DateField(verbose_name=u'生日', null=True, blank=True)
    gender = models.CharField(max_length=6, choices=(("male", u"男"), ("female", "女")), default=None,null=True)
    address = models.CharField(max_length=100,verbose_name=u'地址', default=u"")
    mobile = models.CharField(max_length=11,verbose_name=u'手机号', null=True, blank=True)
    image = models.ImageField(upload_to="image/%Y/%m", default=u"image/default.png", max_length=100)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class EmailVerifyRecord(models.Model):
    code = models.CharField(max_length=20, verbose_name=u"验证码")
    email = models.EmailField(max_length=50, verbose_name=u"邮箱")
    send_type = models.CharField(max_length=10,verbose_name=u"验证码类型", choices=(("register", "注册"), ("forget", "找回密码")))
    send_time = models.DateTimeField(default=datetime.now,verbose_name=u"发送时间") #需要注意now后面的括号，有括号就会在生成本数据表的时候生成，没有就会在实例化的时候生成

    class Meta:
        verbose_name = u"邮箱验证码"
        verbose_name_plural = verbose_name