"""Nonglai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.views.generic import TemplateView
from extra_apps import xadmin
from users.views import *
from news.views import *

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^news/', include('news.urls')),
    url(r'^$', Index_View.as_view(), name="index"),
    url(r'^register/$', RegisterView.as_view(), name="register"),
    url(r'^login/$',LoginView.as_view(),name="login"),
    url(r'^logout/$',LogoutView.as_view(),name="logout"),
    url(r'^captcha/',include('captcha.urls')),
    url(r'^active/(?P<active_code>.*)/$',ActiveView.as_view(),name="active"),
    url(r'^forget/$',ForgetpwdView.as_view(),name="forget"),
    url(r'^reset/(?P<reset_code>.*)/$', ResetPwdView.as_view(),name="reset"),
    url(r'^Modify/$',ModifyView.as_view(),name="Modify"),
    url(r'^change_info/$',Change_infoView.as_view(),name="change_info"),
    url(r'^products/', include('products.urls')),
    url(r'^PersonalCenter/info/$',Change_infoView.as_view(),name="PersonalCenter"),
    url(r'^PersonalCenter/collection/$',MyCollectionView.as_view(),name="collection"),
    url(r'^PersonalCenter/comments/$',MyCommentView.as_view(),name="comments"),
    url(r'^PersonalCenter/favproducts/$',MyFavProducts.as_view(),name="favpro"),
]

# from news.views import NewsTag_View,news_list
# from django.contrib import admin

# urlpatterns = [
#     url(r'^xadmin/', xadmin.site.urls),
#     url(r'^$', TemplateView.as_view(template_name="index.html"), name="index"),
#     url(r'^register/$', user_register, name="register"),
#     url(r'^news/$',news_list, name="news")
# ]