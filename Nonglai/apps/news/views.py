from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.db.models import *

from .models import *
from products.models import *
from operation.models import user_fav_news,comments,news_log,user_fav_products
from users.models import UserProfile
from products.models import *

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from pure_pagination import PageNotAnInteger,EmptyPage,Paginator
from .search_engine import *
import json,jieba,MySQL,functions,random


class Index_View(View):
    def get(self,request):
        hot_news = functions.get_hot_news()
        hot_comments = functions.get_hot_comnent()
        new_news = news.objects.filter().order_by("-newsdate")[:5]
        gjzz_news = news.objects.filter(newstag__tagid='1').order_by("-newsdate")[:3]
        hyzx_news = news.objects.filter(newstag__tagid='2').order_by("-newsdate")[:3]
        nybk_news = news.objects.filter(newstag__tagid='3').order_by("-newsdate")[:3]
        qtzx_news = news.objects.filter(newstag__tagid='4').order_by("-newsdate")[:3]
        hot_labels = postings.objects.all().order_by("-df")[:40]
        #获取价格播报数据
        price = product_price.objects.filter(marketproduct__market="20547").order_by("-date")[:10]

        return render(request, "index.html", {
            "hot_news":hot_news,
            "new_news":new_news,
            "gjzz_news":gjzz_news,
            "hyzx_news":hyzx_news,
            "nybk_news":nybk_news,
            "qtzx_news":qtzx_news,
            "hot_labels":hot_labels,
            "price":price,
            "hot_comments":hot_comments,
        })

class NewsTag_View(View):
    def get(self, request):
        newstags = tag.objects.all()
        return render(request,"news.html",{
            "newstags" : newstags
        })

class News_list(View):
    def get(self,request,tagid='0'):
        hot_news = functions.get_hot_news()
        try:
            page = request.GET.get('page',1)
        except:
            page = 1
        if tagid=='0':
            newstags = tag.objects.get(pk=0)
            newslist = news.objects.all().order_by('-newsdate')
        else:
        #newstags = tag.objects.get(pk=tagid)
            newstags = tag.objects.get(pk=tagid)
            newslist = news.objects.filter(newstag__tagid=tagid)
        p = Paginator(newslist,request=request,per_page=5)
        paged_news = p.page(page)

        sqlcon = MySQL.MySQL()
        maxid = sqlcon.sql_execute("select max(newsid) from news_news")[0][0]
        randnews=[]
        i=1
        while i <= 5:
            randnews_i = news.objects.filter(newsid=random.randint(0,maxid))
            if len(randnews_i)==1:
                randnews.append(randnews_i[0])
                i+=1

        return render(request, "news_list.html", {
            "newstags": newstags,
            "newslist": paged_news,
            "hotnews":hot_news,
            "randnews":randnews,
        })

class Hot_label(View):
    def get(self,request,searchstr):
        sqlcon = MySQL.MySQL()
        maxid = sqlcon.sql_execute("select max(newsid) from news_news")[0][0]
        randnews = []
        i = 1
        while i <= 5:
            randnews_i = news.objects.filter(newsid=random.randint(0, maxid))
            if len(randnews_i) == 1:
                randnews.append(randnews_i[0])
                i += 1
        se = SearchEngine('./log/config.ini', 'utf-8')
        flag, rs = se.search(searchstr, 0)
        hot_news = functions.get_hot_news()
        if flag == 1:
            newslist = []
            for result in rs:
                one_news = news.objects.filter(newsid=result[0])
                newslist.append(one_news[0])

            return render(request, "search_result.html", {
                "newslist": newslist,
                "randnews": randnews,
                "hotnews": hot_news,
                "search_str": searchstr,
            })
        else:
            return render(request, "search_result.html", {
                "msg": "无结果！",
                "randnews": randnews,
                "hotnews": hot_news,
                "search_str": searchstr,
            })

class Search_Result(View):
    def post(self,request):
        sqlcon = MySQL.MySQL()
        maxid = sqlcon.sql_execute("select max(newsid) from news_news")[0][0]
        randnews = []
        i = 1
        while i <= 5:
            randnews_i = news.objects.filter(newsid=random.randint(0, maxid))
            if len(randnews_i) == 1:
                randnews.append(randnews_i[0])
                i += 1
        searchstr = request.POST.get('search_box',"")
        se = SearchEngine('./log/config.ini', 'utf-8')
        hot_news = functions.get_hot_news()
        flag, rs = se.search(searchstr, 0)
        if flag == 1:
            newslist = []
            for result in rs:
                one_news = news.objects.filter(newsid=result[0])
                newslist.append(one_news[0])

            return render(request, "search_result.html", {
                "newslist": newslist,
                "search_str":searchstr,
                "randnews": randnews,
                "hotnews":hot_news
            })
        else:
            return render(request, "search_result.html", {
                "msg":"无结果！",
                "search_str": searchstr,
                "randnews": randnews,
                "hotnews": hot_news
            })

class News_details(View):
    def get(self,request,newsid):
        newsdetails = news.objects.get(newsid=newsid)
        newscomments = comments.objects.filter(news_id=newsid).order_by('-add_time')
        # towardsusers = []
        # for comment in newscomments:
        #     towardsusers.append(comment.user)
        newslog = news_log()
        if request.user.is_authenticated():
            newslog.user = request.user
            useridstr = str(request.user.id)
        else:
            newslog.user = UserProfile.objects.filter(id=1)[0]
            useridstr = "1"
        newslog.news = newsdetails
        newslog.save()
        has_fav = False
        nearest_list = knearest.objects.filter(id=newsid)
        nearest_news = []
        nearest_news.append(news.objects.filter(newsid=nearest_list[0].first)[0])
        nearest_news.append(news.objects.filter(newsid=nearest_list[0].second)[0])
        nearest_news.append(news.objects.filter(newsid=nearest_list[0].third)[0])
        nearest_news.append(news.objects.filter(newsid=nearest_list[0].fourth)[0])
        nearest_news.append(news.objects.filter(newsid=nearest_list[0].fifth)[0])
        mysql = MySQL.MySQL()
        sqlstr = "SELECT DISTINCT news_id,count(news_id) from operation_news_log where news_id!="+str(newsid)+" and user_id in (SELECT DISTINCT user_id from operation_news_log where news_id = "+str(newsid)+" and user_id!="+useridstr+") group by news_id ORDER BY count(news_id) desc"
        user_like_list = mysql.sql_execute(sqlstr)
        user_like_news = []
        for each_news in user_like_list[:5]:
            user_like_news.append(news.objects.filter(newsid=each_news[0])[0])
        try:
            if user_fav_news.objects.filter(news=newsid,user=request.user):
                has_fav = True
        except:
            pass
        return render(request, "news_details.html", {
            "newsdetails": newsdetails,
            "has_fav":has_fav,
            "commentscount": len(newscomments),
            "newscomments":newscomments,
            "nearestnews":nearest_news,
            "user_like_news":user_like_news,
        })

class My_Fav_News(View):
    def get(self,requset):
        return render(requset,'login.html',{})
    def post(self,request):
        news_id = request.POST.get('newsid','0')
        #判断用户是否登录
        if not request.user.is_authenticated():
            return HttpResponse(json.dumps({'status':'fail','msg':'请先登录'}),content_type='application/json')
        else:
        #判断用户是否已收藏
            exist_record = user_fav_news.objects.filter(user=request.user,news=int(news_id))
            if exist_record:
                #若用户已收藏，则改为不收藏
                exist_record.delete()
                return HttpResponse(json.dumps({"status": "success", "msg": "收藏"}), content_type='application/json')
            else:
                fav_news = user_fav_news()
                fav_news.user = request.user
                fav_news.news = news.objects.filter(newsid=int(news_id))[0]
                fav_news.save()
                return HttpResponse(json.dumps({"status":"success", "msg":"已收藏"}), content_type='application/json')

class Add_comment(View):
    def get(self, requset):
        return render(requset, 'login.html', {})

    def post(self, request):
        try:
            news_id = request.POST.get('newsid', 0)
            comment = request.POST.get('comments','0')
            reply = request.POST.get('reply',None)
            # exist_record = user_fav_news.objects.filter(user=request.user, news=int(news_id))
            # newsdetails = news.objects.get(newsid=news_id)
            # if exist_record:
            #     # 若用户已收藏，则改为不收藏
            #     exist_record.delete()
            #     # return render(request,"news_details.html",{"newsdetails":newsdetails})
            #     return HttpResponse(json.dumps({"status": "success", "msg": "收藏"}),
            #                         content_type='application/json')
            # else:
            newcomment = comments()
            # this_news = news.objects.filter(newsid=int(news_id))
            newcomment.user = request.user
            if reply is not None:
                newcomment.towards = comments.objects.filter(id=reply)[0]
            newcomment.news = news.objects.get(newsid=news_id)
            newcomment.comment = comment
            newcomment.save()
        except Exception as e:
            print(e)
            return HttpResponse(json.dumps({"status": "fail", "msg": "失败"}),content_type='application/json')
        return HttpResponse(json.dumps({"status": "success", "msg": "已收藏"}),content_type='application/json')
# try:
#         # 实例化调度器
#     scheduler = BackgroundScheduler()
#         # 调度器使用DjangoJobStore()
#     scheduler.add_jobstore(DjangoJobStore(), "default")
#         # 'cron'方式循环，周一到周五，每天9:30:10执行,id为工作ID作为标记
#         # ('scheduler',"interval", seconds=1)  #用interval方式循环，每一秒执行一次
#     @register_job(scheduler, 'cron', day_of_week='mon-fri', hour='20', minute='40', second='10',id='task_time')
#     def test_job():
#             print("I am a test!")
#       # 监控任务
#     register_events(scheduler)
#       # 调度器开始
#     scheduler.start()
# except Exception as e:
#     print(e)
#     # 报错则调度器停止执行
#     scheduler.shutdown()


# def news_list(request,tagid):
#     try:
#         page = request.GET.get('page',1)
#     except:
#         tagid = '0'
#         page = 1
#     if tagid=='0':
#         newstags = tag.objects.filter(pk=tagid)
#         newslist = news.objects.all().order_by('-newsdate')
#     else:
#     #newstags = tag.objects.get(pk=tagid)
#         newstags = tag.objects.filter(pk=tagid)
#         newslist = news.objects.filter(newstag_id=tagid)
#     p = Paginator(newslist,request=request,per_page=5)
#     paged_news = p.page(page)
#
#     return render(request, "news_list.html", {
#         "newstags": newstags,
#         "newslist": paged_news,
#     })

# def news_details(request, newsid):
#     newsdetails = news.objects.get(newsid=newsid)
#     return render(request, "news_details.html", {
#         "newsdetails": newsdetails,
#     })

