# _*_ encoding:utf-8 _*_

from django.db.models import *
from news.models import news
from operation.models import *

def get_hot_news():
    hot_news_log = news_log.objects.all().values('news').annotate(total=Count('user')).order_by('-total')[:5]
    hot_news = []
    for each_hot_news in hot_news_log:
        hot_news.append(news.objects.filter(newsid=each_hot_news['news'])[0])
    return hot_news

def get_hot_comnent():
    hot_comment_id = comments.objects.all().values('towards').annotate(total=Count('id')).order_by('-total')[:5]
    hot_comments = []
    for each_hot_news in hot_comment_id:
        if each_hot_news['towards']:
            hot_comments.append(comments.objects.filter(id=each_hot_news['towards'])[0])
    return hot_comments