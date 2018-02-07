from django.views.decorators.csrf import csrf_exempt
from wss.tools import *
#js_ticket
from wss.views_ticket import *
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from mongoengine.django.auth import User, make_password
from common.tools import *
from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
import traceback
from wss.tools_wechat import OpenidViewRequired
from django.core.urlresolvers import reverse
import re
from common.models import *
from bms.tools import DocumentBmsTools
from wss.tools_wx_config import ConfigTools
from wss.views_menu import MenuManager
import os, base64
#添加xml文件
from xml.etree import ElementTree

from wss.views_sendmessage import  send_wx_message
from common import tools_string
import qrcode
# 用来接收微信服务器的访问请求，初步分类
# 如果是POST方式，视为服务器推送请求
# 如果是GET方式，视为服务器验证请求
@csrf_exempt
def we_chat_receiver(request):
    try:
        wss_tools = WssTools(request)
        if request.method == 'POST':
            print(request.body)
            # 每次发消息时都要检测
            if wss_tools.check_signature():     # 检测消息真实性
#                 wx = MenuManager()
#                 accessToken = wx.get_access_token()
#                 wx.createmenu(accessToken)  #创建菜单
                response = wss_tools.response_message()
                return response
            else:
                print("invalid request")
                return HttpResponse("invalid request")
        elif request.method == 'GET':   # 微信服务器与公众账号服务器绑定时用Get，只此一次。即公众账号与微信服务器绑定
            response = wss_tools.check_signature_request()
            return response
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return HttpResponse("invalid request")

#
# #绑定
@csrf_exempt
@JSAPI_TICKET_Required
def view_bind(request):
    print("开始绑定：------------------------")
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    open_id = request_tool.get_parameter('open_id').strip()
    #test referee_id
    referee_id=request_tool.get_parameter('referee_id','')
    print('绑定open_id：'+open_id)
    next_view = request_tool.get_parameter('next_view').strip()
    print('绑定next_view：'+next_view)
    data['open_id'] = open_id
    data['next_view'] = next_view
    #test referee_id
    data['referee_id'] = referee_id
    
    request.session['open_id'] = open_id
    request.session['next_view'] = next_view
    if request.method == 'POST':
        data['posted_data'] = request.POST
        print("进入绑定post方法中")
        username = request_tool.get_parameter('username').strip()
        password = request_tool.get_parameter('password').strip()

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                if user.is_staff:
                    data['message'] = "登陆失败，管理员账号不可绑定"
                    return render_to_response('wss/bind.html', data, context)
            else:
                data['message'] = '登陆失败，用户未激活或被冻结'
                return render_to_response('wss/bind.html', data, context)
        else:
            # Django登录失败，尝试使用客户登陆流程
            user, entity = DocumentTools.multi_authenticate(username, ConvertTools.get_sha1_string(password))
            if user and entity:
                try:
                    client = Client.objects(user=user).first()
                    if Client.objects(user=user).count() == 0:
                        data['message'] = '登陆失败，未找到用户登陆信息。'
                        return render_to_response('wss/bind.html', data, context)
                except:
                    data['message'] = '登陆失败，未找到用户登陆信息'
                    return render_to_response('wss/bind.html', data, context)
                
                print('微信绑定过的数量：'+str(Client.objects(wx_id=open_id).count()))
                if client.wx_id:
                    data['message'] = '登陆失败，用户绑定过微信'
                if open_id == '':
                    data['message'] = '登陆失败，未获取到微信id号，请退出重新登陆'
                elif Client.objects(wx_id=open_id).count() > 0 :
                    if Client.objects(wx_id=open_id).count() == 1:
                        client_test =Client.objects(wx_id=open_id).first()
                        if client_test != client :
                            data['message'] = '登陆失败，微信账号已绑定过用户'
                    else:
                        data['message'] = '登陆失败，微信账号已绑定过用户'
                elif client.wx_id:
                    data['message'] = '登陆失败，用户登陆过微信，请退出登陆'
                else:
                    client.wx_id = open_id
                    print("完成绑定："+open_id)
                    client.save()
                    return HttpResponseRedirect(next_view + "?"+'next_view='+next_view+'&'+'open_id='+open_id)
                    #此处不完整，应该跳转来源页面
                return render_to_response('wss/bind.html', data, context)
            else:
                data['message'] = '登录失败，用户名、密码错误'
                return render_to_response('wss/bind.html', data, context)

    elif request.method == 'GET':
        print("进入绑定get方法中")
        # open_id = request.session.get('open_id', '')
        # request.session['open_id'] = ''
        # next_view = request.session.get('next_view', '')
        # request.session['next_view'] = ''
        return render_to_response('wss/bind.html', data, context)


# #解除绑定
@csrf_exempt
@JSAPI_TICKET_Required
def view_unbind(request):
    print("开始解除绑定：------------------------")
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    client_request = Client.objects(user=request.user).first()
    request_tool.check_message(data)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        print("进入解除绑定post方法中")
        username = request_tool.get_parameter('username').strip()
        client_1 = Client.objects(profile__phone=username).first()
        password = request_tool.get_parameter('password').strip()
        password = hashlib.sha1(password.encode('utf-8')).hexdigest()
        if not client_1:
            request_tool.set_message('退出失败，用户名不存在！')
            return HttpResponseRedirect(reverse('wss:unbind'))
        username = client_1.user.username
        user = authenticate(username=username, password=password)
        if not user:
            print("密码错误")
            request_tool.set_message('退出失败，用户名、密码错误')
            return HttpResponseRedirect(reverse('wss:unbind'))
            # data['message'] = '解除绑定失败，用户名、密码错误'
            # return render_to_response('wss/unbind.html', data, context)
        print(user)
        client = Client.objects(user=user).first()
        print(client)
        if client_request:
            if client == client_request:
                client.wx_id = ''
                logout(request)
                client.save()
                request_tool.set_message('您已经退出登陆')
                return HttpResponseRedirect(reverse('wss:success'))
                # data['message'] = '您已经成功解除绑定，请绑定新页面'
                # return render_to_response('wss/mine/my_account.html', data, context)
            else:
                print('绑定的账号不一致')
                # request_tool.set_message('您输入的账号和绑定的账号不一致')
                # return HttpResponseRedirect(reverse('wss:unbind'))
                data['message'] = "退出失败，绑定的账号不一致。"

                data['alj'] = 'woainizhongguo'
                return render_to_response('wss/unbind.html', data, context)
                # data['message'] = '您输入的账号和绑定的账号不一致'
                # return render_to_response('wss/unbind.html', data, context)
        else:
            print('与登陆的账号不一致')
            request_tool.set_message('登陆用户不存在')
            return HttpResponseRedirect(reverse('wss:unbind'))
            # data['message'] = '绑定用户不存在'
            # return render_to_response('wss/unbind.html', data, context)
    elif request.method == 'GET':
        data['client'] = client_request
        request_tool.set_message('')
        return render_to_response('wss/unbind.html', data, context)


# #解除绑定空页面
@csrf_exempt
def view_unbind_null(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    return render_to_response('wss/unbind_null.html', data, context)

#注册 修改
# @JSAPI_TICKET_Required
def view_register(request):
    print("开始注册：------------------------")
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    open_id = request.session.get('open_id', '')
    #test referee_id
    referee_id=request_tool.get_parameter('referee_id', '')
    
    print('注册open_id：'+open_id)
    next_view = request.session.get('next_view', '')
    print('注册next_view：'+next_view)
    data['open_id'] = open_id
    data['next_view'] = next_view

    if request.method == 'POST':
        try:
            print("进入注册post方法中")
            data['posted_data'] = request.POST
            phone = request_tool.get_parameter('phone', '')
            password = request_tool.get_parameter('password', '')
            password_again = request_tool.get_parameter('password_again', '')
            checkbox = request_tool.get_parameter('checkbox')
            verification_code = request_tool.get_parameter('verification_code', '')
            #下面两行代码为修改后代码
            code = request_tool.get_parameter('code')
            data['referee_phone'] = code
            if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', phone):
                data['message'] = '请输入正确的手机号码'
                return render_to_response('wss/register.html', data, context)
            if not password or not password_again:
                data['message'] = '密码或再次输入密码不能为空'
                return render_to_response('wss/register.html', data, context)
            if not re.match(r'^[a-zA-Z0-9]{6,12}$', password):
                data['message'] = '密码必须有6-12位的数字字母组合，不能是纯数字或纯字母组合'
                return render_to_response('wss/register.html', data, context)
            if  re.match(r'^[0-9]{6,12}$', password)  or re.match(r'^[a-zA-Z]{6,12}$', password) :
                data['message'] = '密码必须有6-12位的数字字母组合，不能是纯数字或纯字母组合。'
                return render_to_response('wss/register.html', data, context)
            if not checkbox:
                data['message'] = '注册用户必须同意运之宝协议'
                return render_to_response('wss/register.html', data, context)
            if password != password_again:
                data['message'] = '两次输入的密码不一致'
                return render_to_response('wss/register.html', data, context)
            if not verification_code:
                data['message'] = '验证码不能为空'
                return render_to_response('wss/register.html', data, context)
            #验证验证码
            DocumentTools.check_code(code=verification_code, phone=phone, code_type='register')
            #修改code位置，下面一行代码为原代码
#             code = request_tool.get_parameter('code')
            user = DocumentTools.get_user(phone)
            client = None
            if user is not None:
                data['message'] = '手机号已存在'
                return render_to_response('wss/register.html', data, context)

            if password == '':
                data['message'] = '密码不能为空'
                return render_to_response('wss/register.html',data, context)
            if code:
                client = Client.objects(profile__phone=code).first()
                if not client:
                    data['message'] = '您输入的推荐码不存在，请确认'
                    return render_to_response('wss/register.html', data, context)
            username = DocumentTools.get_username()
            password = hashlib.sha1(password.encode('utf-8')).hexdigest()
            user = User(username=username, password=make_password(password), first_name='registered')
            user.save()
            profile = UserProfile(phone=phone, user_id=user.id)
            registered = Client(user=user, profile=profile, password=password)
            if client:
                registered.referee = client.user
            registered.save()
            data['message'] = '注册成功'
            request_tool.set_message('注册成功')
            #return HttpResponseRedirect(reverse('wss:view_bind'))
            client = Client.objects(user=user).first()
#             client.wx_id = open_id
#             print("完成绑定："+open_id)
#             client.save()
#             
#             #注册成功通知信息
#             crteamtop = request.get_host()
#             certificate_url = "http://"+crteamtop+reverse('wss:certificate') + "?"+'next_view='+next_view+'&'+'open_id='+open_id
#             content = "恭喜，您已注册成功！成为运之宝注册会员，您的登陆账号为"+str(profile.phone)+",认证成功将获取更多会员权利，<a href='" +certificate_url+ "'>点击进行认证</a>"
#             
#             touser = client.wx_id
#             send_wx_message(touser,content)
            
            
#             #此处应该调到绑定页面
#             if next_view:
#                 #return HttpResponseRedirect(reverse('wss:bind') + "?"+'next_view='+next_view+'&'+'open_id='+open_id)
#                 return HttpResponseRedirect(reverse('wss:certificate') + "?"+'next_view='+next_view+'&'+'open_id='+open_id)
#             else:
#                 return render_to_response('wss/register.html', data, context)
        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('wss/register.html', data, context)
        #自动生成二维码
        try:
            create_code = wx_create_code_pic(request, client.id)
        except:
            pass
        try:
            client.wx_id = str(open_id)
            print("完成绑定："+open_id)
            client.save()
            
            #注册成功通知信息
            crteamtop = request.get_host()
            certificate_url = "http://"+crteamtop+reverse('wss:certificate') + "?"+'next_view='+next_view+'&'+'open_id='+open_id
            content = "恭喜，您已注册成功！成为运之宝注册会员，您的登陆账号为"+str(profile.phone)+",认证成功将获取更多会员权利，<a href='" +certificate_url+ "'>点击进行认证</a>"
            
            touser = client.wx_id
            send_wx_message(touser,content)
            #此处应该调到绑定页面
            data['message'] = '注册成功，欢迎成为运之宝大家庭的一员'
            return render_to_response('wss/success.html', data, context)
#             if next_view:
#                 #return HttpResponseRedirect(reverse('wss:bind') + "?"+'next_view='+next_view+'&'+'open_id='+open_id)
#                 return HttpResponseRedirect(reverse('wss:certificate') + "?"+'next_view='+next_view+'&'+'open_id='+open_id)
#             else:
#                 return render_to_response('wss/register.html', data, context)
        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('wss/register.html', data, context)
    elif request.method == 'GET':
        print("进入注册get方法中")
        if referee_id:
            try:
                client =  Client.objects(id =referee_id).first()
                data['referee_phone'] = client.profile.phone
            except:
                data['referee_phone'] = ""
           
        site_settings = SiteSettings.get_settings()
        data['user_protocol'] = site_settings.user_protocol
        return render_to_response('wss/register.html', data, context)


def user_agreement(request):
    context = RequestContext(request)
    # data = {}
    site_settings = SiteSettings.get_settings()
    return HttpResponse(site_settings.user_protocol)


#认证
@OpenidViewRequired
@JSAPI_TICKET_Required
def view_certificate(request):
    print("开始认证：------------------------")
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    wss_tools = DocumentWssTools(request)
    bms_tools = DocumentBmsTools(request)
    request_tool.check_message(data)

    client = Client.objects(user=request.user).first()
    print("获取用户："+str(client.user_type))
    count = Certificate.objects(client=client).count()
    print("认证数量："+str(count))
    data['user_types'] = Client.USER_TYPE
    data['user_classifys'] = Client.USER_CLASSIFY
    if client:
        print("有用户")
        data['registered'] = client
    else:
        print("无用户")
        data['message'] = '没有找到对应的注册用户'
        return render_to_response('wss/certificate.html', data, context)
    if count > 0:
        data['message'] = '用户不能二次认证'
        return render_to_response('wss/certificate.html', data, context)

    if request.method == 'POST':
        # data['posted_data'] = request.POST
        try:
            print('进入PSOT方法')
            certificate = Certificate()
            certificate = bms_tools.validation_certificate(certificate)
            certificate.client = client
            certificate.save()
             #申请认证通知管理员
            import datetime
            import time
            phone =  certificate.client.profile.phone
            nowtime = datetime.datetime.now()
            subtime = nowtime.strftime("%Y-%m-%d %H:%M:%S")
            content = "手机号码"+str(phone)+"已经提交认证，提交时间"+str(subtime)+"请审核！"
            string_tools = tools_string.StringTools()
            touser = string_tools.get_string("administrator_wx_id")
            send_wx_message(touser,content)
            # print(request.FILES.get('national_image', None))
            data['message'] = '申请成功，等待审核'
            return render_to_response('wss/unbind_null.html', data, context)
            # return HttpResponse('申请成功，请等待审核')
            # return HttpResponseRedirect(reverse('wss:unbind_null'))
        except CustomError as e:
            request_tool.set_message(e.message)
        except Exception as e:
            print(traceback.format_exc())
            request_tool.set_message(str(e))
        path = request.META['PATH_INFO']
        if 'result' in path:
            return HttpResponseRedirect(reverse('wss:certificate'))
        else:
            return HttpResponseRedirect(reverse('wss:certificate_result'))

    elif request.method == 'GET':
        print("进入GET方法")

        return render_to_response('wss/certificate.html', data, context)


def success(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    # data['message'] = "提交成功"
    if request.method == 'GET':
        return render_to_response('wss/success.html', data, context)
    
    
def warn(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    if request.method == 'GET':
        return render_to_response('wss/warn.html', data, context)

def update_data(request):
    data = {}
    # user_set = User.objects(first_name='registered')
    # client_set = Client.objects(user__in=user_set, user_type__ne='registered')
    # for client in client_set:
    #     client.user.update(set__first_name=client.user_type)
    #     print('{0}:{1}:{2}'.format(client.profile.phone, client.user.username, client.user_type))
    client = Client.objects(wx_id='o1UXRsjv4U7Tf8_4gyqta4rHdFfI').update(set__wx_id='')
    return HttpResponse(json.dumps(data))

# 忘记密码
def send_code(request):
    context = RequestContext(request)
    data={}
    request_tool = RequestTools(request)
    request_tool.check_message(data)

    if request.method == 'POST':
        try:
            data['posted_data'] = request.POST
            phone = request_tool.get_parameter('phone', '')
            if not re.match(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$', phone):
                data['message'] = '输入数据不能为空'
                return render_to_response('wss/forget_password1.html', data, context)
            verification_code = request_tool.get_parameter('verification_code', '')
            user = DocumentTools.get_user(phone)
            if not user:
                data['message'] = '你输入的手机号不存在'
                return render_to_response('wss/forget_password1.html', data, context)

            if not verification_code:
                data['message'] = '验证码不能为空'
                return render_to_response('wss/forget_password1.html', data, context)
            #验证验证码
            DocumentTools.check_code(code=verification_code, phone=phone, code_type='reset_password')
            data['phone'] = phone
            return render_to_response('wss/forget_password2.html', data, context)

        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('wss/forget_password1.html', data, context)

    elif request.method == 'GET':
        return render_to_response('wss/forget_password1.html', data, context)


# 重置密码
def update_password(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    if request.method == 'POST':
        try:
            data['posted_data'] = request.POST
            phone = request_tool.get_parameter('hidden_phone', '')
            data['phone'] = phone
            password = request_tool.get_parameter('password', '')
            password_again = request_tool.get_parameter('password_again', '')

            user = DocumentTools.get_user(phone)
            if not user:
                data['message'] = '你输入的手机号不存在'
                return render_to_response('wss/forget_password2.html', data, context)
            if not password or not password_again:
                data['message'] = '密码或再次输入密码不能为空'
                return render_to_response('wss/forget_password2.html', data, context)
            if not re.match(r'^[a-zA-Z0-9]{6,12}$', password):
                data['message'] = '密码必须有6-12位的数字字母组合'
                return render_to_response('wss/forget_password2.html', data, context)
            if password != password_again:
                data['message'] = '两次输入的密码不一致'
                return render_to_response('wss/forget_password2.html', data, context)
            DocumentTools.reset_password(password, user)
            data['message'] = '修改密码成功'

            if request.user == user:
                client = Client.objects(user=user).first()
                client.wx_id = ''
                logout(request)
                client.save()
            return render_to_response('wss/success.html', data, context)

        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('wss/forget_password2.html', data, context)

    elif request.method == 'GET':
        return render_to_response('wss/forget_password2.html', data, context)
    
@OpenidViewRequired
def update_my_password(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.check_message(data)

    if request.method == 'POST':
        try:
            data['posted_data'] = request.POST
            oldpassword = request_tool.get_parameter('oldpassword', '')
            password = request_tool.get_parameter('password', '')
            password_again = request_tool.get_parameter('password_again', '')
            client = Client.objects(user=request.user).first()
#             client = Client.objects(id='577dede653bc2b145bba28ff').first()
            user = client.user
            if not client:
                data['message'] = '您没有登录'
                return render_to_response('wss/bind.html', data, context)
            if not oldpassword or not password or not password_again:
                data['message'] = '输入不能为空'
                return render_to_response('wss/mine/update_password.html', data, context)
            
            oldpassword = hashlib.sha1(oldpassword.encode('utf-8')).hexdigest()
            if client.password != oldpassword:
                data['message'] = '旧密码不正确!'
                return render_to_response('wss/mine/update_password.html', data, context)
            
            if not re.match(r'^[a-zA-Z0-9]{6,12}$', password):
                data['message'] = '密码必须有6-12位的数字字母组合'
                return render_to_response('wss/mine/update_password.html', data, context)
            if password != password_again:
                data['message'] = '两次输入的密码不一致'
                return render_to_response('wss/mine/update_password.html', data, context)
            
            password =  hashlib.sha1(password.encode('utf-8')).hexdigest()
            user.set_password(password)
            client.update(set__password=password)
            data['message'] = '修改密码成功'
            return render_to_response('wss/success.html', data, context)

        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('wss/mine/update_password.html', data, context)

    elif request.method == 'GET':
        return render_to_response('wss/mine/update_password.html', data, context)
    
    
    
    
    
    
    
    
def view_register_code(request):
    print("开始注册：------------------------")
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    open_id = request.session.get('open_id', '')
    #test referee_id
    referee_id=request_tool.get_parameter('referee_id', '')
    
    print('注册open_id：'+open_id)
    next_view = 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzI0MzQwNzcxMw==&scene=124#wechat_redirect'
    print('注册next_view：'+next_view)
    data['open_id'] = open_id
    data['next_view'] = next_view

    if request.method == 'POST':
        try:
            print("进入注册post方法中")
            data['posted_data'] = request.POST
            phone = request_tool.get_parameter('phone', '')
            password = request_tool.get_parameter('password', '')
            password_again = request_tool.get_parameter('password_again', '')
            checkbox = request_tool.get_parameter('checkbox')
            verification_code = request_tool.get_parameter('verification_code', '')
            #下面两行代码为修改后代码
            code = request_tool.get_parameter('code')
            data['referee_phone'] = code
            if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', phone):
                data['message'] = '请输入正确的手机号码'
                return render_to_response('wss/register_code.html', data, context)
            if not password or not password_again:
                data['message'] = '密码或再次输入密码不能为空'
                return render_to_response('wss/register_code.html', data, context)
            if not re.match(r'^[a-zA-Z0-9]{6,12}$', password):
                data['message'] = '密码必须有6-12位的数字字母组合，不能是纯数字或纯字母组合'
                return render_to_response('wss/register_code.html', data, context)
            if  re.match(r'^[0-9]{6,12}$', password)  or re.match(r'^[a-zA-Z]{6,12}$', password) :
                data['message'] = '密码必须有6-12位的数字字母组合，不能是纯数字或纯字母组合。'
                return render_to_response('wss/register_code.html', data, context)
            if not checkbox:
                data['message'] = '注册用户必须同意运之宝协议'
                return render_to_response('wss/register_code.html', data, context)
            if password != password_again:
                data['message'] = '两次输入的密码不一致'
                return render_to_response('wss/register_code.html', data, context)
            if not verification_code:
                data['message'] = '验证码不能为空'
                return render_to_response('wss/register_code.html', data, context)
            #验证验证码
            DocumentTools.check_code(code=verification_code, phone=phone, code_type='register')
            #修改code位置，下面一行代码为原代码
#             code = request_tool.get_parameter('code')
            user = DocumentTools.get_user(phone)
            client = None
            if user is not None:
                data['message'] = '手机号已存在'
                return render_to_response('wss/register_code.html', data, context)

            if password == '':
                data['message'] = '密码不能为空'
                return render_to_response('wss/register_code.html',data, context)
            if code:
                client = Client.objects(profile__phone=code).first()
                if not client:
                    data['message'] = '您输入的推荐码不存在，请确认'
                    return render_to_response('wss/register_code.html', data, context)
            username = DocumentTools.get_username()
            password = hashlib.sha1(password.encode('utf-8')).hexdigest()
            user = User(username=username, password=make_password(password), first_name='registered')
            user.save()
            profile = UserProfile(phone=phone, user_id=user.id)
            registered = Client(user=user, profile=profile, password=password)
            if client:
                registered.referee = client.user
            registered.save()
            data['message'] = '注册成功'
            #return HttpResponseRedirect(reverse('wss:view_bind'))
            client1 = Client.objects(user=user).first()

            #return HttpResponseRedirect(reverse('wss:view_register_pic'))
        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('wss/register_code.html', data, context)
        #自动生成二维码
        try:
            create_code = wx_create_code_pic(request, client1.id)
            if create_code != 'success':
                data['message'] = '注册成功'+str(create_code)
                return render_to_response('wss/warn.html', data, context)
        except Exception as e:
            data['message'] = '注册成功'+str(e)
            return render_to_response('wss/warn.html', data, context)
        try:
            client1.wx_id = open_id
            print("完成绑定："+open_id)
            client1.save()
        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('wss/register_code.html', data, context)
        
        return HttpResponseRedirect(reverse('wss:view_register_pic'))

    elif request.method == 'GET':
        print("进入注册get方法中")
        if referee_id:
            try:
                client =  Client.objects(id =referee_id).first()
                data['referee_phone'] = client.profile.phone
            except:
                data['referee_phone'] = ""
           
        site_settings = SiteSettings.get_settings()
        data['user_protocol'] = site_settings.user_protocol
        return render_to_response('wss/register_code.html', data, context)
    
#注册成功扫描关注二维码页面
def view_register_pic(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/register_concern.html', data, context)


#创建二维码图片
def wx_create_code_pic(request,client_id):
     #根据用户身份区分返回页面结束
    try:
        client = Client.objects(id=client_id).first()
    except:
        return  '未找到对应数据'
    
    try:
        BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
        phone=client.profile.phone
        path = BASE_ROOT+"/static/pic/user_code/"+str(client.id)+".png" 
        #img = qrcode.make('https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzI0MzQwNzcxMw==&scene=124#wechat_redirect')
        #自动获取域名
        host = request.get_host()
        main_url="http://"+host+"/wss/register_code/?referee_id="+str(client.id)
        img=qrcode.make(str(main_url))
        img.save(path)
        request.session['code_message'] = '成功更新二维码'
    except Exception as e:
        return  str(e)
    try:
        client.QR_code_image = "/static/pic/user_code/"+str(client.id)+".png" 
        client.save()
        return 'success'
    except:
        return'保存路径失败，请稍后点击更新二维码'
    
    
    
#验证是否认证
@OpenidViewRequired
@JSAPI_TICKET_Required
def view_certificate_test(request,client_id):
    print("开始认证：------------------------")
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    wss_tools = DocumentWssTools(request)
    bms_tools = DocumentBmsTools(request)
    request_tool.check_message(data)
    client = Client.objects(id=client_id).first()

    #client = Client.objects(user=request.user).first()
    print("获取用户："+str(client.user_type))
    count = Certificate.objects(client=client).count()
    print("认证数量："+str(count))
    data['user_types'] = Client.USER_TYPE
    data['user_classifys'] = Client.USER_CLASSIFY
    if client:
        print("有用户")
        data['registered'] = client
    else:
        print("无用户")
        data['message'] = '没有找到对应的注册用户'
        return render_to_response('wss/certificate.html', data, context)
    
    if count == 0:
        return HttpResponseRedirect(reverse('wss:certificate'))
    elif count > 0:
        try:
            certificate = Certificate.objects(client=client).first()
        except Exception as e:
            data['message'] = '网络不稳定，发生错误，错误码：'+str(e)
            return render_to_response('wss/warn.html', data, context)
        if certificate.state == 'init':
            data['message'] = '您已成功申请认证，审核暂未通过，不能查看信息'
            return render_to_response('wss/success.html', data, context)
        elif certificate.state == 'success':
            data['message'] = '认证成功'
            return render_to_response('wss/mine/certificate_pic_list.html', data, context)
            #return render_to_response('wss/success.html', data, context)
        else:
            data['message'] = '网络不稳定，未获取用户认证状态'
            return render_to_response('wss/warn.html', data, context)

 

    
    
    