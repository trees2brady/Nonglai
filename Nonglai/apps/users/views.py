from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.backends import ModelBackend
from .models import UserProfile,EmailVerifyRecord
from django.db.models import Q
from django.views.generic.base import View
from .forms import LoginForm,RegisterForm,ForgetpwdForm,ResetpwdForm
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect,HttpResponse
from utils.email_send import send_register_email,send_resetpwd_email

from operation.sql_views import *
from news.models import news,postings
import functions,json,datetime

class ForgetpwdView(View):
    def get(self,request):
        forgetpwd_form = ForgetpwdForm()
        return render(request, "forgetpwd.html", {"forgetpwd_form": forgetpwd_form})

    def post(self,request):
        forgetpwd_form = ForgetpwdForm(request.POST)
        if forgetpwd_form.is_valid():
            email = request.POST.get("email", "")
            # flag = UserProfile.objects.filter(email=email)
            # if not flag:
            #     return render(request, "register.html", {
            #         "msg": "该邮箱未被注册！",
            #         "forgetpwd_form": forgetpwd_form,
            #     })
            send_resetpwd_email(email, "forget")
            return render(request, "send_success.html", {})
        else:
            return render(request, "forgetpwd.html", {"forgetpwd_form":forgetpwd_form})

class ResetPwdView(View):
    def get(self,request,reset_code):
        records = EmailVerifyRecord.objects.filter(code=reset_code)
        if records:
            for record in records:
                email = record.email
                return render(request, "resetpwd.html", {"email": email })
        else:
            return render(request, "failactive.html", {})
        return render(request, "login.html", {})

class ModifyView(View):
    def post(self,request):
        reset_form = ResetpwdForm(request.POST)
        if reset_form.is_valid():
            newpwd1 = request.POST.get("newpwd1","")
            newpwd2 = request.POST.get("newpwd2", "")
            if newpwd1!=newpwd2:
                return render(request,"resetpwd.html",{"msg":"密码不一致！"})
            email = request.POST.get("email","")
            user = UserProfile.objects.get(email=email)
            user.password = make_password(newpwd1)
            user.save()
            return render(request,"login.html",{})
        else:
            return render(request, "resetpwd.html", {
                "msg": reset_form.errors,
            })

class ActiveView(View):
    def get(self,request,active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                this_user = UserProfile.objects.get(email=email)
                this_user.is_active = True
                this_user.save()
        else:
            return render(request, "failactive.html", {})
        return render(request, "login.html", {})

class LogoutView(View):
    def get(self,request):
        logout(request)
        from django.core.urlresolvers import reverse
        return HttpResponseRedirect(reverse("index"))

class LoginView(View):
    def get(self,request):
        return render(request, "login.html", {})

    def post(self,request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            password = request.POST.get("password", "")
            user = authenticate(username=user_name, password=password)
            if user is not None:
                # if user.is_active:
                    login(request, user)
                    return HttpResponse(json.dumps({"status": 'success', "username": user_name}), content_type='application/json')
                # else:
                #     return HttpResponse(json.dumps({"status":'fail', "msg":u"用户未激活！"}),
                #                         content_type='application/json')
            else:
                return HttpResponse(json.dumps({"status": 'fail', "msg": u"用户名或密码错误！"}),
                                    content_type='application/json')
        else:
            return HttpResponse(json.dumps({"status": 'fail', "msg":"输入不合法！"}),
                                content_type='application/json')

class RegisterView(View):
    def get(self,request):
        register_form = RegisterForm()
        return render(request, "signup.html", {"register_form":register_form})
    def post(self,request):
        if request.POST.get("password1", "") != request.POST.get("password2", ""):
            return render(request, "signup.html", {
                "msg": "两次密码不一致！",
            })
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            # email = request.POST.get("email", "")
            # if UserProfile.objects.filter(email=email):
            #     return render(request, "signup.html", {
            #         "msg": "该邮箱已被注册！",
            #         "register_form": register_form,
            #     })
            user_name = request.POST.get("username", "")
            if UserProfile.objects.filter(username=user_name):
                return render(request, "signup.html", {
                    "register_form": register_form,
                    "msg": "该用户名已被注册！",
                })
            password = request.POST.get("password1", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            # user_profile.email = email
            user_profile.email = ""
            user_profile.is_active = False
            user_profile.password = make_password(password)
            user_profile.save()
            # if send_register_email(email,"register"):
            #     return render(request, "signup.html", {
            #         "register_success":True,
            #         "msg":"注册成功，请注意查收激活邮件！"
            #     })
            # else:
            #     return render(request, "signup.html", {
            #         "register_form": register_form,
            #         "msg": "邮件发送失败！",
            #     })
            return render(request, "signup.html", {
                    "register_success":True,
                    "msg":"注册成功！"
                })
        else:
            try:
                msg = register_form.errors['checkword'][0]
            except:
                msg = '注册失败!'
            return render(request, "signup.html", {
                "register_form": register_form,
                "msg":msg,
            })

class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except:
            return None
#
# def user_login(request):
#     if request.method == "POST":
#         user_name = request.POST.get("username","")
#         password = request.POST.get("pwd", "")
#         nic = request.POST.get("nic", "")
#         email = request.POST.get("email", "")
#         address = request.POST.get("address", "")
#         user=authenticate(username=user_name, password=password)
#         if user is not None:
#             login(request,user)
#             return render(request,"news_list.html",{
#                 "username":user_name,
#             })
#         else:
#             return render(request, "login.html", {
#                 "msg":u"用户名或密码错误！",
#             })
#
#     elif request.method == "GET":
#         return render(request,"login.html",{})

class Change_infoView(View):
    def get(self,request):
        if request.user.birthday == None:
            user_brithday = ""
        else:
            user_brithday = request.user.birthday
        return  render(request,"personal_center_info.html",{"user_brithday":user_brithday})
    def post(self,request):
        user_name = request.POST.get("user_name","")
        try:
            user_brithday = datetime.datetime.strptime(request.POST.get("user_brithday",""),"%Y-%m-%d")
            user_brithday1 = request.POST.get("user_brithday","")
        except:
            user_brithday = None
            user_brithday1 = ""
        user_mobile = request.POST.get("user_mobile","")
        user_address = request.POST.get("user_address","")
        user_email = request.POST.get("user_email","")
        user = UserProfile.objects.get(email=user_email)
        if user is not None:
            user.username = user_name
            user.mobile = user_mobile
            user.address = user_address
            user.birthday = user_brithday
            user.save()
            return render(request, "personal_center_info.html", {"user_brithday":user_brithday1})
        else:
            return render(request, "personal_center_info.html", {'msg':u'账号异常！请联系管理员！'})

class MyCollectionView(View):
    def get(self,request):
        Myfavnewslist = user_fav_news.objects.filter(user=request.user)
        return render(request, "personal_center_collect.html", {
                "fav_news_count":len(Myfavnewslist),
                "fav_news_list":Myfavnewslist
            })

    def post(self,request):
        deleted_id = request.POST.get("deleted_favnewsid",'0')
        delete_item = user_fav_news.objects.filter(id=deleted_id)
        delete_item.delete()
        Myfavnewslist = user_fav_news.objects.filter(user=request.user)
        return render(request, "personal_center_collect.html", {
            "fav_news_count": len(Myfavnewslist),
            "fav_news_list": Myfavnewslist
        })

class MyFavProducts(View):
    def get(self,request):
        Myfavnewslist = user_fav_products.objects.filter(user=request.user)
        return render(request, "personal_center_collect_product.html", {
                "fav_products_count":len(Myfavnewslist),
                "fav_products_list":Myfavnewslist
            })

    def post(self,request):
        deleted_id = request.POST.get("deleted_favid",'0')
        delete_item = user_fav_products.objects.filter(id=deleted_id)
        delete_item.delete()
        Myfavnewslist = user_fav_products.objects.filter(user=request.user)
        return render(request, "personal_center_collect_product.html", {
            "fav_products_count": len(Myfavnewslist),
            "fav_products_list": Myfavnewslist
        })

class MyCommentView(View):
    def get(self,request):
        Mycommentlist = comments.objects.filter(user=request.user)
        return render(request, "personal_center_comment.html", {
                "comments_count":len(Mycommentlist),
                "comments_list":Mycommentlist
            })

    def post(self,request):
        deleted_id = request.POST.get("deleted_commentid",'0')
        delete_item = comments.objects.filter(id=deleted_id)
        delete_item.delete()
        Mycommentlist = comments.objects.filter(user=request.user)
        return render(request, "personal_center_comment.html", {
            "comments_count": len(Mycommentlist),
            "comments_list": Mycommentlist
        })