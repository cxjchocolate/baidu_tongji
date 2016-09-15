#coding=gbk
'''
Created on 2015年12月23日

@author: 大雄
'''
import logging
import tools
from db import ScheduleLog, BaiduDailyVisit
from datetime import datetime

host = 'pop.ym.163.com'  
username = 'tongji@zaofans.com'  
password = 'tongji4321#'


def importBaiduDailyVisit(row_range,col_range):
    job = ScheduleLog()
    job.job_name = "importBaiduDailyVisit"
    try:
        messages = tools.fetchMail(host, username, password)
        if messages:
            desc = ''
            desc = desc + "total messages: " + str(len(messages)) + "\n"
            for msg in messages:
                try:
                    #读取邮件附件
                    subject = tools.parserSubject(msg)
                    attachs = tools.parserAttachMent(msg)
                    if len(attachs) != 1:
                        raise Exception("more than 1 attachments in one mail")
                    for k,v in attachs.items():
                        (attachname,zipcontent) = (k,v)
                    logging.debug(attachname)
                    if attachname.find(".zip") <= -1:
                        raise Exception("attachment is not zip file")
                    #解压邮件附件
                    unzip_files = tools.parserZipfile(zipcontent)
                    if len(unzip_files) != 1:
                        raise Exception("more than 1 file in one zipfile")
                    for k,v in unzip_files.items():
                        (unzipfilename, content) = (k,v)
                    logging.debug(unzipfilename)
                    #解析附件压缩包中的csv数据
                    (start,end) = __parserBaiduVisitCVSname(unzipfilename)[1:3]
                    if start != end:
                        raise Exception("wrong range of date for cvs data")
                    else:
                        logging.debug("start = end")
                        
                    csv_content = bytes.decode(content,"GB2312")
                    data = tools.parserCSV(csv_content,row_range,col_range)
                    #写入数据库
                    if data:
                        v = BaiduDailyVisit()
                        v.pv_count       = tools.convertStr2Int(data[0][0],0)
                        v.uv_count       = tools.convertStr2Int(data[0][1],0)
                        v.ip_count       = tools.convertStr2Int(data[0][2],0)
                        v.bounce_rate    = tools.convertStr2Float(data[0][3],0.00)
                        v.visit_time_avg = data[0][4].strip() #str
                        v.src_sys        = tools.mappingKeywords(subject) #str
                        v.visit_date     = start
                        v.save()
                    else:
                        raise Exception("no data found")
                    desc = desc + "subject:" + subject + "\n" + "success" + "\n"
                except Exception as e:
                    logging.debug(e)
                    desc = desc + "subject:" + subject + "\n" + str(e) + "\n"
                    #继续读取其他mail
            job.status = "success"
            job.desc = desc
        else:
            logging.debug("no message")
            job.status = "error"
            job.desc = "No new mail"
        #保存schedule log
    except Exception as e:
        logging.debug(e)
        job.status = "error"
        job.desc = str(e)
    finally:
        job.save(force_insert=True)
        
def __parserBaiduVisitCVSname(name):
    datefmt = '%Y%m%d'
    if name:
        pos1 = name.find("_")
        pos2 = name.find("-")
        pos3 = name.find(".")
        return (name[0:pos1], 
                datetime.strptime(name[pos1+1:pos2],datefmt),
                datetime.strptime(name[pos2+1:pos3],datefmt))
    else:
        return None

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')
    importBaiduDailyVisit([1], [2,3,4,5,6])
