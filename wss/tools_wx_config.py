#!/usr/bin/python3.3
#_*_coding:utf-8_*_
#
# 文件作用：电子邮件工具类
#
# 创建时间：2015-07-06
#
#

from openpyxl import Workbook
from mongoengine import ReferenceField
from common.models import *
from mongoengine import ListField
from mongoengine.base.datastructures import BaseList
import datetime
from common.tools_legoo import DocumentTools, DocumentFolderType, ImageTools, ImageFolderType
try:
    from common.models import SiteSettings
except ImportError:
    from common.models import BaseSettings as SiteSettings
from common.models import DException
from django.conf import settings
import traceback
from uuid import uuid1
import os
import time
import random
import string
import hashlib
import json
import urllib.request
from wss.views_menu import MenuManager

class ConfigTools(object):
    def __init__(self, jsapi_ticket, url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret

    def get_jsapi_ticket(self, access_token):
        print("进入获取ticket")
        url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?type=jsapi&access_token='+access_token
        f = urllib.request.urlopen(url)
        accessT = f.read().decode("utf-8")
        jsonT = json.loads(accessT)
        print(jsonT)
        return jsonT["ticket"]

    def get_access_token(self):
        print("进入获取access_token")
        site_settings = SiteSettings.get_settings()
        app_id = site_settings.wechat_app_id
        secret = site_settings.wechat_app_secret
        accessUrl = url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+app_id+'&secret='+secret
        f = urllib.request.urlopen(accessUrl)
        accessT = f.read().decode("utf-8")
        jsonT = json.loads(accessT)
        print(jsonT)
        return jsonT["access_token"]

