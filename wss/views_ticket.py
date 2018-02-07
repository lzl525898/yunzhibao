import urllib.request
import json
import os

import time
import random
import string
import hashlib
#用户id
from xml.etree import ElementTree
from common.models import *
#open_id
from wss.tools_wechat import *
from common.decorators import ExceptionRequired, CheckTokenRequired

#test2
try:
    from common.models import SiteSettings
except ImportError:
    from common.models import BaseSettings as SiteSettings
from common.models import Certificate
from xml.dom.minidom import Document
from django.http import HttpResponse
from xml.etree import ElementTree
from django.conf import settings
from common.models import Client
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
# from wss.tools import *
from django.shortcuts import render_to_response
from django.template import RequestContext
#test
from common.tools import RequestTools

#test cache
from django.core.cache import cache







#保证有参数code
class CODE_View_Required:
    def _get_code(self, request, code, next_view):
        site_settings = SiteSettings.get_settings()
        host = request.get_host()
        redirect_uri = "http://"+host+"{0}?{1}".format(next_view, urllib.parse.urlencode(request.GET))
        return self.open_tools.get_code(app_id=site_settings.wechat_app_id, redirect_uri=redirect_uri, response_type='code', scope='snsapi_base', state='1')


    def __init__(self, func):
        print('__init__')
        self.func = func
        self.open_tools = GetOpenId()
        self.STATIC_HOST = settings.SERVER_URL

    def __call__(self, *args, **kwargs):
        print('__call__')
        request = args[0]
        next_view = request.META.get('PATH_INFO', '')
        print("下一个链接地址:"+next_view)
        code = request.GET.get('code', '')
        open_id = request.GET.get('open_id', '')
        print("CODE:"+code)
        print("OPEN_ID:"+open_id)
        if not code:
             code= self._get_code(request, code, next_view)
             if not isinstance(code, str):
                 return code
        return self.func(*args, **kwargs)

#通过auth2.0获取用户openid 
def get_Recommend_openid(request):
    site_settings = SiteSettings.get_settings()
    try:
        next_view = request.META.get('PATH_INFO', '')
    except:
        return "next_view wrong"
    try:
        code = request.GET.get('code', '')
        open_id = request.GET.get('open_id', '')
        if not open_id:
            open_id_url='https://api.weixin.qq.com/sns/oauth2/access_token?appid='+site_settings.wechat_app_id+'&secret='+site_settings.wechat_app_secret+'&code='+code+'&grant_type=authorization_code'
            a = urllib.request.urlopen(open_id_url)
            OPEN_ID = a.read().decode("utf-8")
            jsonO = json.loads(OPEN_ID)
            return jsonO["openid"]
        else:
            return open_id
    except Exception as e :
        return 'No2ne'

@ExceptionRequired
#获取当前的用户id:
def get_Recommend_id(request):
    openid=get_Recommend_openid(request)
    try:
        client = Client.objects(wx_id=openid).first()
        id=client.id
        return id
    except:
        try:
            client = Client.objects(user=request.user).first()
            id=client.id
            return id
        except:
            return 'Do not have client.id'
            
    
#生成js_ticket
class JsapI_ticket:
    
    def get_access_token(self):
        site_settings = SiteSettings.get_settings()
        url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+site_settings.wechat_app_id+'&secret='+site_settings.wechat_app_secret
        f = urllib.request.urlopen(url)
        accessT = f.read().decode("utf-8")
        jsonT = json.loads(accessT)
        cache.set('token', jsonT["access_token"],60*5)
        print(jsonT)
        print( jsonT["access_token"])
        return jsonT["access_token"]
    
    
    def get_jsapi_ticket(self,ACCESS_TOKEN):
        jsapi_ticket_url='https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token='+ACCESS_TOKEN+'&type=jsapi'
        f = urllib.request.urlopen(jsapi_ticket_url)
        Ticket = f.read().decode("utf-8")
        jsonT = json.loads(Ticket)
        cache.set('ticket',  jsonT["ticket"],60*10)
        print(jsonT)
        return jsonT["ticket"]
    
if __name__ == "__main__":
    js = JsapI_ticket()
    accessToken = js.get_access_token()
    js_ticket=js.get_jsapi_ticket(accessToken)

#保证js_ticket实时有效
class JSAPI_TICKET_Required:
    def __init__(self, func):
        print('__init__')
        self.func = func
        self.open_tools = JsapI_ticket()
        self.STATIC_HOST = settings.SERVER_URL

    def __call__(self, *args, **kwargs):
        print('__call__')
        request = args[0]
        token = cache.get('token',None)
        ticket = cache.get('ticket',None)
        if token is None:
            token=self.open_tools.get_access_token()
            ticket=self.open_tools.get_jsapi_ticket(token)
            cache.set('token',token,60*5)
            cache.set('ticket',ticket,60*10)
        if ticket is None:
            ticket=self.open_tools.get_jsapi_ticket(token)
            cache.set('token',token,60*5)
            cache.set('ticket',ticket,60*10)
        return self.func(*args, **kwargs)

#获得微信当前页面#前的url
def get_wx_url(request):
    try:
        url_1='http://'
        url_3=request.get_host()
        url_2=request.get_full_path()
        print(url_2)
        url_2=url_2.split('#')[0]
        url=url_1+url_3+url_2
    except:
        url='None'    
    return url
 


#进行签名
class Sign:
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
    string=string.encode('utf-8')
    self.ret['signature'] = hashlib.sha1(string).hexdigest()
    return self.ret

if __name__ == '__main__':
  # 注意 URL 一定要动态获取，不能 hardcode
  sign = Sign('jsapi_ticket', 'http://example.com')
  
  
  
#生成data
def CREAT_DATA_CONTENT(request):
    site_settings = SiteSettings.get_settings()
    atoken=cache.get('token',None)
    if request.method == 'GET':
        referee_id   =     request.GET.get('referee_id')
    else:
        referee_id   =     request.POST.get('referee_id')       
    referee_id = referee_id or None
    try:
         mine_id=get_Recommend_id(request)
    except:
        mine_id='None'
    js_ticket=cache.get('ticket',None)
    if js_ticket is None:
        data={}
        data['referee_id']="js_ticket is wrong"
    else:
        url=get_wx_url(request)
        sign = Sign(js_ticket,url)
        a=sign.sign()
        data = {}
        data['a']=a
        data['app_id'] =site_settings.wechat_app_id
        data['jsapi_ticket'] =js_ticket
        data['url'] = url
        data['referee_id']=referee_id
        data['mine_id']=mine_id
        host = request.get_host()
        data['main_url']="http://"+host+"/"
    return data
  
  
  
  
  
 
 