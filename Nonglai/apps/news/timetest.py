# _*_ encoding:utf-8 _*_

def write_conf():
    import configparser, datetime
    cf = configparser.ConfigParser()
    cf.add_section("log_news")
    cf.set("log_news","nextid","1")
    cf.set("log_news","scrpytime",datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S"))
    cf.set("log_news","lasttitle","no title")
    with open("Log.conf", "w") as f:
        cf.write(f)