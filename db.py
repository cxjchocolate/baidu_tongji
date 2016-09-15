#coding=gbk
'''
Created on 2015年11月5日

@author: 大雄
'''

from peewee import *
import peewee
import datetime

database = peewee.MySQLDatabase(host = '192.168.46.106', user = 'root', passwd = 'root.com', database = 'bi', charset = 'utf8')  

class BaiduDailyVisit(Model):
    visit_date = DateField()
    pv_count = DecimalField(max_digits=10)
    uv_count = DecimalField(max_digits=10)
    ip_count = DecimalField(max_digits=10)
    bounce_rate = DecimalField(max_digits=10,decimal_places=4)
    visit_time_avg = CharField(max_length=20)
    create_time = DateTimeField(default=datetime.datetime.now)
    src_sys = CharField(max_length=20,null=True)
    class Meta:
        db_table = 'bi_dm_baidu_visit_by_day'
        database = database
        
class ScheduleLog(Model):
    job_name = CharField(max_length=50,null=True)
    create_time = DateTimeField(default=datetime.datetime.now)
    status = CharField(max_length=20,null=True)
    desc = TextField(null=True)
    class Meta:
        db_table = 'bi_schedule_log'
        database = database

if __name__ == '__main__':
    database.connect()
    database.create_tables([ScheduleLog])