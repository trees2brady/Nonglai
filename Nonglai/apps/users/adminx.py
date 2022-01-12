# _*_ encoding:utf-8 _*_

import xadmin

from .models import EmailVerifyRecord
from xadmin import views

class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True

class GolbalSettings(object):
    site_title = "农莱"
    site_footer = "农莱农业信息网"
    menu_style = "accordion"

class EmailVerifyRecordAdmin(object):
    list_display = ["code","email","send_type","send_time"]
    list_filter = ["code","email","send_type","send_time"]
    search_fields = ["code","email"]

class BannerAdmin(object):
    list_display = ["title","url","index","add_time"]
    list_filter = ["title","index","add_time"]
    search_fields = ["title"]

xadmin.site.register(EmailVerifyRecord,EmailVerifyRecordAdmin)
xadmin.site.register(views.BaseAdminView,BaseSetting)
xadmin.site.register(views.CommAdminView,GolbalSettings)