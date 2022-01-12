# _*_ encoding:utf-8 _*_

from django import forms
from captcha.fields import CaptchaField

class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True,min_length=6)

class RegisterForm(forms.Form):
    username = forms.CharField(required=True)
    password1 = forms.CharField(required=True, min_length=6)
    password2 = forms.CharField(required=True, min_length=6)
    # email = forms.EmailField(required=True)
    checkword = CaptchaField(error_messages={"invalid":u"验证码错误！"})

class ForgetpwdForm(forms.Form):
    email = forms.EmailField(required=True)
    checkword = CaptchaField(error_messages={"invalid":u"验证码错误！"})


class ResetpwdForm(forms.Form):
    newpwd1 = forms.CharField(required=True,min_length=6)
    newpwd2 = forms.CharField(required=True, min_length=6)