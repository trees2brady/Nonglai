# -*- coding: utf-8 -*-

import configparser
import math
import operator
import datetime

import jieba

from MySQL import *


class SearchEngine:
    stop_words = set()
    
    config_path = ''
    config_encoding = ''
    
    K1 = 0
    B = 0
    N = 0
    AVG_L = 0
    
    #conn = None
    
    def __init__(self, config_path, config_encoding):
        self.config_path = config_path
        self.config_encoding = config_encoding
        config = configparser.ConfigParser()
        config.read(config_path, config_encoding)
        f = open("./log/stop_words.txt", encoding = 'utf-8')
        words = f.read()
        self.stop_words = set(words.split('\n'))
        
        self.K1 = float(1.5)
        self.B = float(0.75)
        self.N = int(380)
        self.AVG_L = float(865.4131578947369)
        self.nonglaidb = MySQL()


    #def __del__(self):
    #    self.conn.close()
    
    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    """分割、统计关键字及个数{key="词项", value="个数"}"""        
    def clean_list(self, seg_list):
        cleaned_dict = {}
        n = 0
        for i in seg_list:
            i = i.strip().lower()
            if i != '' and not self.is_number(i) and i not in self.stop_words:
                n = n + 1
                if i in cleaned_dict:
                    cleaned_dict[i] = cleaned_dict[i] + 1
                else:
                    cleaned_dict[i] = 1
        return n, cleaned_dict

    """找出posting中词项所匹配"""
    def fetch_from_db(self, term):
        conn = self.nonglaidb.get_connect()
        c = conn.cursor()
        c.execute("SELECT * FROM news_postings WHERE term='"+term+"'")
        conn.commit()
        conn.close()
        return(c.fetchone())

    """综合排序"""
    def result_by_BM25(self, sentence):
        seg_list = jieba.lcut(sentence, cut_all=False)
        n, cleaned_dict = self.clean_list(seg_list)#分割、统计搜索词中关键字及个数
        BM25_scores = {}
        for term in cleaned_dict.keys():
            r = self.fetch_from_db(term)
            if r is None:
                continue
            df = r[1] #df值
            w = math.log2((self.N - df + 0.5) / (df + 0.5))
            docs = r[2].split('\n')
            for doc in docs:
                docid, date_time, tf, ld = doc.split('\t')
                docid = int(docid)
                tf = int(tf)
                ld = int(ld)
                s = (self.K1 * tf * w) / (tf + self.K1 * (1 - self.B + self.B * ld / self.AVG_L))
                if docid in BM25_scores:
                    BM25_scores[docid] = BM25_scores[docid] + s
                else:
                    BM25_scores[docid] = s
                #对文档相关度打分 BM25_scores{key=docid value=分数}
        BM25_scores = sorted(BM25_scores.items(), key = operator.itemgetter(1))
        BM25_scores.reverse()    #逆序排序
        if len(BM25_scores) == 0:
            return 0, []
        else:
            return 1, BM25_scores

    """按时间排序"""
    def result_by_time(self, sentence):
        seg_list = jieba.lcut(sentence, cut_all=False)
        n, cleaned_dict = self.clean_list(seg_list)
        time_scores = {}
        for term in cleaned_dict.keys():
            r = self.fetch_from_db(term)
            if r is None:
                continue
            docs = r[2].split('\n')
            for doc in docs:
                docid, date_time, tf, ld = doc.split('\t')
                if docid in time_scores:
                    continue
                #TODO:修改日期格式
                news_datetime = datetime.datetime.strptime(date_time[:10], "%Y-%m-%d")
                now_datetime = datetime.datetime.now()
                td = now_datetime - news_datetime
                docid = int(docid)
                td = (datetime.timedelta.total_seconds(td) / 3600) # hour
                time_scores[docid] = td
        time_scores = sorted(time_scores.items(), key = operator.itemgetter(1))
        if len(time_scores) == 0:
            return 0, []
        else:
            return 1, time_scores

    """按热度排序"""
    def result_by_hot(self, sentence):
        seg_list = jieba.lcut(sentence, cut_all=False)
        n, cleaned_dict = self.clean_list(seg_list)
        hot_scores = {}
        for term in cleaned_dict.keys():
            r = self.fetch_from_db(term)
            if r is None:
                continue
            df = r[1]
            w = math.log2((self.N - df + 0.5) / (df + 0.5))
            docs = r[2].split('\n')
            for doc in docs:
                docid, date_time, tf, ld = doc.split('\t')
                docid = int(docid)
                tf = int(tf)
                ld = int(ld)
                news_datetime = datetime.datetime.strptime(date_time[:10], "%Y-%m-%d")
                now_datetime = datetime.datetime.now()
                td = now_datetime - news_datetime
                BM25_score = (self.K1 * tf * w) / (tf + self.K1 * (1 - self.B + self.B * ld / self.AVG_L))
                td = (datetime.timedelta.total_seconds(td) / 3600) # hour
                hot_score = math.log(BM25_score) + 1 / td
                if docid in hot_scores:
                    hot_scores[docid] = hot_scores[docid] + hot_score
                else:
                    hot_scores[docid] = hot_score
        hot_scores = sorted(hot_scores.items(), key = operator.itemgetter(1))
        hot_scores.reverse()
        if len(hot_scores) == 0:
            return 0, []
        else:
            return 1, hot_scores
    
    def search(self, sentence, sort_type = 0):
        if sort_type == 0:
            return self.result_by_BM25(sentence)
        elif sort_type == 1:
            return self.result_by_time(sentence)
        elif sort_type == 2:
            return self.result_by_hot(sentence)

if __name__ == "__main__":
    se = SearchEngine('config.ini', 'utf-8')
    flag, rs = se.search('我国农业发展', 2)#################修改
    print(rs[:15])######??????????
