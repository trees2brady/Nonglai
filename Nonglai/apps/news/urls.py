from django.conf.urls import url
from .views import *

app_name = 'news'
urlpatterns = [
    # url(r'^list/(?P<tagid>[0-9]+)/$', News_list.as_view(), name="news_list"),
    url(r'^details/(?P<newsid>[0-9]+)/$', News_details.as_view(), name="news_details"),
    url(r'^news_list/(?P<tagid>[0-9])/$', News_list.as_view(), name="news_list"),
    # url(r'^details/(?P<newsid>[0-9]+)/$', views.news_details, name="news_details"),
    url(r'^my_fav_news/',My_Fav_News.as_view(), name="my_fav_news"),
    url(r'^add_comment/',Add_comment.as_view(), name="add_comment"),
    url(r'^search_result/',Search_Result.as_view(), name="search_result"),
    url(r'^hot_label/(?P<searchstr>.+?)/$', Hot_label.as_view(), name="hot_label"),
]