#coding=gbk
'''
Created on 2015年12月21日

@author: 大雄
'''
import csv
import poplib 
import email.header
import email.utils
import base64
import os
import logging
from zipfile import ZipFile
from io import BytesIO,StringIO

def parserCSV(string,row_range,col_range):
    try:
        strio = StringIO(string)
        data = []
        reader = csv.reader(strio,delimiter=',',quotechar='"')
        index = 0
        for row in reader:
            if index in row_range:
                item = []
                for col in col_range:
                    item.append(row[col])
                data.append(item)
            index = index + 1
        return data
    except Exception as e:
        logging.debug(e)
        return None
    finally:
        strio.close()

def showMessage( msg ):
    if msg.is_multipart():
        for part in msg.get_payload():
            showMessage( part )
    else:
        types = msg.get_content_type()
        if types=='text/plain':
            try:
                body =msg.get_payload(decode=True)
                print(bytes.decode(body))
            except:
                print( '[*001*]BLANK')
        elif types=='text/base64':
            try:
                body = base64.decodestring(msg.get_payload())
                print(bytes.decode(body))
            except:
                print( '[*001*]BLANK')
               
def parserAttachMent( msg ):
    # 取得附件部分
    attachments = {}
    code = email.header.decode_header(msg['subject'])[0][1]
    for part in msg.walk():
        filename = part.get_filename()
        if filename==None:
            continue
        filename = email.header.decode_header(filename)[0][0]
        filename = bytes.decode(os.path.split(filename)[1], code)
            # 防止文件名出现全路径错误
        if filename:
            ###解析邮件的附件内容
            attach_b64 = part.get_payload()
            attach_byte = base64.decodestring(str.encode(attach_b64))
            attachments[filename] = attach_byte
        else:
            continue
    return attachments    

def parserZipfile( zipbytes ):
    with ZipFile(BytesIO(zipbytes), 'r') as myzip:
        files = {}
        for filename in myzip.namelist():
            files[filename] = myzip.read(filename)
        return files

def fetchMail(host,username,password,mail_from='autopost@baidu.com',max_top_mail_prefetch = 10):   
    try:
        pop_conn = poplib.POP3(host,port=110)
        pop_conn.user(username)  
        pop_conn.pass_(password)
        messages = []
        totalNum = pop_conn.stat()[0]
        if max_top_mail_prefetch < totalNum:
            start = totalNum
            end = totalNum - max_top_mail_prefetch
        else:
            start = totalNum
            end = 1
        for i in range(start, end,-1):
            msg = []
            for line in pop_conn.retr(i)[1]:
                msg.append(bytes.decode(line))
            message = email.message_from_string('\n'.join(msg))
            #print(message)
            #m_subject = email.header.decode_header(message['subject'])[0][0]
            m_subcode = email.header.decode_header(message['subject'])[0][1]
            header_from = email.header.decode_header(message['From'])
            m_from     = header_from[len(header_from)-1][0]
            #m_to      = email.header.decode_header(message['To'])[0][0]
            #m_date    = email.header.decode_header(message['date'])[0][0]
            #print(email.header.decode_header(message['From']))
            if str(type(m_from)) == "<class 'str'>":
                #准确格式
                m_from = email.utils.parseaddr(m_from)[1]
            elif str(type(m_from)) == "<class 'bytes'>":
                #格式可能有点问题：" <jun.zhang@mcake.com>
                m_from = bytes.decode(m_from,m_subcode).strip()
            else:
                logging.debug("from: wrong type")
            
            if m_from:
                if (m_from.find(mail_from) > -1):
                    messages.append(message)
        return messages
    except Exception as e:
        logging.debug(e)
        raise Exception(e)
    finally: 
        pop_conn.quit()

def parserSubject( msg ):
    #m_subject = email.header.decode_header(message['subject'])[0][0]
    m_subcode = email.header.decode_header(msg['subject'])[0][1]
    m_subject = email.header.decode_header(msg['subject'])[0][0]
    #m_to      = email.header.decode_header(message['To'])[0][0]
    #m_date    = email.header.decode_header(message['date'])[0][0]
    #print(email.header.decode_header(message['From']))
    if str(type(m_subject)) == "<class 'str'>":
        pass
    elif str(type(m_subject)) == "<class 'bytes'>":
        m_subject = bytes.decode(m_subject,m_subcode)
    else:
        logging.debug("from: wrong type")
    
    return m_subject

def mappingKeywords(subject):
    keywords = {
                "Grand-Cookies":["zumuquqi"], 
                "Joyseed":["joyseed"],
                "HI-MCAKE":["mcake"],
                "WithWheat":["withwheat"],
                "Flower":["flower"]
                }

    if subject:
        for (tag,keys) in keywords.items():
            for key in keys:
                if subject.find(key) > -1:
                    return tag
    return None 

def convertStr2Int(value,default=0):
    try:
        return int(value.replace(',',''))
    except ValueError:
        return default
    
def convertStr2Float(value,defalut=0.00):
    try:
        if value.find('%',-1) > 0:
            return float(value.replace(',','')[0:-1]) / 100
        else:
            return float(value.replace(',',''))
    except ValueError:
        return defalut
