__author__ = 'mlzx'
import hashlib
try:
    from common.models import SiteSettings
except ImportError:
    from common.models import BaseSettings as SiteSettings
from common.models import Certificate
from xml.dom.minidom import Document
from wss.models_wechat import Event
from django.http import HttpResponse
from xml.etree import ElementTree
from django.conf import settings
import time
from enum import Enum
from common import tools_string
from common.models import Client
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
# from wss.tools import *
import urllib.request
from django.shortcuts import render_to_response
from django.template import RequestContext
import json
#test
from common.tools import RequestTools

class EventType(Enum):
    text = 0
    voice = 1


REPLAY_TEXT = """<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    <FuncFlag>0</FuncFlag>
    </xml>"""
MESSAGE_HYPER_LINK = """<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[link]]></MsgType>
    <Title><![CDATA[%s]]></Title>
    <Description><![CDATA[%s]]></Description>
    <Url><![CDATA[%s]]></Url>
    </xml>"""
MESSAGE_TEXT_PICTURE = """
    <xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>1</ArticleCount>
    <Articles>
    <item>
    <Title><![CDATA[%s]]></Title>
    <Description><![CDATA[%s]]></Description>
    <PicUrl><![CDATA[%s]]></PicUrl>
    <Url><![CDATA[%s]]></Url>
    </item>
    </Articles>
    </xml>
"""


class AccessToken(object):
    def __init__(self, token, create_time):
        self.token = token
        self.create_time = create_time


class WeChatTools(object):
    access_token = AccessToken(token="", create_time=0)
    site_settings = SiteSettings.get_settings()
    KEY_LENGTH = 5

    # 检测消息真实性
    # 将token、timestamp、nonce三个参数进行字典序列排序
    # 将三个参数字符串拼接成一个字符串进行sha1加密
    # 开发者获得加密后的字符串可与signature对比， 标志该请求来源于微信
    def check_signature(self, signature, timestamp, nonce):
        if self.site_settings is None:
            print("token is none")
            return False
        if timestamp is None:
            print("timestamp is none")
            return False
        if nonce is None:
            print("nonce is none")
            return False
        array = [self.site_settings.we_chat_token, timestamp, nonce]
        array.sort()
        line = array[0]+array[1]+array[2]
        string = hashlib.sha1(line.encode(encoding='gb2312')).hexdigest()
        print(string)
        print(signature)
        return signature == string

    # 根据创建时间和来源进行查重，若重复则代表此请求已接受到过，不予处理
    #  #
    @staticmethod
    def is_repeat(create_time, user_open_id):
        #todo 根据创建时间和来源在数据库中查重
        num_event = Event.objects(create_time=create_time, from_user_name=user_open_id).count()
        if num_event > 0:
            return True
        else:
            return False

    # 检查Event是否重复，若不重复则保存到数据库
    @staticmethod
    def check_event(xml, content):
        print("检测消息是否重复")
        try:
            server_id = xml.find("ToUserName").text
            user_open_id = xml.find("FromUserName").text
            create_time = xml.find("CreateTime").text
            message_type = xml.find("MsgType").text
            if WeChatTools.is_repeat(create_time=create_time, user_open_id=user_open_id):
                return False
            else:
                Event(from_user_name=user_open_id, to_user_name=server_id, create_time=int(create_time), msg_type=message_type,
                      content=content).save()
                return True
        except Exception as e:
            print("check event error:"+e.args)
            return False

    # 回复文字
    @staticmethod
    def text_response(to_user_name, from_user_name, text):
        print("get text response to %s:text = %s" % (to_user_name, text))
        post_time = str(int(time.time()))
        return HttpResponse(REPLAY_TEXT % (to_user_name, from_user_name, post_time, text))

    # 回复超链接
    @staticmethod
    def hyper_link_response(from_user_name, to_user_name, title, description, url):
        post_time = str(int(time.time()))
        content = MESSAGE_HYPER_LINK % (to_user_name, from_user_name, post_time, title, description, url)
        return HttpResponse(content)

    # 单图文消息
    @staticmethod
    def single_text_picture_response(from_user_name, to_user_name, title, description, pic_url, url):
        post_time = str(int(time.time()))
        return HttpResponse(MESSAGE_TEXT_PICTURE % (to_user_name, from_user_name, post_time, title, description, pic_url
                                                    , url))


class GetOpenId:
    def get_code(self, app_id, redirect_uri, response_type, scope, state):
        print("开始获取code")
        print(app_id)
        # get_parameters = {}
        app_id = app_id.strip()
        app_id = {'appid': app_id}
        redirect_uri = {'redirect_uri': redirect_uri}
        response_type = {'response_type': response_type}
        scope = {'scope': scope}
        state = {'state': state}
        url = "https://open.weixin.qq.com/connect/oauth2/authorize"
        # 拼接字符串
        app_id = urllib.parse.urlencode(app_id)
        redirect_uri = urllib.parse.urlencode(redirect_uri)
        print(redirect_uri)
        response_type = urllib.parse.urlencode(response_type)
        scope = urllib.parse.urlencode(scope)
        state = urllib.parse.urlencode(state)
        get_data = "?"+app_id+'&'+redirect_uri+'&'+response_type+'&'+scope+'&'+state
        print(get_data)
        req = url + str(get_data) + "#wechat_redirect"
        print(req)
        # response = urllib.request.urlopen(req)
        return HttpResponseRedirect(req)
        # print(response.msg)
        # return ''

    def get_open_id_id(self, app_id, secret, code, grant_type):
        print("开始获取openid")
        get_parameters = {}
        get_parameters['appid'] = app_id.strip()
        get_parameters['secret'] = secret.strip()
        get_parameters['code'] = code
        get_parameters['grant_type'] = grant_type
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        # 拼接字符串
        get_data = "?" + urllib.parse.urlencode(get_parameters)
        print(get_data)
        req = urllib.request.Request(url + get_data)
        response = urllib.request.urlopen(req)
        result = response.read()
        mystr = result.decode("utf-8")
        my_josn = json.loads(mystr)
        open_id = my_josn.get('openid')
        print('解码后'+mystr)
        return open_id


class OpenidViewRequired:
    def _get_open_id(self, request, code, next_view):
        print('_get_open_id')
        site_settings = SiteSettings.get_settings()
        # redirect_uri = "%s/wss/mine/my_account/" % (self.STATIC_HOST)
       # redirect_uri = "http://china-legoo.com{0}?{1}".format(next_view, urllib.parse.urlencode(request.GET))
        host = request.get_host()
        redirect_uri = "http://"+host+"{0}?{1}".format(next_view, urllib.parse.urlencode(request.GET))
        print("重定向地址"+redirect_uri)
        if not code:
            print("没有code，访问url获取code")
            print(site_settings.wechat_app_id)
            return self.open_tools.get_code(app_id=site_settings.wechat_app_id, redirect_uri=redirect_uri, response_type='code', scope='snsapi_base', state='1')
        else:
            print("有code，通过code获取openid")
            open_id = self.open_tools.get_open_id_id(app_id=site_settings.wechat_app_id, secret=site_settings.wechat_app_secret, code=code, grant_type='authorization_code')
            print("获取到openid："+open_id)
            return open_id
    
    @staticmethod
    def _get_user(open_id):
        print('_get_user===============')
        client = Client.objects(wx_id=open_id).first()
        # print('微信客户的电话：'+client)
        if client:
            return client.user, client.user_type
        else:
            print("未找到用户，走绑定流程")
            return '', ''

    @staticmethod
    def _bind_view(open_id, next_view, referee_id):
        print('_bind_view')
        get_parameters = {}
        get_parameters['open_id'] = open_id
        get_parameters['next_view'] = next_view
        get_parameters['referee_id']=referee_id
        get_data = "?" + urllib.parse.urlencode(get_parameters)
        print('绑定get_data:'+get_data)
        return HttpResponseRedirect(reverse('wss:bind') + get_data)

    @staticmethod
    def _certificate():
        # print('_certificate')
        # get_parameters = {}
        # get_parameters['open_id'] = open_id
        # get_parameters['next_view'] = next_view
        # get_data = "?" + urllib.parse.urlencode(get_parameters)
        return HttpResponseRedirect(reverse('wss:certificate'))

    @staticmethod
    def _auto_login(request, user):
        print('_auto_login')
        client = Client.objects(user=user).first()
        print("phone："+ client.profile.phone)
        password = client.password
        print("user密码："+ password)
        username = user.username
        user = authenticate(username=username, password=password)
        login(request, user)

    def __init__(self, func):
        print('__init__')
        self.func = func
        self.open_tools = GetOpenId()
        self.STATIC_HOST = settings.SERVER_URL

    def __call__(self, *args, **kwargs):
        print('__call__')
        request = args[0]
        user = request.user
        print("user__call__进入:"+user.username)
        print(request.user.is_authenticated())
        if request.user.is_authenticated():
            path = request.META['PATH_INFO']
            print('注册类型：'+str(request.user.first_name))
            print('地址：'+str(path))
            if request.user.first_name == 'registered' and '/wss/certificate/' not in path:
                if Certificate.objects(client=Client.objects(user=request.user).first(), state='init').count() == 0:
                     if '/second/wx_publish_info/' in path:
                            request.session['message'] = "注册用户请先进行会员认证，认证后方可使用发布货物部分功能"
                            return OpenidViewRequired._certificate()
                     else:
                         return self.func(*args, **kwargs)
                            
                else:
                     if '/second/wx_publish_info/' in path: 
                            data = {}
                            context = RequestContext(request)
                            data['message'] = "您的认证正在审查，请耐心等待，如有问题联系客服。"
                            return render_to_response('wss/warn.html', data, context)
                     else:
                            return self.func(*args, **kwargs)

            return self.func(*args, **kwargs)
        else:
            #next_view = request.META.get('PATH_INFO', '')
            next_view = request.get_full_path()  #获取完整参数
            if "?" in next_view:
                next_view_url = next_view.split('?') [0]
            else:
                next_view_url = next_view
            print("下一个链接地址:"+next_view)
            code = request.GET.get('code', '')
            open_id = request.GET.get('open_id', '')
            print("CODE:"+code)
            print("OPEN_ID:"+open_id)
            if not open_id:
                open_id = self._get_open_id(request, code, next_view_url)
                if not isinstance(open_id, str):
                    # 获取open_id失败，使用重定向获取Code
                    return open_id
            user, user_type = OpenidViewRequired._get_user(open_id)
            print("__call__用户类型"+user_type)
            
            #test referee_id
            test1 = RequestTools(request)
            referee_id=test1.get_parameter('referee_id', '')
            if not user:
                print("__call__绑定")
                return OpenidViewRequired._bind_view(open_id, next_view, referee_id)
            elif not user.is_active:
                request.session['message'] = '登陆失败：用户状态异常'
                return OpenidViewRequired._bind_view(open_id, next_view,referee_id)
            OpenidViewRequired._auto_login(request, user)
            return self.func(*args, **kwargs)


#判断用户是否已绑定帐号
class OpenidRequired:
    def __init__(self, func):
        print("装饰类：初始化")
        self.func = func
        self.we_chat_tools = WeChatTools()
        self.STATIC_HOST = settings.SERVER_URL
        self.string_tools = tools_string.StringTools()

    def _get_user(self, openid):
        return []

    def _get_openid(self, args, kwargs):
        return ""

    def _get_request(self, args, kwargs):
        return ''

    def _login(self, request, title):
        print("装饰类：返回登录信息")
        #todo  hyper_link_response
        xml = ElementTree.fromstring(request.body)
        server_id = xml.find("ToUserName").text
        user_open_id = xml.find("FromUserName").text
        print("新用户：" + user_open_id)
        description = self.string_tools.get_string("wechat_login_message")
        url = "%s/wss/bind/" % (self.STATIC_HOST)
        pic = "%s/static/pic/default/favicon.ico" % self.STATIC_HOST
        return self.we_chat_tools.single_text_picture_response(from_user_name=server_id, to_user_name=user_open_id,
                                                               title=title, description=description, url=url,
                                                               pic_url=pic)

    def __call__(self, *args, **kwargs):
        print("装饰类：启动")
        openid = self._get_openid(args, kwargs)
        users = self._get_user(openid)
        if isinstance(users, int):
            user_count = users
        else:
            user_count = len(users)
        if user_count <= 0:
            # 用户没有绑定
            return self._login(self._get_request(args, kwargs), title=self.string_tools.get_string("wechat_login_title"))
        else:
            return self.func(*args, **kwargs)


class CreateXML(object):
    toUser = ""
    fromUser = ""
    createTime = 0
    msgType = ""
    articleCount = 0
    items = []

    def __init__(self, to_user, from_user, create_time, msg_type):
        self.toUser = to_user
        self.fromUser = from_user
        self.createTime = create_time
        self.msgType = msg_type
        self.articleCount = 0
        self.items = []

    def add_item(self, item):
        self.items.append(item)
        self.articleCount += 1

    def get_size(self):
        return self.articleCount

    def create(self):
        #创建一个Document文档
        doc = Document()
        # 创建一个根元素
        xml = doc.createElement('xml')
        doc.appendChild(xml)
        # 创建<ToUserName>
        to_user_name = doc.createElement('ToUserName')
        to_user_name_text = doc.createCDATASection(self.toUser)
        to_user_name.appendChild(to_user_name_text)
        xml.appendChild(to_user_name)
        # print ("create ToUserName finish")
        # 创建<FromUserName>
        from_user_name = doc.createElement('FromUserName')
        from_user_name_text = doc.createCDATASection(self.fromUser)
        from_user_name.appendChild(from_user_name_text)
        xml.appendChild(from_user_name)
        # print ("create FromUserName finish")
        # 创建<CreateTime>
        create_time = doc.createElement('CreateTime')
        create_time_text = doc.createCDATASection(str(self.createTime))
        create_time.appendChild(create_time_text)
        xml.appendChild(create_time)
        # print ("create CreateTime finish")
        # 创建<MsgType>
        msg_type = doc.createElement('MsgType')
        msg_type_text = doc.createCDATASection(self.msgType)
        msg_type.appendChild(msg_type_text)
        xml.appendChild(msg_type)
        # print ("create MsgType finish")
        # 创建<ArticleCount>
        article_count = doc.createElement('ArticleCount')
        article_count_text = doc.createCDATASection(str(self.articleCount))
        article_count.appendChild(article_count_text)
        xml.appendChild(article_count)
        # print ("create ArticleCount finish")
        # 创建<Articles>
        articles = doc.createElement('Articles')
        for item in self.items:
            articles.appendChild(item)
        xml.appendChild(articles)
        return str(doc.toprettyxml(indent = ''))


class CreateItem(object):
    title_content = ""
    description_content = ""
    picurl_content = ""
    url_content = ""

    def __init__(self, title_content, description_content, picurl_content, url_content):
        self.title_content = title_content
        self.description_content = description_content
        self.picurl_content = picurl_content
        self.url_content = url_content

    def create(self):
        doc = Document()
        item = doc.createElement('item')
        doc.appendChild(item)
        # 创建<Title>
        title = doc.createElement('Title')
        title_text = doc.createCDATASection(self.title_content)
        title.appendChild(title_text)
        item.appendChild(title)
        # print ("create title finish")
        # 创建<Description>
        description = doc.createElement('Description')
        description_text = doc.createCDATASection(self.description_content)
        description.appendChild(description_text)
        item.appendChild(description)
        # print ("create description finish")
        # 创建<PicUrl>
        picurl = doc.createElement('PicUrl')
        picurl_text = doc.createCDATASection(self.picurl_content)
        picurl.appendChild(picurl_text)
        item.appendChild(picurl)
        # print ("create PicUrl finish")
        # 创建<Url>
        url = doc.createElement('Url')
        url_text = doc.createCDATASection(self.url_content)
        url.appendChild(url_text)
        item.appendChild(url)
        # print ("create url finish")
        return item