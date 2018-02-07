#!/usr/bin/python3.3
#_*_coding:utf-8_*_
#
# 文件作用：电子邮件工具类
#
# 创建时间：2015-07-06
#
#
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate
from email.mime.text import MIMEText
import subprocess
import os


class EmailTools(object):
    server = None
    frm = None
    username = None
    password = None

    def __init__(self, server, frm, username, password):
        self.server = server
        self.frm = frm
        self.username = username
        self.password = password

    def send(self, to, subject, text='', html='', files=''):
        #构造MIMEMultipart对象作为根容器
        msg = MIMEMultipart()
        print('创建新邮件:'+self.frm+' 到 '+to)
        # 邮件的基本属性
        msg[u'Subject'] = subject
        #格式为*@*.*或者*<*@*.*>具体的电子邮件地址必须与实际地址相符
        msg[u'From'] = self.frm
        #格式为*@*.*或者*<*@*.*>具体的电子邮件地址必须与实际地址相符
        msg[u'To'] = to
        #Date表示发送邮件的时间，不过验证不严，可以随便填，只要是str就好
        msg[u'Date'] = formatdate()
        # 添加邮件内容
        #构造MIEMText对象作为邮件显示内容并附加到根容器
        if text != '':
            msg.attach(MIMEText(text, 'text'))
        if html != '':
            msg.attach(MIMEText(html, 'html'))
        #构造MIMEBase对象作为文件附件内容
        attachment = MIMEBase(u'application', u'octet-stream')
        #读入文件并格式化
        if files != '':
            #print(files)
            attachment.set_payload(open(files, 'rb').read())
            encoders.encode_base64(attachment)
            #设置附件头
            attachment.add_header(u'Content-Disposition', u'attachment; filename="%s"'%os.path.basename(files))
            #添加到根容器
            msg.attach(attachment)
            # 初始化
        s = smtplib.SMTP()
        # print(u'连接SMTP服务器:'+server+'...')
        s.connect(self.server)
        # print(u'登陆:'+user+'...')
        s.login(self.username, self.password)
        # print(u'正在发送邮件{subject}...'.format(**locals()))
        s.sendmail(self.frm, to, msg.as_string())
        # 退出
        s.quit()
        # print(u'邮件发送成功.')

if __name__ == "__main__":
    email_tools = EmailTools(server='smtp.163.com',
                             frm='"系统邮件"<jorintest@163.com>',
                             username='jorintest',
                             password='82380592')
    #mto = u'JorinTest2@163.com'
    mto = '"邮件发送成功@163.com"<jorintest2@163.com>'
    testfile = u'test.apk'
    title = u'{test}em邮件发送成功ail_33{tessst}'
    text = u'this is a email for test'
    #设置要使用的目录
    here = subprocess.check_output(['pwd'], shell=True, universal_newlines=True).strip()
    email_tools.send(to=mto, text=text, subject=title)

