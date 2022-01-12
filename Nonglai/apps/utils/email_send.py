# _*_ encoding:utf-8 _*_

from users.models import EmailVerifyRecord
from random import Random
from django.core.mail import send_mail
from Nonglai.settings import EMAIL_FROM

def send_register_email(email,sendtype="register"):
    email_record = EmailVerifyRecord()
    code = get_randomstr(8)
    email_record.code = code
    email_record.email = email
    email_record.send_type = sendtype
    email_record.save()

    if sendtype=="register":
        email_title = u"农莱小站注册激活邮件"
        email_body = u"请点击链接激活你的帐号：http://127.0.0.1:8000/active/"+code

        has_send = send_mail(email_title,email_body,EMAIL_FROM,[email])
        return has_send

def send_resetpwd_email(email,sendtype="forget"):
    email_record = EmailVerifyRecord()
    code = get_randomstr(8)
    email_record.code = code
    email_record.email = email
    email_record.send_type = sendtype
    email_record.save()

    if sendtype=="forget":
        email_title = u"农莱小站找回密码邮件"
        email_body = u"请点击链接重置你的密码：http://127.0.0.1:8000/reset/"+code

        has_send = send_mail(email_title,email_body,EMAIL_FROM,[email])
        return has_send

def get_randomstr(strlen=8):
    randomstr = ""
    chars = "AaBbCcDdEeFfGgHhIiJiKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789"
    length = len(chars)-1
    random = Random()
    for i in range(strlen):
        randomstr+=chars[random.randint(0,length)]
    return randomstr