# _*_ encoding:utf-8 _*_

from .models import *

class MyFavNews(models.Model):
    id = models.IntegerField(primary_key=True)
    addtime = models.DateTimeField(verbose_name=u"收藏时间")
    userid = models.IntegerField(verbose_name=u"用户ID")
    newsid = models.IntegerField(verbose_name=u"新闻ID")
    title = models.CharField(max_length=50,verbose_name=u"新闻标题")

    # def __repr__(self):
    #     return 'addtime: ' + str(self.addtime)

    class Meta:
        managed = False
        db_table = 'View_MyfavNews'