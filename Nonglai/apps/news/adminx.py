# _*_ encoding:utf-8 _*_
import xadmin

from .models import tag,news

class tagAdmin(object):
    list_display = ["tagid","tagname"]

class newsAdmin(object):
    list_display = ["newsid","newstag","title"]
    list_filter = ["newstag"]
    search_fields = ["title"]

xadmin.site.register(tag,tagAdmin)
xadmin.site.register(news,newsAdmin)