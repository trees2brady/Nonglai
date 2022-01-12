from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from .models import *
import datetime,time,json
import numpy as np
from scipy.stats import mode
from django.contrib import messages
from MySQL import *
from news.models import news
from operation.models import user_fav_products
from news.search_engine import *
# from sklearn.metrics import r2_score
# Create your views here.

#相关新闻推荐
class News_rec(View):
    def __init__(self, seacrchstr, starttime, endtime):
        self.seacrchstr = seacrchstr
        if type(starttime)==type("1"):
            starttime=datetime.datetime.strptime(starttime,"%Y-%m-%d")
        self.starttime = starttime
        if type(endtime)==type("1"):
            endtime=datetime.datetime.strptime(endtime,"%Y-%m-%d")
        self.endtime= endtime

    def findnews(self):
        se = SearchEngine('./log/config.ini', 'utf-8')
        flag, rs = se.search(self.seacrchstr, 0)
        newslist = []
        if flag == 1:
            msg=""
            for result in rs:
                one_news = news.objects.filter(newsid=result[0],newsdate__range=(self.starttime-datetime.timedelta(days=180),self.endtime+datetime.timedelta(days=180)))
                if one_news:
                    newslist.append(one_news[0])
        return newslist

class ProductBaseView(View):
    db = MySQL()
    def get_all_base_data(self):
        return agr_product.objects.all(),product_category.objects.all(),market.objects.all(),province.objects.all()

    def get_default(self):
        products, categorys, markets, provinces = self.get_all_base_data()
        price_get_d = product_price.objects.filter(marketproduct__product__productid=13233,marketproduct__market__marketid=20547,
                                                    date__date__range=(datetime.date.today() - datetime.timedelta(days=30),datetime.date.today()))
        productname_d = agr_product.objects.get(productid=13233)
        marketname_d = market.objects.get(marketid=20547)
        return products, categorys, markets, provinces, price_get_d, productname_d, marketname_d

    def get_post_info(self,request):
        return request.POST.get("product", ""),request.POST.get("market", ""),request.POST.get("startTime",""),request.POST.get("endTime","")

    def get_market_list(self,products_get,province_,data):
        if products_get == "":
            markets = market.objects.filter(province__provinceid=province_)
            for each_market in markets:
                data.update({each_market.marketid: each_market.marketname})
        else:
            markets = self.db.sql_execute(
                "select marketid,marketname from products_market join products_product_in_market on marketid = market_id where product_id = " + products_get + " and province_id =" + province_)
            for each_market in markets:
                data.update({each_market[0]: each_market[1]})
        return data

    def get_product_list(self,markets_get,category_,data):
        if markets_get == "":
            products = agr_product.objects.filter(category_id=category_)
            for each_product in products:
                data.update({each_product.productid: each_product.productname})
        else:
            products = self.db.sql_execute(
                "select productid,productname from products_agr_product join products_product_in_market on product_id = productid where market_id = " + markets_get + " and category_id =" + category_)
            for each_product in products:
                data.update({each_product[0]: each_product[1]})
        return data

class ProductAnalysisBaseView(ProductBaseView):
    def get_time_set2(self,price_get):
        time_set2_d = []
        time_set_d = list(price_get.values_list('date__date', flat=True))
        for j in time_set_d:
            time_set2_d.append(j.strftime("%Y-%m-%d"))
        return time_set2_d

    def get_np_data(self,price_set_d):
        price_np = np.array(price_set_d)
        analysis = {}
        analysis['max'] = np.max(price_np)
        analysis['min'] = np.min(price_np)
        analysis['mean'] = round(np.mean(price_np), 2)
        analysis['median'] = round(np.median(price_np),2)
        analysis['cv'] = round(np.std(price_np) / np.mean(price_np), 2)
        analysis['std'] = np.std(price_np)
        analysis['mode'] = mode(price_np)[0][0]
        return analysis

#价格查询
class Price_inquiry(ProductBaseView):
    def get(self,request):
        products, categorys, markets, provinces,price_get_d,productname_d,marketname_d = self.get_default()
        # 返回页面
        return render(request, "price_inquiry.html", {
            "products":products,
            "categories":categorys,
            "markets":markets,
            "prices":price_get_d,
            "provinces": provinces,
            # 返回图表默认名称信息
            "starttime": datetime.date.today()-datetime.timedelta(days=30),
            "endtime": datetime.date.today(),
            "productid": "13233",
            "marketid": "20547",
            "start_time": datetime.date.today()-datetime.timedelta(days=30),
            "end_time": datetime.date.today(),
            "product_post": productname_d,
            "market_post": marketname_d,
        })

    def post(self,request):
        x=request.POST.get("btn_submit", "false")
        products_get, markets_get, startTime, endTime = self.get_post_info(request)
        # 查询功能
        if(request.POST.get("btn_submit", "false")=='true'):
            products_gets = agr_product.objects.get(productid = products_get)
            markets_gets = market.objects.get(marketid= markets_get)
            starttime_get = datetime.datetime.strptime(startTime,"%Y-%m-%d").date()
            endtime_get = datetime.datetime.strptime(endTime,"%Y-%m-%d").date()

            productmarket_get = product_in_market.objects.filter(product = products_get, market=markets_get)
            if(len(productmarket_get)>0):
                products, categorys, markets, provinces = self.get_all_base_data()
                price_get = product_price.objects.filter(marketproduct__product=products_get,marketproduct__market=markets_get,date__date__range=(starttime_get, endtime_get))
                return render(request, "price_inquiry.html",{
                    "prices":price_get,
                    "products": products,
                    "categories": categorys,
                    "markets": markets,
                    "start_time":starttime_get,
                    "end_time":endtime_get,
                    "starttime": request.POST.get("startTime",""),
                    "endtime": request.POST.get("endTime",""),
                    "productid":products_get,
                    "marketid":markets_get,
                    "product_post":products_gets,
                    "market_post":markets_gets,
                    "provinces":provinces,
                })
            else:
                # 获取默认图表信息
                products, categorys, markets, provinces, price_get_d, productname_d, marketname_d = self.get_default()
                # 返回页面
                return render(request, "price_inquiry.html", {
                    "products": products,
                    "categories": categorys,
                    "markets": markets,
                    "prices": price_get_d,
                    "provinces": provinces,
                    # 返回图表默认名称信息
                    "start_time": datetime.date.today()-datetime.timedelta(days=30),
                    "end_time": datetime.date.today(),
                    "product_post": productname_d,
                    "market_post": marketname_d,
                    "miss": "不存在此信息，请重新选择！",
                    "productid": "13233",
                    "marketid": "20547",
                    "starttime": datetime.date.today()-datetime.timedelta(days=30),
                    "endtime": datetime.date.today(),
                })

        # 省份与市场选择框相关联
        elif(request.POST.get("verify", "false")=="yes"):
            data = {"status": "success"}
            province_ = request.POST.get("province", "")
            data['market'] = self.get_market_list(products_get,province_,{})
            return HttpResponse(json.dumps(data), content_type='application/json')

        # 产品种类与产品名称选择框相关联
        else:
            data = {"status": "success"}
            category_ = request.POST.get("category", "")
            data['product'] = self.get_product_list(markets_get,category_,{})
            return HttpResponse(json.dumps(data), content_type='application/json')

class Price_analysis1(ProductAnalysisBaseView):
    def get(self, request):
        products, categorys, markets, provinces, price_get_d, productname_d, marketname_d = self.get_default()
        time_set2_d = self.get_time_set2(price_get_d)
        price_set_d = []
        for i in price_get_d:
            price_set_d.append(float(i.price))
         # 分析信息
        analysis = self.get_np_data(price_set_d)
        #推荐新闻
        searchstr_d = productname_d.productname
        news_d = News_rec(searchstr_d, datetime.date.today()-datetime.timedelta(days=30), datetime.date.today())
        newslist_d = news_d.findnews()
        # 返回页面
        return render(request, "price_analysis1.html", {
            "products": products,
            "categories": categorys,
            "markets": markets,
            "provinces": provinces,
            "newslist": newslist_d,
            # 返回图表默认信息
            "time_set": json.dumps(time_set2_d),
            "price_set": price_set_d,
            "analysis": analysis,
            # 返回图表默认名称信息
            "start_time": datetime.date.today()-datetime.timedelta(days=30),
            "end_time": datetime.date.today(),
            "product_post": productname_d,
            "market_post": marketname_d,

        })

    def post(self, request):
        products_get, markets_get, startTime, endTime = self.get_post_info(request)
        if (request.POST.get("btn_submit", "false") == "true"):
            productname = agr_product.objects.get(productid=products_get)
            marketname = market.objects.get(marketid=markets_get)
            if startTime.find("-")>-1:
                starttime_get = datetime.datetime.strptime(startTime, "%Y-%m-%d").date()
                endtime_get = datetime.datetime.strptime(endTime, "%Y-%m-%d").date()
            else:
                starttime_get = datetime.datetime.strptime(startTime, "%Y年%m月%d日").date()
                endtime_get = datetime.datetime.strptime(endTime, "%Y年%m月%d日").date()
            productmarket_get = product_in_market.objects.filter(product=products_get, market=markets_get)
            x=len(productmarket_get)
            price_get = product_price.objects.filter(marketproduct__product__productid=int(products_get),
                                                     marketproduct__market=int(markets_get),
                                                     date__date__range=(starttime_get, endtime_get))
            if (len(price_get) > 0):
                products, categorys, markets, provinces = self.get_all_base_data()

                time_set2 = self.get_time_set2(price_get)
                price_set = []
                for i in price_get:
                    price_set.append(float(i.price))
                # 分析部分
                analysis = self.get_np_data(price_set)

                # 获取推荐新闻
                searchstr = productname.productname
                news = News_rec(searchstr, starttime_get, endtime_get)
                newslist = news.findnews()

                return render(request, "price_analysis1.html", {
                    "prices": price_get,

                    # 返回表单信息
                    "products": products,
                    "categories": categorys,
                    "provinces": provinces,
                    "markets": markets,
                    "newslist": newslist,

                    # 返回图表信息
                    "time_set": json.dumps(time_set2),
                    # "time_set": time_set,
                    "price_set": price_set,
                    "analysis": analysis,

                    # 返回图表名称信息
                    "start_time": starttime_get,
                    "end_time": endtime_get,
                    "product_post": productname,
                    "market_post": marketname,
                })

            else:
                products, categorys, markets, provinces, price_get_d, productname_d, marketname_d = self.get_default()
                time_set2_d = self.get_time_set2(price_get_d)
                price_set_d = []
                for i in price_get_d:
                    price_set_d.append(float(i.price))
                analysis = self.get_np_data(price_set_d)
                searchstr = productname.productname
                news = News_rec(searchstr, starttime_get, endtime_get)
                newslist = news.findnews()

                return render(request, "price_analysis1.html", {
                    "products": products,
                    "categories": categorys,
                    "markets": markets,
                    "provinces": provinces,
                    "newslist": newslist,
                    # "time_set": '',
                    # "price_set": '',

                    # 返回图表默认信息
                    "time_set": json.dumps(time_set2_d),
                    "price_set": price_set_d,
                    "analysis": analysis,

                    # 返回图表默认名称信息
                    "start_time": datetime.date.today()-datetime.timedelta(days=30),
                    "end_time": datetime.date.today(),
                    "product_post": productname_d,
                    "market_post": marketname_d,
                    "miss": "不存在此信息，请重新选择！"
                })

        # 省份与市场选择框相关联
        elif (request.POST.get("verify", "false") == "yes"):
            data = {"status": "success"}
            province_ = request.POST.get("province", "")
            data['market'] = self.get_market_list(products_get, province_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')

        # 产品种类与产品名称选择框相关联
        else:
            data = {"status": "success"}
            category_ = request.POST.get("category", "")
            data['product'] = self.get_product_list(markets_get, category_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')

#同一产品在不同年份价格比较
class Price_analysis2(ProductAnalysisBaseView):
    def get_time_set2(self,price_get):
        time_set2_d = []
        time_set_d = list(price_get.values_list('date__date', flat=True))
        for j in time_set_d:
            time_set2_d.append(j.strftime("%m-%d"))
        return time_set2_d

    def get_default(self):
        products, categorys, markets, provinces = self.get_all_base_data()
        price_get_d1 = product_price.objects.filter(marketproduct__product=13233, marketproduct__market=20547,
                                                    date__date__range=("2018-1-31", "2018-12-31"))
        price_get_d2 = product_price.objects.filter(marketproduct__product=13233, marketproduct__market=20547,
                                                    date__date__range=("2019-1-31", "2019-12-31"))
        productname_d = agr_product.objects.get(productid=13233)
        marketname_d = market.objects.get(marketid=20547)
        time_set2_d = self.get_time_set2(price_get_d1)
        return products,categorys, markets, provinces,price_get_d1,price_get_d2,productname_d,marketname_d,time_set2_d

    def get(self,request):
        products, categorys, markets, provinces, price_get_d1, price_get_d2, productname_d, marketname_d, time_set2_d = self.get_default()
        price_set_d1 = []
        for i in price_get_d1:
            price_set_d1.append(float(i.price))
        price_set_d2 = []
        for j in price_get_d2:
            price_set_d2.append(float(j.price))
        #分析信息
        analysis1 = self.get_np_data(price_set_d1)
        analysis2 = self.get_np_data(price_set_d2)

        #推荐新闻
        searchstr_d = productname_d.productname
        news_d1 = News_rec(searchstr_d,"2018-1-31", "2018-12-31")
        news_d2 = News_rec(searchstr_d, "2019-1-31", "2019-12-31")
        newslist_d1 = news_d1.findnews()
        newslist_d2 = news_d2.findnews()
        newslist_d = newslist_d1+newslist_d2
         #返回页面
        return render(request, "price_analysis2.html", {
            "products":products,
            "categories":categorys,
            "markets":markets,
            "provinces":provinces,
            "newslist":newslist_d,

            # 返回图表默认信息
            "time_set": json.dumps(time_set2_d),
            "price_set1": price_set_d1,
            "price_set2": price_set_d2,
            "analysis1":analysis1,
            "analysis2": analysis2,

            # 返回图表默认名称信息
            "start_time": "2018年",
            "end_time": "2019年",
            "product_post": productname_d,
            "market_post": marketname_d,
        })

    def post(self,request):
        x=request.POST.get("btn_submit", "false")
        y = request.POST.get("verify", "false")
        products_get, markets_get, starttime_get, endtime_get = self.get_post_info(request)
        if(request.POST.get("btn_submit", "false")=="true"):
            productname = agr_product.objects.get(productid=products_get)
            marketname = market.objects.get( marketid=markets_get)
            starttime_get_num = starttime_get[0:4]
            endtime_get_num = endtime_get[0:4]
            productmarket_get = product_in_market.objects.filter(product = products_get, market=markets_get)
            price_get1 = product_price.objects.filter(marketproduct__product__productid=int(products_get),
                                                      marketproduct__market=int(markets_get),
                                                      date__year=int(starttime_get_num))
            price_get2 = product_price.objects.filter(marketproduct__product__productid=int(products_get),
                                                      marketproduct__market=int(markets_get),
                                                      date__year=int(endtime_get_num))

            if(len(price_get1)>0 or len(price_get2)>0):
                products, categorys, markets, provinces = self.get_all_base_data()
                time_set2 = self.get_time_set2(price_get1)
                price_set1=[]
                for i in price_get1:
                    price_set1.append(float(i.price))
                price_set2 = []
                for k in price_get2:
                    price_set2.append(float(k.price))

                # 分析信息
                analysis1 = self.get_np_data(price_set1)
                analysis2 = self.get_np_data(price_set2)

                # 推荐新闻
                start1 = starttime_get_num+"-1-1"
                end1 = starttime_get_num+"-12-31"
                start2 = endtime_get_num + "-1-1"
                end2 = endtime_get_num + "-12-31"
                searchstr = productname.productname
                news1 = News_rec(searchstr, start1, end1)
                news2 = News_rec(searchstr, start2, end2)
                newslist1 = news1.findnews()
                newslist2 = news2.findnews()
                newslist = newslist1 + newslist2

                return render(request, "price_analysis2.html",{

                    # 返回表单信息
                    "products": products,
                    "categories": categorys,
                    "provinces":provinces,
                    "markets": markets,
                    "newslist":newslist,

                    # 返回图表信息
                    "time_set": json.dumps(time_set2),
                    "price_set1": price_set1,
                    "price_set2": price_set2,
                    "analysis1": analysis1,
                    "analysis2": analysis2,

                    # 返回图表名称信息
                    "start_time":starttime_get,
                    "end_time":endtime_get,
                    "product_post":productname,
                    "market_post":marketname,
                })

            else:
                # 没有查询到相关记录
                products, categorys, markets, provinces, price_get_d1, price_get_d2, productname_d, marketname_d, time_set2_d = self.get_default()
                price_set_d1 = []
                for i in price_get_d1:
                    price_set_d1.append(float(i.price))
                price_set_d2 = []
                for j in price_get_d2:
                    price_set_d2.append(float(j.price))
                # 分析信息
                analysis1 = self.get_np_data(price_set_d1)
                analysis2 = self.get_np_data(price_set_d2)

                return render(request, "price_analysis2.html", {
                    "products": products,
                    "categories": categorys,
                    "markets": markets,
                    "provinces": provinces,
                    # "time_set": '',
                    # "price_set": '',

                    # 返回图表默认信息
                    "time_set": json.dumps(time_set2_d),
                    "price_set1": price_set_d1,
                    "price_set2": price_set_d2,
                    "analysis1": analysis1,
                    "analysis2": analysis2,

                    # 返回图表默认名称信息
                    "start_time": "2018年",
                    "end_time": "2019年",
                    "product_post": productname_d,
                    "market_post": marketname_d,

                    "miss": "不存在此信息，请重新选择！"
                })


       # 省份与市场选择框相关联
        elif(request.POST.get("verify", "false")=="yes"):
            data = {"status": "success"}
            province_ = request.POST.get("province", "")
            data['market'] = self.get_market_list(products_get, province_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')

        # 产品种类与产品名称选择框相关联
        else:
            data = {"status": "success"}
            category_ = request.POST.get("category", "")
            data['product'] = self.get_product_list(markets_get, category_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')

#同一产品在不同市场价格比较
class Price_analysis3(ProductAnalysisBaseView):
    def get_default(self):
        products, categorys, markets, provinces = self.get_all_base_data()
        price_get_d1 = product_price.objects.filter(marketproduct__product__productid=13233,marketproduct__market__marketid=20547,
                                                    date__date__range=(datetime.date.today() - datetime.timedelta(days=30),datetime.date.today()))
        price_get_d2 = product_price.objects.filter(marketproduct__product__productid=13233,marketproduct__market__marketid=45078,
                                                    date__date__range=(datetime.date.today() - datetime.timedelta(days=30),datetime.date.today()))
        productname_d = agr_product.objects.get(productid=13233)
        marketname_d1 = market.objects.get(marketid=20547)
        marketname_d2 = market.objects.get(marketid=45078)
        return products,categorys, markets, provinces,price_get_d1,price_get_d2,productname_d,marketname_d1,marketname_d2

    def get(self,request):
        products, categorys, markets, provinces, price_get_d1, price_get_d2, productname_d, marketname_d1, marketname_d2 = self.get_default()
        time_set2_d = self.get_time_set2(price_get_d1)
        price_set_d1 = []
        for i in price_get_d1:
            price_set_d1.append(float(i.price))
        price_set_d2 = []
        for k in price_get_d2:
            price_set_d2.append(float(k.price))
        analysis1 = self.get_np_data(price_set_d1)
        analysis2 = self.get_np_data(price_set_d2)
        #新闻推荐
        searchstr_d = productname_d.productname
        news_d = News_rec(searchstr_d,datetime.date.today()-datetime.timedelta(days=30), "2019-12-12")
        newslist_d = news_d.findnews()
        #返回页面
        return render(request, "price_analysis3.html", {
            "products":products,
            "categories":categorys,
            "markets":markets,
            "provinces":provinces,
            "newslist":newslist_d,

            # 返回图表默认信息
            "time_set": json.dumps(time_set2_d),
            "price_set1": price_set_d1,
            "price_set2":price_set_d2,
            "analysis1":analysis1,
            "analysis2": analysis2,

            # 返回图表默认名称信息
            "start_time": datetime.date.today()-datetime.timedelta(days=30),
            "end_time": datetime.date.today(),
            "product_post": productname_d,
            "market_post1": marketname_d1,
            "market_post2": marketname_d2,

        })

    def post(self,request):
        x=request.POST.get("btn_submit", "false")
        y = request.POST.get("verify1", "false")
        m = request.POST.get("verify2", "false")
        products_get = request.POST.get("product", "")
        markets_get1 = request.POST.get("market1", "")
        markets_get2 = request.POST.get("market2", "")
        if(request.POST.get("btn_submit", "false")=="true"):
            productname = agr_product.objects.get(productid=products_get)
            marketname1 = market.objects.get( marketid=markets_get1)
            marketname2 = market.objects.get( marketid=markets_get2)
            starttime_get = datetime.datetime.strptime(request.POST.get("startTime",""),"%Y-%m-%d").date()
            endtime_get = datetime.datetime.strptime(request.POST.get("endTime",""),"%Y-%m-%d").date()
            productmarket_get1 = product_in_market.objects.filter(product = products_get, market=markets_get1)
            productmarket_get2 = product_in_market.objects.filter(product = products_get, market=markets_get2)
            if(len(productmarket_get1)>0 and len(productmarket_get2)>0):
                products, categorys, markets, provinces = self.get_all_base_data()
                price_get1 = product_price.objects.filter(marketproduct__product__productid=int(products_get),marketproduct__market=int(markets_get1),date__date__range=(starttime_get, endtime_get))
                price_get2 = product_price.objects.filter(marketproduct__product__productid=int(products_get),marketproduct__market=int(markets_get2),date__date__range=(starttime_get, endtime_get))
                time_set2 = self.get_time_set2(price_get1)
                price_set1=[]
                for i in price_get1:
                    price_set1.append(float(i.price))
                price_set2=[]
                for j in price_get2:
                    price_set2.append(float(j.price))

                # 分析信息
                analysis1 = self.get_np_data(price_set1)
                analysis2 = self.get_np_data(price_set2)

                #相关新闻
                searchstr = productname.productname
                news = News_rec(searchstr, starttime_get, endtime_get)
                newslist = news.findnews()

                return render(request, "price_analysis3.html",{

                    # 返回表单信息
                    "products": products,
                    "categories": categorys,
                    "provinces":provinces,
                    "markets": markets,
                    "newslist":newslist,

                    # 返回图表信息
                    "time_set": json.dumps(time_set2),
                    "price_set1":price_set1,
                    "price_set2": price_set2,
                    "analysis1":analysis1,
                    "analysis2":analysis2,

                    # 返回图表名称信息
                    "start_time":starttime_get,
                    "end_time":endtime_get,
                    "product_post":productname,
                    "market_post1":marketname1,
                    "market_post2": marketname2,
                })

            else:
                products, categorys, markets, provinces, price_get_d1, price_get_d2, productname_d, marketname_d1, marketname_d2 = self.get_default()
                time_set2_d = self.get_time_set2(price_get_d1)
                price_set_d1 = []
                for i in price_get_d1:
                    price_set_d1.append(float(i.price))
                price_set_d2 = []
                for k in price_get_d2:
                    price_set_d2.append(float(k.price))

                # 分析信息
                analysis1 = self.get_np_data(price_set_d1)
                analysis2 = self.get_np_data(price_set_d2)

                # 没有查询到相关记录
                return render(request, "price_analysis3.html", {
                    "products": products,
                    "categories": categorys,
                    "markets": markets,
                    "provinces": provinces,

                    # 返回图表默认信息
                    "time_set": json.dumps(time_set2_d),
                    "price_set1": price_set_d1,
                    "price_set2": price_set_d2,
                    "analysis1": analysis1,
                    "analysis2": analysis2,

                    # 返回图表默认名称信息
                    "start_time": datetime.date.today()-datetime.timedelta(days=30),
                    "end_time": datetime.date.today(),
                    "product_post": productname_d,
                    "market_post1": marketname_d1,
                    "market_post2": marketname_d2,
                    "miss": "不存在此信息，请重新选择！"
                })

            # 省份1与市场1选择框相关联
        elif(request.POST.get("verify1", "false")=="yes"):
            data = {"status": "success"}
            province_ = request.POST.get("province1", "")
            data['market1'] = self.get_market_list(products_get, province_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')

            # 省份2与市场2选择框相关联
        elif (request.POST.get("verify2", "false") == "yes"):
            data = {"status": "success"}
            province_ = request.POST.get("province2", "")
            data['market2'] = self.get_market_list(products_get, province_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')

        # 产品种类与产品名称选择框相关联
        else:
            data = {"status": "success"}
            category_ = request.POST.get("category", "")
            data['product1'] = self.get_product_list(markets_get1, category_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')

#同一市场的不同产品价格比较
class Price_analysis4(ProductAnalysisBaseView):
    def get_default(self):
        products, categorys, markets, provinces = self.get_all_base_data()
        price_get_d1 = product_price.objects.filter(marketproduct__product__productid=13233,marketproduct__market__marketid=20547,
                                                    date__date__range=(datetime.date.today() - datetime.timedelta(days=30),datetime.date.today()))
        price_get_d2 = product_price.objects.filter(marketproduct__product__productid=13087,marketproduct__market__marketid=20547,
                                                    date__date__range=(datetime.date.today() - datetime.timedelta(days=30),datetime.date.today()))
        productname_d1 = agr_product.objects.get(productid=13233)
        productname_d2 = agr_product.objects.get(productid=13087)
        marketname_d = market.objects.get(marketid=20547)
        return products,categorys, markets, provinces,price_get_d1,price_get_d2,productname_d1,productname_d2,marketname_d

    def get(self,request):
        products, categorys, markets, provinces, price_get_d1, price_get_d2, productname_d1, productname_d2, marketname_d = self.get_default()
        time_set2_d = self.get_time_set2(price_get_d1)
        price_set_d1 = []
        for i in price_get_d1:
            price_set_d1.append(float(i.price))
        price_set_d2 = []
        for j in price_get_d2:
            price_set_d2.append(float(j.price))
        analysis1 = self.get_np_data(price_set_d1)
        analysis2 = self.get_np_data(price_set_d2)

         #返回页面
        return render(request, "price_analysis4.html", {
            "products":products,
            "categories":categorys,
            "markets":markets,
            "provinces":provinces,

            # 返回图表默认信息
            "time_set": json.dumps(time_set2_d),
            "price_set1": price_set_d1,
            "price_set2": price_set_d2,
            "analysis1":analysis1,
            "analysis2": analysis2,

            # 返回图表默认名称信息
            "start_time": datetime.date.today()-datetime.timedelta(days=30),
            "end_time": datetime.date.today(),
            "product_post1": productname_d1,
            "product_post2": productname_d2,
            "market_post": marketname_d,
        })

    def post(self,request):
        x=request.POST.get("btn_submit", "false")
        y = request.POST.get("verify1", "false")
        m=request.POST.get("verify2", "false")
        products_get1 = request.POST.get("product1", "")
        products_get2 = request.POST.get("product2","")
        markets_get = request.POST.get("market","")
        if(request.POST.get("btn_submit", "false")=="true"):
            productname1 = agr_product.objects.get(productid=products_get1)
            productname2 = agr_product.objects.get(productid=products_get2)
            marketname = market.objects.get( marketid=markets_get)
            starttime_get = datetime.datetime.strptime(request.POST.get("startTime",""),"%Y-%m-%d").date()
            endtime_get = datetime.datetime.strptime(request.POST.get("endTime",""),"%Y-%m-%d").date()
            productmarket_get = product_in_market.objects.filter(product = products_get1, market=markets_get)
            price_get1 = product_price.objects.filter(marketproduct__product__productid=int(products_get1),
                                                      marketproduct__market=int(markets_get),
                                                      date__date__range=(starttime_get, endtime_get))
            price_get2 = product_price.objects.filter(marketproduct__product__productid=int(products_get2),
                                                      marketproduct__market=int(markets_get),
                                                      date__date__range=(starttime_get, endtime_get))

            if(len(price_get1)>0 and len(price_get2)>0):
                products, categorys, markets, provinces = self.get_all_base_data()
                time_set2 = self.get_time_set2(price_get1)
                price_set1=[]
                for i in price_get1:
                    price_set1.append(float(i.price))
                price_set2=[]
                for k in price_get2:
                    price_set2.append(float(k.price))
                analysis1 = self.get_np_data(price_set1)
                analysis2 = self.get_np_data(price_set2)

                return render(request, "price_analysis4.html",{
                    # 返回表单信息
                    "products": products,
                    "categories": categorys,
                    "provinces":provinces,
                    "markets": markets,

                    # 返回图表信息
                    "time_set": json.dumps(time_set2),
                    # "time_set": time_set,
                    "price_set1":price_set1,
                    "price_set2": price_set2,
                    "analysis1":analysis1,
                    "analysis2":analysis2,

                    # 返回图表名称信息
                    "start_time":starttime_get,
                    "end_time":endtime_get,
                    "product_post1":productname1,
                    "product_post2": productname2,
                    "market_post":marketname,
                })

            else:
                #没有查询到相关记录
                products, categorys, markets, provinces, price_get_d1, price_get_d2, productname_d1, productname_d2, marketname_d = self.get_default()
                time_set2_d = self.get_time_set2(price_get_d1)
                price_set_d1 = []
                for i in price_get_d1:
                    price_set_d1.append(float(i.price))
                price_set_d2 = []
                for j in price_get_d2:
                    price_set_d2.append(float(j.price))
                analysis1 = self.get_np_data(price_set_d1)
                analysis2 = self.get_np_data(price_set_d2)

                return render(request, "price_analysis4.html",{

                "products": products,
                "categories": categorys,
                "markets": markets,
                "provinces": provinces,

                # 返回图表默认信息
                "time_set": json.dumps(time_set2_d),
                "price_set1": price_set_d1,
                "price_set2": price_set_d2,
                "analysis1": analysis1,
                "analysis2": analysis2,

                # 返回图表默认名称信息
                "start_time": datetime.date.today()-datetime.timedelta(days=30),
                "end_time": datetime.date.today(),
                "product_post1": productname_d1,
                "product_post2": productname_d2,
                "market_post": marketname_d,

                "miss": "不存在此信息，请重新选择！"
                })


       # 省份与市场选择框相关联
        elif(request.POST.get("verify", "false")=="yes"):
            data = {"status": "success"}
            province_ = request.POST.get("province", "")
            data['market'] = self.get_market_list(products_get1, province_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')

        # 产品种类1与产品名称1选择框相关联
        elif(request.POST.get("verify2", "false")=="yes"):
            data = {"status": "success"}
            category_ = request.POST.get("category1", "")
            data['product1'] = self.get_product_list(markets_get, category_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')

        # 产品种类2与产品名称2选择框相关联
        else:
            data = {"status": "success"}
            category_ = request.POST.get("category2", "")
            data['product2'] = self.get_product_list(markets_get, category_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')

#价格预测
class Price_predict(ProductBaseView):
    # 计算R^2
    # def R_square(self, his, pre):
    #     avg = sum(his) / len(his)
    #     l1 = 0
    #     l2 = 0
    #     for i in range(13):
    #         l1 += (pre[i] - his[i]) ** 2
    #         l2 += (his[i] - avg) ** 2
    #     result = 1-l1/l2
    #     return (result)

    def get_default(self):
        products, categorys, markets, provinces = self.get_all_base_data()
        price1_get_d = price_predict1.objects.filter(marketproduct__product=13233, marketproduct__market=20547)
        price2_get_d = price_predict2.objects.filter(marketproduct__product=13233, marketproduct__market=20547)
        productname_d = agr_product.objects.get(productid=13233)
        marketname_d = market.objects.get(marketid=20547)
        return products,categorys, markets, provinces,price1_get_d,price2_get_d,productname_d,marketname_d

    def get(self,request):
        # 获取默认图表信息
        products, categorys, markets, provinces, price1_get_d, price2_get_d, productname_d, marketname_d = self.get_default()
        # 获取模型Ⅰ信息
        price1_set_d = []
        for i in price1_get_d:
            price1_set_d.append(float(i.price))
        #获取模型Ⅱ信息
        price2_set_d = []
        for i in price2_get_d:
            price2_set_d.append(float(i.price))
        #获取时间信息
        time1_set_d = list(price1_get_d.values_list('date__date', flat=True))
        time1_set2_d = []
        for j in time1_set_d:
            time1_set2_d.append(j.strftime("%Y-%m-%d"))
        starttime2_get_d = time1_set2_d[0]
        endtime2_get_d = time1_set2_d[len(time1_set2_d) - 1]

        #获取历史价格
        starttime1_get_d=datetime.datetime.strptime(starttime2_get_d,"%Y-%m-%d")
        endtime1_get_d = datetime.datetime.strptime(starttime2_get_d,"%Y-%m-%d")+datetime.timedelta(12)
        # h=endtime1_get_d+datetime.timedelta(1)
        price_get1_d = product_price.objects.filter(marketproduct__product__productid=13233, marketproduct__market__marketid=20547,
                                              date__date__range=(starttime1_get_d,endtime1_get_d ))
        time_get1_d = date.objects.filter(date__range=(starttime1_get_d,endtime1_get_d ))
        time_set1_d = list(time_get1_d.values_list('date', flat=True))
        price_set1_d = []
        for i in price_get1_d:
            price_set1_d.append(float(i.price))
        time_set1_d1 =[]
        for j in time_set1_d:
            time_set1_d1.append(j.strftime("%Y-%m-%d"))

        #计算模型拟合度
        #r1 = self.R_square(price_set1_d,price1_set_d )
        # r1= r2_score(price_set1_d, price1_set_d)

        #时间拼接
        time_d = time1_set2_d
        # # 模型Ⅰ曲线拼接
        # price1_d = price_set1_d+price1_set_d
        # time_d =  time_set1_d1+time1_set2_d
        # # 模型Ⅱ曲线拼接
        # price2_d = price_set1_d + price2_set_d

        #获取表格信息
        table_pre_d = list(zip(time1_set2_d, price1_set_d, price2_set_d))
        #  #返回页面
        return render(request, "price_predict.html", {
            "products":products,
            "categories":categorys,
            "markets":markets,
            "provinces":provinces,
            "starttime":(endtime1_get_d+datetime.timedelta(1)).strftime("%Y-%m-%d"),
            "endtime": endtime2_get_d,

            # # 返回图表默认信息
            "time_set": json.dumps(time_d),
            "price_set1": price1_set_d,
            "price_set2": price2_set_d,
            "price_his":price_set1_d,
            "table_pre":table_pre_d,

            # # 返回图表默认名称信息
            "product_post": productname_d,
            "market_post": marketname_d,
        })

    def post(self,request):
        x=request.POST.get("btn_submit", "false")
        y = request.POST.get("verify", "false")
        products_get, markets_get,a,b = self.get_post_info(request)
        if(request.POST.get("btn_submit", "false")=="true"):
            productname = agr_product.objects.get(productid=products_get)
            marketname = market.objects.get( marketid=markets_get)
            productmarket_get = product_in_market.objects.filter(product=products_get, market=markets_get)
          #   predict1 = price_predict1.objects.filter(marketproduct = productmarket_get)
          #   predict2 =  price_predict2.objects.filter(marketproduct = productmarket_get)
            price1_get = price_predict1.objects.filter(marketproduct=productmarket_get)
            price2_get = price_predict2.objects.filter(marketproduct=productmarket_get)
            if(len(price1_get)>0 and len(price2_get)>0):
                products, categorys, markets, provinces = self.get_all_base_data()
                # 获取模型Ⅰ信息
                price1_get = price_predict1.objects.filter(marketproduct=productmarket_get)
                # price1_get = price_predict1.objects.filter(marketproduct__product=products.productid, marketproduct__market=markets.marketid)
                price1_set = []
                for i in price1_get:
                    price1_set.append(float(i.price))
                #获取时间信息
                time1_set= list(price1_get.values_list('date__date', flat=True))
                time1_set2 = []
                for j in time1_set:
                    time1_set2.append(j.strftime("%Y-%m-%d"))
                starttime2_get = time1_set2[0]
                endtime2_get = time1_set2[len(time1_set2) - 1]
                # 获取模型Ⅱ信息
                price2_get = price_predict2.objects.filter(marketproduct=productmarket_get)
                price2_set = []
                for i in price2_get:
                    price2_set.append(float(i.price))

                # 获取历史价格
                starttime1_get = datetime.datetime.strptime(starttime2_get, "%Y-%m-%d")
                endtime1_get = datetime.datetime.strptime(starttime2_get, "%Y-%m-%d") + datetime.timedelta(12)
                price_get1 = product_price.objects.filter(marketproduct__product__productid=products_get,
                                                            marketproduct__market__marketid=markets_get,
                                                            date__date__range=(starttime1_get, endtime1_get))
                time_get1 = date.objects.filter(date__range=(starttime1_get, endtime1_get))
                time_set1 = list(time_get1.values_list('date', flat=True))
                price_set1 = []
                for i in price_get1:
                    price_set1.append(float(i.price))
                time_set1_1 = []
                for j in time_set1:
                    time_set1_1.append(j.strftime("%Y-%m-%d"))

                # 时间拼接
                time= time1_set2

                # 获取表格信息
                table_pre = list(zip(time1_set2, price1_set, price2_set))
                return render(request, "price_predict.html",{

                    "products": products,
                    "categories": categorys,
                    "markets": markets,
                    "provinces": provinces,
                    "starttime": (endtime1_get+ datetime.timedelta(1)).strftime("%Y-%m-%d"),
                    "endtime": endtime2_get,

                    # # 返回图表默认信息
                    "time_set": json.dumps(time),
                    "price_set1": price1_set,
                    "price_set2": price2_set,
                    "price_his": price_set1,
                    "table_pre":table_pre,

                    # # 返回图表默认名称信息
                    "product_post": productname,
                    "market_post": marketname,
                })

            else:
                #没有查询到相关记录
                # 获取默认图表信息
                products, categorys, markets, provinces, price1_get_d, price2_get_d, productname_d, marketname_d = self.get_default()
                # 获取模型Ⅰ信息
                price1_set_d = []
                for i in price1_get_d:
                    price1_set_d.append(float(i.price))
                # 获取模型Ⅱ信息
                price2_set_d = []
                for i in price2_get_d:
                    price2_set_d.append(float(i.price))
                # 获取时间信息
                time1_set_d = list(price1_get_d.values_list('date__date', flat=True))
                time1_set2_d = []
                for j in time1_set_d:
                    time1_set2_d.append(j.strftime("%Y-%m-%d"))
                starttime2_get_d = time1_set2_d[0]
                endtime2_get_d = time1_set2_d[len(time1_set2_d) - 1]

                # 获取历史价格
                starttime1_get_d = datetime.datetime.strptime(starttime2_get_d, "%Y-%m-%d")
                endtime1_get_d = datetime.datetime.strptime(starttime2_get_d, "%Y-%m-%d") + datetime.timedelta(12)
                # h=endtime1_get_d+datetime.timedelta(1)
                price_get1_d = product_price.objects.filter(marketproduct__product__productid=13233,
                                                            marketproduct__market__marketid=20547,
                                                            date__date__range=(starttime1_get_d, endtime1_get_d))
                time_get1_d = date.objects.filter(date__range=(starttime1_get_d, endtime1_get_d))
                time_set1_d = list(time_get1_d.values_list('date', flat=True))
                price_set1_d = []
                for i in price_get1_d:
                    price_set1_d.append(float(i.price))
                time_set1_d1 = []
                for j in time_set1_d:
                    time_set1_d1.append(j.strftime("%Y-%m-%d"))

                # 时间拼接
                time_d = time1_set2_d

                # 获取表格信息
                table_pre_d = list(zip(time1_set2_d, price1_set_d, price2_set_d))

            return render(request, "price_predict.html",{
                "products": products,
                "categories": categorys,
                "markets": markets,
                "provinces": provinces,
                "starttime": (endtime1_get_d + datetime.timedelta(1)).strftime("%Y-%m-%d"),
                "endtime": endtime2_get_d,

                # # 返回图表默认信息
                "price_set1": price1_set_d,
                "price_set2": price2_set_d,
                "price_his": price_set1_d,
                "table_pre": table_pre_d,

                # # 返回图表默认名称信息
                "product_post": productname_d,
                "market_post": marketname_d,
                "miss": "不存在此信息，请重新选择！"
                })


       # 省份与市场选择框相关联
        elif(request.POST.get("verify", "false")=="yes"):
            data = {"status": "success"}
            province_ = request.POST.get("province", "")
            data['market'] = self.get_market_list(products_get, province_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')

        # 产品种类与产品名称选择框相关联
        else:
            data = {"status": "success"}
            category_ = request.POST.get("category", "")
            data['product'] = self.get_product_list(markets_get, category_, {})
            return HttpResponse(json.dumps(data), content_type='application/json')


class FavProductView(View):
    def get(self,requset):
        return render(requset,'login.html',{})
    def post(self,request):
        product1 = request.POST.get('product1','0')
        product2 = request.POST.get('product2','0')
        market1 = request.POST.get('market1', '0')
        market2 = request.POST.get('market2', '0')
        webtype = request.POST.get('webtype',0)
        mf1 = product_in_market.objects.filter(product=product1,market=market1)[0]
        try:
            mf2 = product_in_market.objects.filter(product=product2, market=market2)[0]
            exist_record = user_fav_products.objects.filter(user=request.user,webtype=webtype, mf1=mf1,mf2=mf2)
        except:
            mf2 = None
            exist_record = user_fav_products.objects.filter(user=request.user, webtype=webtype, mf1=mf1)
        #判断用户是否登录
        # if not request.user.is_authenticated():
        #     return HttpResponse(json.dumps({'status':'fail','msg':'请先登录'}),content_type='application/json')
        # else:
        #判断用户是否已收藏
        if exist_record:
            #若用户已收藏，则改为不收藏
            exist_record[0].delete()
            # return render(request,"news_details.html",{"newsdetails":newsdetails})
            return HttpResponse(json.dumps({"status": "success", "msg": "收藏"}), content_type='application/json')
        else:
            fav_product = user_fav_products()
            # this_news = news.objects.filter(newsid=int(news_id))
            fav_product.user = request.user
            fav_product.webtype = webtype
            fav_product.mf1 = mf1
            if mf2:
                fav_product.mf2 = mf2
            fav_product.save()
            return HttpResponse(json.dumps({"status":"success", "msg":"已收藏"}), content_type='application/json')
