__author__ = 'mlzx'
import hashlib
from django.contrib.auth.decorators import login_required
from common.decorators import AdminRequired
from common.decorators import SuperAdminRequired
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from mongoengine.django.auth import User, make_password
# from common.tools_legoo import *
from common.tools import *
from bms.tools import DocumentBmsTools
from django.shortcuts import render_to_response, HttpResponse
import traceback
from common.decorators import *
import datetime

from wss.views_sendmessage import  send_wx_message
from common import tools_string
import os

import qrcode

from common.tools_excel_export import ExcelExportTools
from django.contrib.staticfiles.templatetags.staticfiles import static

#－－－－－－－－－－－－－－－－－－－－－－－－－－管理员－－－－－－－－－－－－－－－－－－－－－－－－－－
# 管理员列表
@login_required
@AdminRequired
def admin_list(request, page_index):
    context = RequestContext(request)
    page_index = int(page_index)
    if request.method == 'POST':
        request_tool = RequestTools(request)
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')

        if len(search_keyword) > 30:
            request.session['msg'] = '搜索关键字过长，请控制在30个字以内'
            return HttpResponseRedirect(reverse('bms:admin_list', args=[request.session.get('page_index', '1'), ]))

        request.session['search_keyword_admin'] = search_keyword
        request.session['page_index_admin'] = 1

        return HttpResponseRedirect(reverse('bms:admin_list', args=[1, ]))

    elif request.method == 'GET':
        if request.user.is_superuser is False:
            return render_to_response('bms/user/admin_only.html', {}, context)

        msg = request.session.get('msg', '')
        request.session['msg'] = ''

        search_keyword = request.session.get('search_keyword_admin', '')
        user_set = User.objects(is_staff=True, username__contains=search_keyword)
        admin_count = user_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, admin_count)
        request.session['page_index_admin'] = paging['page_index']
        admins = user_set.order_by('-date_joined')[
                 paging['start_item']: paging['end_item']]

        return render_to_response('bms/user/admin_list.html',
                                  {'admins': admins, 'msg': msg, 'search_keyword': search_keyword, 'paging': paging},
                                  context)


@login_required
@SuperAdminRequired
def admin_edit(request, admin_id):
    context = RequestContext(request)
    request_tool = RequestTools(request)
    request_tool.save_log()
    page_index = request.session.get('page_index', '1')
    admin = User.objects.get(id=admin_id)
    return render_to_response('bms/user/admin_edit.html', {'admin': admin, 'page_index': page_index}, context)


@login_required
@SuperAdminRequired
def admin_save(request, admin_id):
    context = RequestContext(request)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        page_index = request.session.get('page_index', '1')

        user = User.objects.get(id=admin_id)
        if request.POST['password'] != '':
            new_password = request.POST['password']
            re_password = request.POST['re_password']
            if re_password =="":
                return render_to_response('bms/user/admin_edit.html',
                                          {'admin': user, 'page_index': page_index, 'alert': '确认密码未输入'}, context)
            if len(new_password) > 20:
                return render_to_response('bms/user/admin_edit.html',
                                          {'admin': user, 'page_index': page_index, 'alert': '密码最多20字'}, context)
            if re_password != new_password:
                return render_to_response('bms/user/admin_edit.html',
                                          {'admin': user, 'page_index': page_index, 'alert': '两次密码不一致，请检查后重新输入'}, context)

            user.set_password(new_password)

        if 'email' in request.POST:
            email = request.POST['email']
            if email == '':
                user.email = None
            else:
                if len(email) > 50:
                    return render_to_response('bms/user/admin_edit.html',
                                              {'admin': user, 'page_index': page_index, 'alert': '邮箱最多50字'}, context)

                user.email = email

        if request.POST.get('active', '') == "":
            pass
        elif ConvertTools.is_boolean(request.POST.get('active', '')):
            user.is_active = True
        else:
            user.is_active = False

        user.save()
        return HttpResponseRedirect(reverse('bms:admin_list', args=[page_index, ]))


@login_required
@SuperAdminRequired
def admin_create(request):
    context = RequestContext(request)
    request_tool = RequestTools(request)
    request_tool.save_log()
    if request.method == 'POST':

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')
        re_password = request.POST.get('re_password', '')

        user = User.objects(username=username).first()
        if user:
            page_index = request.session.get('page_index', '1')
            return render_to_response('bms/user/admin_create.html', {'posted_data': request.POST, 'alert': '该用户名已存在',
                                                                     'page_index': page_index}, context)
        if len(password) > 20:
            page_index = request.session.get('page_index', '1')
            return render_to_response('bms/user/admin_create.html', {'posted_data': request.POST, 'alert': '密码最多20字',
                                                                     'page_index': page_index}, context)
        if password != re_password:
            page_index = request.session.get('page_index', '1')
            return render_to_response('bms/user/admin_create.html', {'posted_data': request.POST, 'alert': '两次密码不一致，请检查后重新输入',
                                                                     'page_index': page_index}, context)

        user = User(username=username, password=make_password(password), is_staff=True, is_superuser=False, first_name='admin')
        if email != '':
            user.email = email

        if request.POST.get('active', ''):
            user.is_active = True
        else:
            user.is_active = False

        user.save()

        return HttpResponseRedirect(reverse('bms:admin_list', args=['1', ]))

    if request.method == 'GET':
        page_index = request.session.get('page_index', '1')
        return render_to_response('bms/user/admin_create.html', {'page_index': page_index}, context)



#－－－－－－－－－－－－－－－－－－－－－－－－－－注册用户－－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def registered_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    
    message = request.session.get('code_message', '')
    data['message'] = message
    request.session['code_message'] = ''
    password_message = request.session.get('password_message', '')
    data['password_message'] = password_message
    request.session['password_message'] = ''
    
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')

        request.session['search_keyword_registered'] = search_keyword
        request.session['page_index_registered'] = 1
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET

        search_keyword = request.session.get('search_keyword_registered', '')
        
        registered_set = Client.objects().filter(Q(name__contains=search_keyword) |
                                     Q(profile__phone__contains=search_keyword))

#         registered_set = Client.objects(user_type='registered').filter(Q(name__contains=search_keyword) |
#                                      Q(profile__phone__contains=search_keyword))

        state = request_tool.get_parameter("state", "active")
        if state == 'active':
            user_set = User.objects(is_active=True)
            registered_set = registered_set.filter(user__in=user_set)
        elif state == 'hidden':
            user_set = User.objects(is_active=False)
            registered_set = registered_set.filter(user__in=user_set)
            
        #2017/3/15修改页面显示
        registered_set_list=[]
        for registered_detail in registered_set:
            show_set = []
            try:
                certificate = Certificate.objects(client=registered_detail).first()
                certificate_count=Certificate.objects(client=registered_detail).count()
            except Exception as e :
                a=str(e)
                certificate_count=0
            #添加推荐人部分
            client_set=''
            try:
                client_detail = Client.objects(user=registered_detail.referee).first()        #推荐人信息
                if client_detail:
                    client_set=client_detail
            except:
                pass
            if  certificate:
                b=certificate.state
                show_set=[registered_detail,certificate_count,certificate,client_set]
            else:
                show_set=[registered_detail,certificate_count,'',client_set]
            registered_set_list.append(show_set)
            
        count = len(registered_set_list)
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_registered'] = paging['page_index']
        registered_set_list = registered_set_list[paging['start_item']:paging['end_item']]
        data['registereds'] = registered_set_list

#         count = registered_set.count()
#         page = PageTools()
#         paging = page.get_paging(5, page_index, count)
#         request.session['page_index_registered'] = paging['page_index']
#         registered_set = registered_set[paging['start_item']:paging['end_item']]
#         data['registereds'] = registered_set
        # data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/registered_list.html', data, context)


@login_required
@AdminRequired
def registered_create(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_registered', '1')
    data['page_index'] = page_index

    if request.method == 'POST':
        request_tool.save_log()
        data['posted_data'] = request.POST
        # nickname = request.POST.get('nickname', '')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        re_password = request.POST.get('re_password', '')
        code = request.POST.get('code', '')
        client = None
        if code:
            print('code：'+code)
            client = Client.objects(profile__phone=code).first()
            if not client:
                data['message'] = '您输入的推荐码不存在，请确认'
                return render_to_response('bms/user/registered_create.html', data, context)
        # user = DocumentTools.get_user(nickname)
        # if user is not None:
        #     data['message'] = '用户昵称已存在'
        #     return render_to_response('bms/user/registered_create.html', data, context)
        user = DocumentTools.get_user(phone)
        if user is not None:
            data['message'] = '手机号已存在'
            return render_to_response('bms/user/registered_create.html', data, context)

        if password == '':
            return render_to_response('bms/user/registered_create.html',
                                      {'posted_data': request.POST, 'message': '密码不能为空',
                                       'page_index': request.session.get('page_index_registered', '1')}, context)
        if re_password == '':
            return render_to_response('bms/user/registered_create.html',
                                  {'posted_data': request.POST, 'message': '确认密码不能为空',
                                   'page_index': request.session.get('page_index_registered', '1')}, context)
        if len(password) > 20:
            return render_to_response('bms/user/registered_create.html',
                                      {'posted_data': request.POST, 'message': '密码最多20字',
                                       'page_index': request.session.get('page_index_registered', '1')}, context)
        if password != re_password:
            return render_to_response('bms/user/registered_create.html',
                                      {'posted_data': request.POST, 'message': '两次密码不一致，请检查后重新输入',
                                       'page_index': request.session.get('page_index_registered', '1')}, context)
        username = DocumentTools.get_username()
        password = hashlib.sha1(password.encode('utf-8')).hexdigest()
        user = User(username=username, password=make_password(password), first_name='registered')
        if request.POST.get('active', '') == 'show':
            user.is_active = True
        else:
            user.is_active = False
        user.save()

        profile = UserProfile(phone=phone, user_id=user.id)
        registered = Client(user=user, profile=profile, password=password)
        if client:
            print('进入client推荐码')
            print(client.user)
            registered.referee = client.user
        registered.save()
        #生成二维码
        try:
            create_code = create_code_pic(request, registered.id)
            if create_code != 'success':
                request.session['code_message'] = str(create_code)
        except:
            request.session['code_message'] = '网络不稳定，用户生成二维码失败，可认证后手动刷新二维码'

        return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))

    if request.method == 'GET':
        data['page_index'] = page_index
        return render_to_response('bms/user/registered_create.html', data, context)

#2017添加注册用户详情页面
@login_required
@AdminRequired
def registered_detail(request, registered_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_registered', '1')
    registered = Client.objects(id=registered_id).first()
    data['registered'] = registered                 #注册用户
    referee_people = Client.objects(user=registered.referee).first()        #推荐人信息
    data['referee_people'] = referee_people    
    bms_tools = DocumentBmsTools(request)
    data['user_types'] = Client.USER_TYPE   
    message = request.session.get('message', '')
    data['message'] = message
    request.session['message'] = ''
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    data["USE_PROPERTY"] = InquiryInfo.USE_PROPERTY
    data["CAR_TYPE"] = InquiryInfo.CAR_TYPE
    posted_data = request.session.get('posted_data', '')
    request.session['posted_data'] = ''
    data["posted_data"] = posted_data
    #分解行驶证
    try:
        a=registered.plate_number
        short = registered.plate_number[0]
        mid = registered.plate_number[2]
        end = registered.plate_number[4:]
        data["short_number"]=short
        data["mid_number"]=mid
        data["end_number"]=end
    except:
        pass
    #优惠卷
    coupon_count = 0
    use_coupon_set = UseCoupon.objects(client=registered)
    if use_coupon_set:
        for use_coupon in use_coupon_set:
            if use_coupon.coupon.end_date > datetime.datetime.now():
                coupon_count += 1
    data['coupon_count'] = coupon_count
    data['use_coupons'] = use_coupon_set
    return render_to_response('bms/user/registered_detail_new.html', data, context)




@login_required
@AdminRequired
def registered_edit(request, registered_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_registered', '1')
    registered = Client.objects(id=registered_id).first()
    data['registered'] = registered                 #注册用户
    data['page_index'] = page_index
    certificate = Certificate.objects(client=registered).first()
    data['certificate'] = certificate
    client = Client.objects(user=registered.referee).first()        #推荐人信息
    if client:
        data["client"] = client
    print("保险公司注册用户：")
    print(registered.referee)

    if request.method == 'POST':
        request_tool.save_log()     #保存日志
        if request.POST['password'] != '':
            new_password = request.POST['password']
            re_password = request.POST['re_password']
            if re_password =="":
                data['message'] = '确认密码未输入'
                return render_to_response('bms/user/registered_edit.html', data, context)
            if len(new_password) > 20:
                data['message'] = '密码最多20字'
                return render_to_response('bms/user/registered_edit.html', data, context)
            if re_password != new_password:
                data['message'] = '两次密码不一致，请检查后重新输入'
                return render_to_response('bms/user/registered_edit.html', data, context)
            DocumentTools.reset_password(new_password, registered.user)
        phone = request.POST.get('phone', '')
        if phone != registered.profile.phone and DocumentTools.get_user(phone) is not None:
            data['message'] = '手机号已存在'
            return render_to_response('bms/user/registered_edit.html', data, context)
        if request.POST.get('active', '') == 'show':
            registered.user.is_active = True
        else:
            registered.user.is_active = False
        referee_phone=request.POST.get('referee_phone')
        referee_phone=referee_phone or None
        if referee_phone is None:
            registered.referee =referee_phone
        elif referee_phone==registered.profile.phone:
            data['message']='推荐人不可填写本人手机号'
            return render_to_response('bms/user/registered_edit.html',data,context)
        elif DocumentTools.get_user(referee_phone) is None:
            data['message'] = '推荐人不存在，请检查您所填写的号码'
            return render_to_response('bms/user/registered_edit.html', data, context)
        else:
            referee_user=Client.objects(profile__phone=referee_phone).first()
            registered.referee = referee_user.user
        registered.profile.phone = phone
        registered.user.save()
        registered.save()
        #return render_to_response('bms/user/registered_edit.html', data, context)
        return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
    return render_to_response('bms/user/registered_edit.html', data, context)


#－－－－－－－－－－－－－－－－－－－－－－－－－－认证用户－－－－－－－－－－－－－－－－－－－－－－－－－－
@login_required
@AdminRequired
def certificate_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_certificate'] = search_keyword
        request.session['page_index_certificate'] = 1
        state = request_tool.get_parameter("state")
        certification_goal = request_tool.get_parameter("certification_goal")
        get_parameter = "?state={0}&certification_goal={1}".format(state, certification_goal)
        return HttpResponseRedirect(reverse('bms:certificate_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        message = request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_certificate', '')
        certificate_set = Certificate.objects()
        certificate_set = request_tool.certificate_filter(certificate_set=certificate_set, keyword=search_keyword)
        count = certificate_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_certificate'] = paging['page_index']
        certificate_set = certificate_set[paging['start_item']:paging['end_item']]
        data['certificates'] = certificate_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/certificate_list.html', data, context)


@login_required
@AdminRequired
def certificate_detail(request, certificate_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_certificate', '1')
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    data['page_index'] = page_index
    insurance_product_car_set = InsuranceProducts.objects()
    # product_type='car'
    data['insurance_product_cars'] = insurance_product_car_set
    insurance_product_batch_set = InsuranceProducts.objects()
    # product_type='batch'
    data['insurance_product_batchs'] = insurance_product_batch_set
    insurance_product_ticket_set = InsuranceProducts.objects()
    # product_type='ticket'
    data['insurance_product_tickets'] = insurance_product_ticket_set
    data['certificate_id'] = certificate_id
    certificate = Certificate.objects(id=certificate_id).first()
    # print("用户认证的first_name："+ str(certificate.client.user.first_name))
    # certificate.client.user.first_name = 'boss'
    # certificate.client.user.save()
    # print("用户认证的first_name："+ str(certificate.client.user.first_name))
    if certificate:
        data['certificate'] = certificate
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:certificate_list', args=[certificate_id, page_index, ]))
    return render_to_response('bms/user/certificate_detail.html', data, context)


#申请认证
@login_required
@AdminRequired
def certificate_create(request, registered_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_certificate', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    request_tool = RequestTools(request)
    data['user_types'] = Client.USER_TYPE
    data['user_classifys'] = Client.USER_CLASSIFY
    registered = Client.objects(id=registered_id).first()
    count = Certificate.objects(client=registered).count()
    if registered:
        data['registered'] = registered
    else:
        request_tool.set_message('没有找到对应的注册用户')
        return HttpResponseRedirect(reverse('bms:registered_list', args=['1', ]))
    if count > 0:
        request_tool.set_message('用户不能二次认证')
        return HttpResponseRedirect(reverse('bms:registered_list', args=['1', ]))
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            certificate = Certificate()
            certificate = bms_tools.validation_certificate(certificate)
            certificate.client = registered
            certificate.save()
            request.session['message'] = '申请成功，请认证'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/user/certificate_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/user/certificate_create.html', data, context)
        try:
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
            return HttpResponseRedirect(reverse('bms:certificate_detail', args=[certificate.id, ]))
        except Exception as e:
            data['message'] = str(e)
            request.session['message'] = '申请成功，网络问题，通知管理员失败'
            return HttpResponseRedirect(reverse('bms:certificate_detail', args=[certificate.id, ]))
    elif request.method == 'GET':
        return render_to_response('bms/user/certificate_create.html', data, context)


#重新申请认证
@login_required
@AdminRequired
def certificate_reject_repeat(request, certificate_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_certificate', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    certificate = Certificate.objects(id=certificate_id).first()
    if certificate:
        data['certificate'] = certificate
    else:
        data['message'] = '没有找到上次认证信息信息'
        return HttpResponseRedirect(reverse('bms:registered_list', args=['1', ]))
    if certificate.state != 'fail':
        data['message'] = '认证状态不正确'
        return HttpResponseRedirect(reverse('bms:registered_list', args=['1', ]))
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            certificate = bms_tools.validation_certificate_repeat(certificate)
            certificate.state = 'init'
            certificate.save()
            request.session['message'] = '重新申请成功，请认证'
           
            return HttpResponseRedirect(reverse('bms:certificate_detail', args=[certificate.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
        return render_to_response('bms/user/certificate_create_repeat.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/user/certificate_create_repeat.html', data, context)


###认证成功
@login_required
@AdminRequired
def certificate_result(request, certificate_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.save_log()
    certificate = Certificate.objects(id=certificate_id).first()
    client = Client.objects(id=certificate.client.id).first()
    result = request.GET.get('type', '')
    insurance_product_car_set = InsuranceProducts.objects()
    # product_type='car'
    data['insurance_product_cars'] = insurance_product_car_set
    insurance_product_batch_set = InsuranceProducts.objects()
    # product_type='batch'
    data['insurance_product_batchs'] = insurance_product_batch_set
    insurance_product_ticket_set = InsuranceProducts.objects()
    # product_type='ticket'
    data['insurance_product_tickets'] = insurance_product_ticket_set
    try:
        if result:
            if result == 'product':
                insurance_product_car_id = request.POST.get('insurance_product_car_id', '')
                if insurance_product_car_id:
                    insurance_product_car = InsuranceProducts.objects(id=insurance_product_car_id).first()
                    if insurance_product_car:
                        certificate.product_car = insurance_product_car
                    else:
                        data['certificate'] = certificate
                        data['message'] = '您选择的运单产品不存在'
                        return render_to_response('bms/user/certificate_detail.html', data, context)
                else:
                    data['certificate'] = certificate
                    data['message'] = '请选择默认的发送运单产品'
                    return render_to_response('bms/user/certificate_detail.html', data, context)

                insurance_product_batch_id = request.POST.get('insurance_product_batch_id', '')
                if insurance_product_batch_id:
                    insurance_product_batch = InsuranceProducts.objects(id=insurance_product_batch_id).first()
                    if insurance_product_batch:
                        certificate.product_batch = insurance_product_batch
                    else:
                        data['certificate'] = certificate
                        data['message'] = '您选择的车次产品不存在'
                        return render_to_response('bms/user/certificate_detail.html', data, context)
                else:
                    data['certificate'] = certificate
                    data['message'] = '请选择默认的发送车次产品'
                    return render_to_response('bms/user/certificate_detail.html', data, context)

                insurance_product_ticket_id = request.POST.get('insurance_product_ticket_id', '')
                if insurance_product_ticket_id:
                    insurance_product_ticket = InsuranceProducts.objects(id=insurance_product_ticket_id).first()
                    if insurance_product_ticket:
                        certificate.product_ticket = insurance_product_ticket
                    else:
                        data['certificate'] = certificate
                        data['message'] = '您选择的单票产品不存在'
                        return render_to_response('bms/user/certificate_detail.html', data, context)
                else:
                    data['certificate'] = certificate
                    data['message'] = '请选择默认的发送单票产品'
                    return render_to_response('bms/user/certificate_detail.html', data, context)

            elif result == 'national':
                national_id = request.POST.get('modal_national_id', '')
                certificate.national_id = national_id
                national_name = request.POST.get('modal_national_name', '')
                certificate.name = national_name
                try:
                    national_effective_time = request.POST.get('modal_national_effective', '')
                    if national_effective_time:
                        now = datetime.datetime.now()
                        otherStyleTime = now.strftime("%Y-%m-%d ")
                        if otherStyleTime > national_effective_time:
                            data['certificate'] = certificate
                            data['message'] = '身份证有效时间不能早于当前时间'
                            return render_to_response('bms/user/certificate_detail.html', data, context)
                        certificate.national_effective_time = national_effective_time
                    else:
                        data['certificate'] = certificate
                        data['message'] = '请输入身份证有效时间'
                        return render_to_response('bms/user/certificate_detail.html', data, context)
                except Exception:
                    data['certificate'] = certificate
                    data['message'] = '身份证有效时间格式不正确,例：2015-08-08'
                    return render_to_response('bms/user/certificate_detail.html', data, context)
            elif result == 'driver':
                driver_id = request.POST.get('modal_driver_id', '')
                certificate.driver_id = driver_id
            elif result == 'plate':
                plate_id = request.POST.get('modal_plate_id', '')
                certificate.plate_number = plate_id
                car_type = request.POST.get('modal_car_type', '')
                certificate.car_type = car_type
                holder = request.POST.get('modal_holder', '')
                certificate.holder = holder
                use_property = request.POST.get('modal_use_property', '')
                certificate.use_property = use_property
                brand_digging = request.POST.get('modal_brand_digging', '')
                certificate.brand_digging = brand_digging
                engine_number = request.POST.get('modal_engine_number', '')
                certificate.engine_number = engine_number
                # try:
                issue_date = request.POST.get('modal_issue_date', '')
                if issue_date:
                    certificate.issue_date = issue_date
                # except Exception:
                #     data['certificate'] = certificate
                #     data['message'] = '发证日期时间格式不正确,例：2015-08-08'
                #     return render_to_response('bms/user/certificate_detail.html', data, context)
            elif result == 'transportation':
                transportation_id = request.POST.get('modal_transportation_id', '')
                certificate.transportation_license_id = transportation_id
            elif result == 'business':
                if not certificate.organ_image:
                    # or not certificate.tax_image
                    organ = request.POST.get('modal_business_organ', '')
                    # tax_id = request.POST.get('modal_business_tax', '')
                    if organ:
                        # and tax_id
                        certificate.organ = organ
                        # certificate.tax_id = tax_id
                    else:
                        data['certificate'] = certificate
                        data['message'] = '请填入有效的组织机构代码'
                        # 和税务登记证
                        return render_to_response('bms/user/certificate_detail.html', data, context)

                business_id = request.POST.get('modal_business_id', '')
                certificate.business_license_id = business_id
                business_name = request.POST.get('modal_business_name', '')
                certificate.company_name = business_name
            elif result == 'organ':
                organ_id = request.POST.get('modal_organ_id', '')
                certificate.organ = organ_id
            # elif result == 'tax':
            #     tax_id = request.POST.get('modal_tax_id', '')
            #     certificate.tax_id = tax_id
            elif result == 'operating':
                operating_id = request.POST.get('modal_operating_id', '')
                certificate.operating_permit_id = operating_id
            else:
                data['certificate'] = certificate
                data['message'] = '认证的证件不存在'
                return render_to_response('bms/user/certificate_detail.html', data, context)
        else:
            data['certificate'] = certificate
            data['message'] = '认证类型错误'
            return render_to_response('bms/user/certificate_detail.html', data, context)
        certificate.save()
    except Exception as e:
        request_tool.set_message(str(e))
        return HttpResponseRedirect(reverse('bms:certificate_detail', args=[certificate_id, ]))
    try:
        certificate.verify1()
        string_tools = tools_string.StringTools()
        content =  string_tools.get_string("wechat_certificate_sucess")
       # touser = "oYXlSwfedYTw0OtzfRy2SYpPrNE8"   
        touser = client.wx_id
        send_wx_message(touser,content)
    except Exception as e:
        pass
    finally:
        return HttpResponseRedirect(reverse('bms:certificate_detail', args=[certificate_id, ]))


###认证驳回
@login_required
@AdminRequired
def certificate_reject(request, certificate_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.save_log()
    certificate = Certificate.objects(id=certificate_id).first()
    data['certificate'] = certificate
    try:
        failed_reason = request.POST.get('fail', '')
        reject_list = request.POST.getlist('reject', [])
        note = request.POST.get('note', '')
        if failed_reason:
            certificate.failed_reason = failed_reason
        else:
            data['message'] = "驳回理由不能为空"
            return render_to_response('bms/user/certificate_detail.html', data, context)
        if reject_list:
            certificate.failed_fields = reject_list
        else:
            data['message'] = "驳回文件不能为空"
            return render_to_response('bms/user/certificate_detail.html', data, context)
        certificate.note = note
        certificate.state = 'fail'
        certificate.save()
    except Exception as e:
        request_tool.set_message(str(e))
        return HttpResponseRedirect(reverse('bms:certificate_detail', args=[certificate_id, ]))
    return HttpResponseRedirect(reverse('bms:certificate_detail', args=[certificate_id, ]))




#－－－－－－－－－－－－－－－－－－－－－－－－－－物流公司－－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def transport_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')

        request.session['search_keyword_transport'] = search_keyword
        request.session['page_index_transport'] = 1
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:transport_list', args=[1, ]) + get_parameter)

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_transport', '')
        transport_set = Client.objects(user_type='transport').filter(Q(name__contains=search_keyword) |
                                     Q(profile__phone__contains=search_keyword))
        state = request_tool.get_parameter("state", "active")
        if state == 'active':
            user_set = User.objects(is_active=True)
            transport_set = transport_set.filter(user__in=user_set)
        elif state == 'hidden':
            user_set = User.objects(is_active=False)
            transport_set = transport_set.filter(user__in=user_set)
        count = transport_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_transport'] = paging['page_index']
        transport_set = transport_set[paging['start_item']:paging['end_item']]
        data['transports'] = transport_set
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/transport_list.html', data, context)

@login_required
@AdminRequired
def transport_detail(request, transport_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_transport', '1')
    data['page_index'] = page_index
    data['transport_id'] = transport_id
    insurance_product_car_set = InsuranceProducts.objects()
    # product_type='car'
    data['insurance_product_cars'] = insurance_product_car_set
    insurance_product_batch_set = InsuranceProducts.objects()
    # product_type='batch'
    data['insurance_product_batchs'] = insurance_product_batch_set
    insurance_product_ticket_set = InsuranceProducts.objects()
    # product_type='ticket'
    data['insurance_product_tickets'] = insurance_product_ticket_set
    transport = Client.objects(id=transport_id).first()
    
    
    message = request.session.get('code_message', '')
    data['message'] = message
    request.session['code_message'] = ''
    coupon_count = 0
    use_coupon_set = UseCoupon.objects(client=transport)
    if use_coupon_set:
        for use_coupon in use_coupon_set:
            if use_coupon.coupon.end_date > datetime.datetime.now():
                coupon_count += 1
    data['coupon_count'] = coupon_count
    data['use_coupons'] = use_coupon_set

    client = Client.objects(user=transport.referee).first()
    if client:
        data["client"] = client
    if transport:
        data['transport'] = transport
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:transport_list', args=[transport_id, page_index, ]))
    return render_to_response('bms/user/transport_detail.html', data, context)


@login_required
@AdminRequired
def transport_edit(request, transport_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_transport', '1')
    transport = Client.objects(id=transport_id).first()
    data['transport'] = transport
    data['page_index'] = page_index
    insurance_product_car_set = InsuranceProducts.objects()
    # product_type='car'
    data['insurance_product_cars'] = insurance_product_car_set
    insurance_product_batch_set = InsuranceProducts.objects()
    # product_type='batch'
    data['insurance_product_batchs'] = insurance_product_batch_set
    insurance_product_ticket_set = InsuranceProducts.objects()
    # product_type='ticket'
    data['insurance_product_tickets'] = insurance_product_ticket_set

    if request.method == 'POST':
        request_tool.save_log()
        if request.POST['password'] != '':
            new_password = request.POST['password']
            DocumentTools.reset_password(new_password, transport.user)
        # name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        # if name != '':
        #     transport.name = name
        if phone != transport.profile.phone and DocumentTools.get_user(phone) is not None:
            data['message'] = '手机号已存在'
            return render_to_response('bms/user/transport_detail.html', data, context)

        insurance_product_car_id = request.POST.get('insurance_product_car_id', '')
        if insurance_product_car_id:
            insurance_product_car = InsuranceProducts.objects(id=insurance_product_car_id).first()
            if insurance_product_car:
                transport.product_car = insurance_product_car
            else:
                data['transport'] = transport
                data['message'] = '您选择的运单产品不存在'
                return render_to_response('bms/user/transport_detail.html', data, context)
        else:
            data['transport'] = transport
            data['message'] = '请选择默认的发送运单产品'
            return render_to_response('bms/user/transport_detail.html', data, context)

        insurance_product_batch_id = request.POST.get('insurance_product_batch_id', '')
        if insurance_product_batch_id:
            insurance_product_batch = InsuranceProducts.objects(id=insurance_product_batch_id).first()
            if insurance_product_batch:
                transport.product_batch = insurance_product_batch
            else:
                data['transport'] = transport
                data['message'] = '您选择的车次产品不存在'
                return render_to_response('bms/user/transport_detail.html', data, context)
        else:
            data['transport'] = transport
            data['message'] = '请选择默认的发送车次产品'
            return render_to_response('bms/user/transport_detail.html', data, context)

        insurance_product_ticket_id = request.POST.get('insurance_product_ticket_id', '')
        if insurance_product_ticket_id:
            insurance_product_ticket = InsuranceProducts.objects(id=insurance_product_ticket_id).first()
            if insurance_product_ticket:
                transport.product_ticket = insurance_product_ticket
            else:
                data['transport'] = transport
                data['message'] = '您选择的单票产品不存在'
                return render_to_response('bms/user/transport_detail.html', data, context)
        else:
            data['transport'] = transport
            data['message'] = '请选择默认的发送单票产品'
            return render_to_response('bms/user/transport_detail.html', data, context)
        # registered.profile.nickname = nickname
        # client.user.last_name = nickname
        if request.POST.get('active', '') == 'show':
            transport.user.is_active = True
        else:
            transport.user.is_active = False
        transport.profile.phone = phone
        transport.user.save()
        transport.save()
        request.session['message'] = '编辑成功'
        return HttpResponseRedirect(reverse('bms:transport_list', args=[page_index, ]))
    return render_to_response('bms/user/transport_detail.html', data, context)


#－－－－－－－－－－－－－－－－－－－－－－－－－－司机－－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def driver_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_driver'] = search_keyword
        request.session['page_index_driver'] = 1
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:driver_list', args=[1, ]) + get_parameter)

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_driver', '')
        driver_set = Client.objects(user_type='driver').filter(Q(name__contains=search_keyword) |
                                     Q(profile__phone__contains=search_keyword))
        state = request_tool.get_parameter("state", "active")
        if state == 'active':
            user_set = User.objects(is_active=True)
            driver_set = driver_set.filter(user__in=user_set)
        elif state == 'hidden':
            user_set = User.objects(is_active=False)
            driver_set = driver_set.filter(user__in=user_set)
        count = driver_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_driver'] = paging['page_index']
        driver_set = driver_set[paging['start_item']:paging['end_item']]
        data['drivers'] = driver_set
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/driver_list.html', data, context)


@login_required
@AdminRequired
def driver_detail(request, driver_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_driver', '1')
    data['page_index'] = page_index
    data['driver_id'] = driver_id
    insurance_product_car_set = InsuranceProducts.objects()
    # product_type='car'
    data['insurance_product_cars'] = insurance_product_car_set
    insurance_product_batch_set = InsuranceProducts.objects()
    # product_type='batch'
    data['insurance_product_batchs'] = insurance_product_batch_set
    insurance_product_ticket_set = InsuranceProducts.objects()
    # product_type='ticket'
    data['insurance_product_tickets'] = insurance_product_ticket_set
    driver = Client.objects(id=driver_id).first()
    
    message = request.session.get('code_message', '')
    data['message'] = message
    request.session['code_message'] = ''

    coupon_count = 0
    use_coupon_set = UseCoupon.objects(client=driver)
    if use_coupon_set:
        for use_coupon in use_coupon_set:
            if use_coupon.coupon.end_date > datetime.datetime.now():
                coupon_count += 1
    data['coupon_count'] = coupon_count
    data['use_coupons'] = use_coupon_set

    client = Client.objects(user=driver.referee).first()
    if client:
        data["client"] = client
    if driver:
        data['driver'] = driver
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:driver_list', args=[driver_id, page_index, ]))
    return render_to_response('bms/user/driver_detail.html', data, context)


@login_required
@AdminRequired
def driver_edit(request, driver_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_driver', '1')
    driver = Client.objects(id=driver_id).first()
    data['driver'] = driver
    data['page_index'] = page_index
    insurance_product_car_set = InsuranceProducts.objects()
    # product_type='car'
    data['insurance_product_cars'] = insurance_product_car_set
    insurance_product_batch_set = InsuranceProducts.objects()
    # product_type='batch'
    data['insurance_product_batchs'] = insurance_product_batch_set
    insurance_product_ticket_set = InsuranceProducts.objects()
    # product_type='ticket'
    data['insurance_product_tickets'] = insurance_product_ticket_set

    if request.method == 'POST':
        request_tool.save_log()
        if request.POST['password'] != '':
            new_password = request.POST['password']
            DocumentTools.reset_password(new_password, driver.user)
        # name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        # if name != '':
        #     driver.name = name
        if phone != driver.profile.phone and DocumentTools.get_user(phone) is not None:
            data['message'] = '手机号已存在'
            return render_to_response('bms/user/driver_detail.html', data, context)

        insurance_product_car_id = request.POST.get('insurance_product_car_id', '')
        if insurance_product_car_id:
            insurance_product_car = InsuranceProducts.objects(id=insurance_product_car_id).first()
            if insurance_product_car:
                driver.product_car = insurance_product_car
            else:
                data['driver'] = driver
                data['message'] = '您选择的运单产品不存在'
                return render_to_response('bms/user/driver_detail.html', data, context)
        else:
            data['driver'] = driver
            data['message'] = '请选择默认的发送运单产品'
            return render_to_response('bms/user/driver_detail.html', data, context)

        insurance_product_batch_id = request.POST.get('insurance_product_batch_id', '')
        if insurance_product_batch_id:
            insurance_product_batch = InsuranceProducts.objects(id=insurance_product_batch_id).first()
            if insurance_product_batch:
                driver.product_batch = insurance_product_batch
            else:
                data['driver'] = driver
                data['message'] = '您选择的车次产品不存在'
                return render_to_response('bms/user/driver_detail.html', data, context)
        else:
            data['driver'] = driver
            data['message'] = '请选择默认的发送车次产品'
            return render_to_response('bms/user/driver_detail.html', data, context)

        insurance_product_ticket_id = request.POST.get('insurance_product_ticket_id', '')
        if insurance_product_ticket_id:
            insurance_product_ticket = InsuranceProducts.objects(id=insurance_product_ticket_id).first()
            if insurance_product_ticket:
                driver.product_ticket = insurance_product_ticket
            else:
                data['driver'] = driver
                data['message'] = '您选择的单票产品不存在'
                return render_to_response('bms/user/driver_detail.html', data, context)
        else:
            data['driver'] = driver
            data['message'] = '请选择默认的发送单票产品'
            return render_to_response('bms/user/driver_detail.html', data, context)
        if request.POST.get('active', '') == 'show':
            driver.user.is_active = True
        else:
            driver.user.is_active = False
        driver.profile.phone = phone
        driver.user.save()
        driver.save()
        return HttpResponseRedirect(reverse('bms:driver_list', args=[page_index, ]))
    return render_to_response('bms/user/driver_detail.html', data, context)


#－－－－－－－－－－－－－－－－－－－－－－－－－－货主－－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def boss_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_boss'] = search_keyword
        request.session['page_index_boss'] = 1
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:boss_list', args=[1, ]) + get_parameter)
    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_boss', '')
        boss_set = Client.objects(user_type='boss').filter(Q(name__contains=search_keyword) |
                                     Q(profile__phone__contains=search_keyword))
        state = request_tool.get_parameter("state", "active")
        if state == 'active':
            user_set = User.objects(is_active=True)
            boss_set = boss_set.filter(user__in=user_set)
        elif state == 'hidden':
            user_set = User.objects(is_active=False)
            boss_set = boss_set.filter(user__in=user_set)
        count = boss_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_boss'] = paging['page_index']
        boss_set = boss_set[paging['start_item']:paging['end_item']]
        data['bosss'] = boss_set
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/boss_list.html', data, context)

@login_required
@AdminRequired
def boss_detail(request, boss_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_boss', '1')
    data['page_index'] = page_index
    data['boss_id'] = boss_id
    insurance_product_car_set = InsuranceProducts.objects()
    # product_type='car'
    data['insurance_product_cars'] = insurance_product_car_set
    insurance_product_batch_set = InsuranceProducts.objects()
    # product_type='batch'
    data['insurance_product_batchs'] = insurance_product_batch_set
    insurance_product_ticket_set = InsuranceProducts.objects()
    # product_type='ticket'
    data['insurance_product_tickets'] = insurance_product_ticket_set
    boss = Client.objects(id=boss_id).first()
    
    message = request.session.get('code_message', '')
    data['message'] = message
    request.session['code_message'] = ''

    coupon_count = 0
    use_coupon_set = UseCoupon.objects(client=boss)
    if use_coupon_set:
        for use_coupon in use_coupon_set:
            if use_coupon.coupon.end_date > datetime.datetime.now():
                coupon_count += 1
    data['coupon_count'] = coupon_count
    data['use_coupons'] = use_coupon_set

    client = Client.objects(user=boss.referee).first()
    if client:
        data["client"] = client
    if boss:
        data['boss'] = boss
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:boss_list', args=[boss_id, page_index, ]))
    return render_to_response('bms/user/boss_detail.html', data, context)


@login_required
@AdminRequired
def boss_edit(request, boss_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_boss', '1')
    boss = Client.objects(id=boss_id).first()
    data['boss'] = boss
    data['page_index'] = page_index
    insurance_product_car_set = InsuranceProducts.objects()
    # product_type='car'
    data['insurance_product_cars'] = insurance_product_car_set
    insurance_product_batch_set = InsuranceProducts.objects()
    # product_type='batch'
    data['insurance_product_batchs'] = insurance_product_batch_set
    insurance_product_ticket_set = InsuranceProducts.objects()
    # product_type='ticket'
    data['insurance_product_tickets'] = insurance_product_ticket_set

    if request.method == 'POST':
        request_tool.save_log()
        if request.POST['password'] != '':
            new_password = request.POST['password']
            DocumentTools.reset_password(new_password, boss.user)
        # name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        # if name != '':
        #     boss.name = name
        if phone != boss.profile.phone and DocumentTools.get_user(phone) is not None:
            data['message'] = '手机号已存在'
            return render_to_response('bms/user/boss_detail.html', data, context)

        insurance_product_car_id = request.POST.get('insurance_product_car_id', '')
        if insurance_product_car_id:
            insurance_product_car = InsuranceProducts.objects(id=insurance_product_car_id).first()
            if insurance_product_car:
                boss.product_car = insurance_product_car
            else:
                data['boss'] = boss
                data['message'] = '您选择的运单产品不存在'
                return render_to_response('bms/user/boss_detail.html', data, context)
        else:
            data['boss'] = boss
            data['message'] = '请选择默认的发送运单产品'
            return render_to_response('bms/user/boss_detail.html', data, context)

        insurance_product_batch_id = request.POST.get('insurance_product_batch_id', '')
        if insurance_product_batch_id:
            insurance_product_batch = InsuranceProducts.objects(id=insurance_product_batch_id).first()
            if insurance_product_batch:
                boss.product_batch = insurance_product_batch
            else:
                data['boss'] = boss
                data['message'] = '您选择的车次产品不存在'
                return render_to_response('bms/user/boss_detail.html', data, context)
        else:
            data['boss'] = boss
            data['message'] = '请选择默认的发送车次产品'
            return render_to_response('bms/user/boss_detail.html', data, context)

        insurance_product_ticket_id = request.POST.get('insurance_product_ticket_id', '')
        if insurance_product_ticket_id:
            insurance_product_ticket = InsuranceProducts.objects(id=insurance_product_ticket_id).first()
            if insurance_product_ticket:
                boss.product_ticket = insurance_product_ticket
            else:
                data['boss'] = boss
                data['message'] = '您选择的单票产品不存在'
                return render_to_response('bms/user/boss_detail.html', data, context)
        else:
            data['boss'] = boss
            data['message'] = '请选择默认的发送单票产品'
            return render_to_response('bms/user/boss_detail.html', data, context)


        # registered.profile.nickname = nickname
        # client.user.last_name = nickname
        if request.POST.get('active', '') == 'show':
            boss.user.is_active = True
        else:
            boss.user.is_active = False
        boss.profile.phone = phone
        boss.user.save()
        boss.save()
        return HttpResponseRedirect(reverse('bms:boss_list', args=[page_index, ]))
    return render_to_response('bms/user/boss_detail.html', data, context)


#－－－－－－－－－－－－－－－－－－－－－－－－－－车主－－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def owner_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_owner'] = search_keyword
        request.session['page_index_owner'] = page_index
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:owner_list', args=[page_index, ]) + get_parameter)
    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_owner', '')
        owner_set = Client.objects(user_type='owner').filter(Q(name__contains=search_keyword) |
                                     Q(profile__phone__contains=search_keyword))
        state = request_tool.get_parameter("state", "active")
        if state == 'active':
            user_set = User.objects(is_active=True)
            owner_set = owner_set.filter(user__in=user_set)
        elif state == 'hidden':
            user_set = User.objects(is_active=False)
            owner_set = owner_set.filter(user__in=user_set)
        count = owner_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_owner'] = paging['page_index']
        owner_set = owner_set[paging['start_item']:paging['end_item']]
        data['owners'] = owner_set
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/owner_list.html', data, context)
    
    
    
    
    
@login_required
@AdminRequired
def owner_detail(request, owner_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_owner', '1')
    data['page_index'] = page_index
    data['owner_id'] = owner_id
    insurance_product_car_set = InsuranceProducts.objects(product_type='car')
    # product_type='car'
    data['insurance_product_cars'] = insurance_product_car_set
    insurance_product_batch_set = InsuranceProducts.objects(product_type='batch')
    # product_type='batch'
    data['insurance_product_batchs'] = insurance_product_batch_set
    insurance_product_ticket_set = InsuranceProducts.objects(product_type='ticket')
    # product_type='ticket'
    data['insurance_product_tickets'] = insurance_product_ticket_set
    owner = Client.objects(id=owner_id).first()
    
    message = request.session.get('code_message', '')
    data['message'] = message
    request.session['code_message'] = ''

    coupon_count = 0
    use_coupon_set = UseCoupon.objects(client=owner)
    if use_coupon_set:
        for use_coupon in use_coupon_set:
            if use_coupon.coupon.end_date > datetime.datetime.now():
                coupon_count += 1
    data['coupon_count'] = coupon_count
    data['use_coupons'] = use_coupon_set

    client = Client.objects(user=owner.referee).first()
    if client:
        data["client"] = client
    if owner:
        data['owner'] = owner
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:owner_list', args=[owner_id, page_index, ]))
    return render_to_response('bms/user/owner_detail.html', data, context)


@login_required
@AdminRequired
def owner_edit(request, owner_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_owner', '1')
    owner = Client.objects(id=owner_id).first()
    data['owner'] = owner
    data['page_index'] = page_index
    insurance_product_car_set = InsuranceProducts.objects()
    # product_type='car'
    data['insurance_product_cars'] = insurance_product_car_set
    insurance_product_batch_set = InsuranceProducts.objects()
    # product_type='batch'
    data['insurance_product_batchs'] = insurance_product_batch_set
    insurance_product_ticket_set = InsuranceProducts.objects()
    # product_type='ticket'
    data['insurance_product_tickets'] = insurance_product_ticket_set

    if request.method == 'POST':
        request_tool.save_log()
        if request.POST['password'] != '':
            new_password = request.POST['password']
            DocumentTools.reset_password(new_password, owner.user)
        phone = request.POST.get('phone', '')
        if phone != owner.profile.phone and DocumentTools.get_user(phone) is not None:
            data['message'] = '手机号已存在'
            return render_to_response('bms/user/owner_detail.html', data, context)

        insurance_product_car_id = request.POST.get('insurance_product_car_id', '')
        if insurance_product_car_id:
            insurance_product_car = InsuranceProducts.objects(id=insurance_product_car_id).first()
            if insurance_product_car:
                owner.product_car = insurance_product_car
            else:
                data['owner'] = owner
                data['message'] = '您选择的运单产品不存在'
                return render_to_response('bms/user/owner_detail.html', data, context)
        else:
            data['owner'] = owner
            data['message'] = '请选择默认的发送运单产品'
            return render_to_response('bms/user/owner_detail.html', data, context)

        insurance_product_batch_id = request.POST.get('insurance_product_batch_id', '')
        if insurance_product_batch_id:
            insurance_product_batch = InsuranceProducts.objects(id=insurance_product_batch_id).first()
            if insurance_product_batch:
                owner.product_batch = insurance_product_batch
            else:
                data['owner'] = owner
                data['message'] = '您选择的车次产品不存在'
                return render_to_response('bms/user/owner_detail.html', data, context)
        else:
            data['owner'] = owner
            data['message'] = '请选择默认的发送车次产品'
            return render_to_response('bms/user/owner_detail.html', data, context)

        insurance_product_ticket_id = request.POST.get('insurance_product_ticket_id', '')
        if insurance_product_ticket_id:
            insurance_product_ticket = InsuranceProducts.objects(id=insurance_product_ticket_id).first()
            if insurance_product_ticket:
                owner.product_ticket = insurance_product_ticket
            else:
                data['owner'] = owner
                data['message'] = '您选择的单票产品不存在'
                return render_to_response('bms/user/owner_detail.html', data, context)
        else:
            data['owner'] = owner
            data['message'] = '请选择默认的发送单票产品'
            return render_to_response('bms/user/owner_detail.html', data, context)


        # registered.profile.nickname = nickname
        # client.user.last_name = nickname
        if request.POST.get('active', '') == 'show':
            owner.user.is_active = True
        else:
            owner.user.is_active = False
        owner.profile.phone = phone
        owner.user.save()
        owner.save()
        return HttpResponseRedirect(reverse('bms:owner_list', args=[page_index, ]))
    return render_to_response('bms/user/owner_detail.html', data, context)

#－－－－－－－－－－－－－－－－－－－－－－－－－－理赔人员－－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def claim_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')

        request.session['search_keyword_claim'] = search_keyword
        request.session['page_index_claim'] = 1
        return HttpResponseRedirect(reverse('bms:claim_list', args=[1, ]))

    elif request.method == 'GET':
        message = request.session.get('message', '')
        request.session['message'] = ''
        search_keyword = request.session.get('search_keyword_claim', '')
        claims = Claim.objects().filter(profile__phone__contains=search_keyword)
        count = claims.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_claim'] = paging['page_index']
        claims = claims[paging['start_item']:paging['end_item']]
        data['claims'] = claims
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/claim_list.html', data, context)

@login_required
@AdminRequired
def claim_detail(request, claim_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_claim', '1')
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    data['page_index'] = page_index
    data['claim_id'] = claim_id
    company_set = InsuranceCompany.objects()
    data['companys'] = company_set
    claim = Claim.objects(id=claim_id).first()
    if claim:
        data['claim'] = claim
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:claim_list', args=[claim_id, page_index, ]))
    return render_to_response('bms/user/claim_detail.html', data, context)

@login_required
@AdminRequired
def claim_create(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_claim', '1')
    data['page_index'] = page_index
    company_set = InsuranceCompany.objects()
    data['companys'] = company_set
    if request.method == 'POST':
        request_tool.save_log()
        data['posted_data'] = request.POST
        # nickname = request.POST.get('nickname', '')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        company_id = request.POST.get('company_id', '')
        name = request.POST.get('name', '')
        re_password = request.POST.get('re_password', '')
        # user = DocumentTools.get_user(nickname)
        # if user is not None:
        #     data['message'] = '用户昵称已存在'
        #     return render_to_response('bms/user/claim_create.html', data, context)
        user = DocumentTools.get_user(phone)
        if user is not None:
            data['message'] = '手机号已存在'
            return render_to_response('bms/user/claim_create.html', data, context)
        count=0
        try:
            count=Claim.objects(profile__phone=phone).count()
        except:
            count=0
        if count>0:
            data['message'] = '手机号已存在。'
            return render_to_response('bms/user/claim_create.html', data, context)

        if password == '':
            data['message'] = '密码不能为空。'
            return render_to_response('bms/user/claim_create.html', data, context)
            
        if re_password == '':
            data['message'] = '确认密码不能为空。'
            return render_to_response('bms/user/claim_create.html', data, context)
        if len(password)>20:
            data['message'] = '密码长度不能超过20个字符。'
            return render_to_response('bms/user/claim_create.html', data, context)
        if password != re_password:
            data['message'] = '两次密码不一致。'
            return render_to_response('bms/user/claim_create.html', data, context)
        username = DocumentTools.get_username()
        password = hashlib.sha1(password.encode('utf-8')).hexdigest()
        user = User(username=username, password=make_password(password))
        user.first_name = 'claim'
        if request.POST.get('active', '') == 'show':
            user.is_active = True
        else:
            user.is_active = False
        user.save()

        profile = UserProfile(phone=phone, user_id=user.id)
        claim = Claim(user=user, profile=profile)
        claim.name = name
        if company_id:
            company = InsuranceCompany.objects(id=company_id).first()
            if company:
                claim.company = company
            else:
                data['message'] = '网络不稳定，未找到对应保险公司，请稍后再试'
                return render_to_response('bms/user/claim_create.html', data, context)
        else:
            data['message'] = '请选择保险公司'
            return render_to_response('bms/user/claim_create.html', data, context)

        claim.save()
        return HttpResponseRedirect(reverse('bms:claim_list', args=[page_index, ]))

    if request.method == 'GET':
        data['page_index'] = page_index
        return render_to_response('bms/user/claim_create.html', data, context)



@login_required
@AdminRequired
def claim_edit(request, claim_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_claim', '1')
    claim = Claim.objects(id=claim_id).first()
    if not claim:
        request.session['message'] = '未找到对应的理赔人员'
        return HttpResponseRedirect(reverse('bms:claim_detail', args=[claim.id, ]))
    data['claim'] = claim
    data['page_index'] = page_index
    data['claim_id'] = claim_id
    company_set = InsuranceCompany.objects()
    data['companys'] = company_set

    if request.method == 'POST':
        request_tool.save_log()
        if request.POST['password'] != '':
            new_password = request.POST['password']
            re_password = request.POST['re_password']
            if new_password =="" or re_password=="" :
                data['message'] = '密码或再次输入密码都不能为空'
                return render_to_response('bms/user/claim_detail.html', data, context)
            if len(new_password)>20:
                data['message'] = '密码最多输入20个字符'
                return render_to_response('bms/user/claim_detail.html', data, context)
            if new_password != re_password:
                data['message'] = '两次输入密码不一致'
                return render_to_response('bms/user/claim_detail.html', data, context)
            DocumentTools.reset_password(new_password, claim.user)
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        company_id = request.POST.get('company_id', '')
        if name != '':
            claim.name = name
        count=0
        try:
            count=Claim.objects(profile__phone=phone).count()
        except:
            count=0
#        if phone != claim.profile.phone and DocumentTools.get_user(phone) is not None:

        if phone != claim.profile.phone and DocumentTools.get_user(phone) is not None :
            data['message'] = '手机号已存在'
            return render_to_response('bms/user/claim_detail.html', data, context)
        if phone != claim.profile.phone  and count>=1:
            data['message'] = '手机号已存在。'
            return render_to_response('bms/user/claim_detail.html', data, context)
        if count>=2:
            data['message'] = '手机号已存在,请检查后重新输入。'
            return render_to_response('bms/user/claim_detail.html', data, context)
        # registered.profile.nickname = nickname
        # client.user.last_name = nickname
        if request.POST.get('active', '') == 'show':
            claim.user.is_active = True
        else:
            claim.user.is_active = False
        claim.profile.phone = phone
        company = InsuranceCompany.objects(id=company_id).first()
        if company:
            claim.company = company
        else:
            data['message'] = '保险公司不存在'
            raise render_to_response('bms/user/claim_create.html', data, context)
        claim.user.save()
        claim.save()
        return HttpResponseRedirect(reverse('bms:claim_list', args=[page_index, ]))
    return render_to_response('bms/user/claim_detail.html', data, context)

#－－－－－－－－－－－－－－－－－－－－－－－－－－律师－－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def lawyer_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')

        request.session['search_keyword_lawyer'] = search_keyword
        request.session['page_index_lawyer'] = 1
        return HttpResponseRedirect(reverse('bms:lawyer_list', args=[page_index, ]))

    elif request.method == 'GET':
        message = request.session.get('message', '')
        request.session['message'] = ''
        search_keyword = request.session.get('search_keyword_lawyer', '')
        lawyer_set = Lawyer.objects()
        lawyer_set = request_tool.lawyer_filter(campaign_lawyer_set=lawyer_set, keyword=search_keyword)
        count = lawyer_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_lawyer'] = paging['page_index']
        lawyer_set = lawyer_set[paging['start_item']:paging['end_item']]
        data['lawyers'] = lawyer_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/lawyer_list.html', data, context)

@login_required
@AdminRequired
def lawyer_detail(request, lawyer_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_lawyer', '1')
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    data['page_index'] = page_index
    data['lawyer_id'] = lawyer_id
    lawyer = Lawyer.objects(id=lawyer_id).first()
    if lawyer:
        data['lawyer'] = lawyer
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:lawyer_list', args=[lawyer_id, page_index, ]))
    return render_to_response('bms/user/lawyer_detail.html', data, context)

@login_required
@AdminRequired
def lawyer_create(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_lawyer', '1')
    data['page_index'] = page_index
    if request.method == 'POST':
        request_tool.save_log()
        data['posted_data'] = request.POST
        # nickname = request.POST.get('nickname', '')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        re_password = request.POST.get('re_password', '')
        name = request.POST.get('name', '')
        if len(name)>16:
            data['message'] = '律师姓名输入过长，最多输入16位字符‘'
            return render_to_response('bms/user/lawyer_create.html', data, context)
        # user = DocumentTools.get_user(nickname)
        # if user is not None:
        #     data['message'] = '用户昵称已存在'
        #     return render_to_response('bms/user/lawyer_create.html', data, context)
        user = DocumentTools.get_user(phone)
        if user is not None:
            data['message'] = '手机号已存在'
            return render_to_response('bms/user/lawyer_create.html', data, context)

        if password == '':
            return render_to_response('bms/user/lawyer_create.html',
                                      {'posted_data': request.POST, 'message': '密码不能为空',
                                       'page_index': request.session.get('page_index_lawyer', '1')}, context)
        if re_password == "":
            data['message'] = '确认密码不能为空‘'
            return render_to_response('bms/user/lawyer_create.html', data, context)
        if len(password) >20:
            data['message'] = '密码长度过长，密码最多输入20个字符‘'
            return render_to_response('bms/user/lawyer_create.html', data, context)
        if re_password != password:
            data['message'] = '两次输入密码不一致‘'
            return render_to_response('bms/user/lawyer_create.html', data, context)
        username = DocumentTools.get_username()
        password = hashlib.sha1(password.encode('utf-8')).hexdigest()
        user = User(username=username, password=make_password(password))
        if request.POST.get('active', '') == 'show':
            user.is_active = True
        else:
            user.is_active = False
        user.save()

        profile = UserProfile(phone=phone, user_id=user.id)
        lawyer = Lawyer(user=user, profile=profile)
        lawyer.name = name
        lawyer.save()
        return HttpResponseRedirect(reverse('bms:lawyer_list', args=[page_index, ]))

    if request.method == 'GET':
        data['page_index'] = page_index
        return render_to_response('bms/user/lawyer_create.html', data, context)



@login_required
@AdminRequired
def lawyer_edit(request, lawyer_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_lawyer', '1')
    lawyer = Lawyer.objects(id=lawyer_id).first()
    if not lawyer:
        return HttpResponseRedirect(reverse('bms:lawyer_detail', args=[lawyer.id, ]))
    data['lawyer'] = lawyer
    data['page_index'] = page_index

    if request.method == 'POST':
        request_tool.save_log()
        if request.POST['password'] != '':
            new_password = request.POST['password']
            re_password = request.POST['re_password']
            if re_password == "":
                data['message'] = '手机号已存在'
                return render_to_response('bms/user/lawyer_detail.html', data, context)
            if len(new_password) >20:
                data['message'] = '密码最多输入20个字符'
                return render_to_response('bms/user/lawyer_detail.html', data, context)
            if new_password != re_password:
                data['message'] = '两次输入密码不一致'
                return render_to_response('bms/user/lawyer_detail.html', data, context)
            DocumentTools.reset_password(new_password, lawyer.user)
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        if name != '':
            lawyer.name = name
        if phone != lawyer.profile.phone and DocumentTools.get_user(phone) is not None:
            data['message'] = '手机号已存在'
            return render_to_response('bms/user/lawyer_detail.html', data, context)
        # registered.profile.nickname = nickname
        # client.user.last_name = nickname
        if request.POST.get('active', '') == 'show':
            lawyer.user.is_active = True
        else:
            lawyer.user.is_active = False
        lawyer.profile.phone = phone
        lawyer.user.save()
        lawyer.save()
        return HttpResponseRedirect(reverse('bms:lawyer_list', args=[page_index, ]))
    return render_to_response('bms/user/lawyer_detail.html', data, context)




#－－－－－－－－－－－－－－－－－－－－－－－－－－预存保费－－－－－－－－－－－－－－－－－－－－－－－－－－

#列表
@login_required
@AdminRequired
def balance_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')

        request.session['search_keyword_balance'] = search_keyword
        request.session['page_index_balance'] = 1
        state = request_tool.get_parameter("certification_goal")
        get_parameter = "?certification_goal={0}".format(state)
        return HttpResponseRedirect(reverse('bms:balance_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_balance', '')
        request.session['search_keyword_balance'] = ''
        #2017修改用户流程
        user_set = User.objects(is_active=True)
        client_set = Client.objects().filter(user__in=user_set)
        count1=client_set.count()
        balance_set=client_set
        #balance_set = Client.objects().filter(user_type__ne='registered')
        balance_set = request_tool.balance_filter(balance_set=balance_set, keyword=search_keyword)

        count = balance_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_balance'] = paging['page_index']
        balance_set = balance_set[paging['start_item']:paging['end_item']]
        data['balances'] = balance_set
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/balance_list.html', data, context)


 
   #预存保费
@login_required
@AdminRequired
@ExceptionRequired
def deposit(request):
    context = RequestContext(request)
    data = {}
    if request.method == 'POST':
        request_tools = RequestTools(request)
        id_client = request_tools.get_parameter('id_client', '')
        deposit_client = request_tools.get_parameter('deposit_client', '')
        if id_client:
            client = Client.objects(id=id_client).first()
            if client:
                if deposit_client:
                    try:
                        deposit_client1= float(deposit_client)*100
                        deposit_client2 = int(deposit_client1)
                    except:
                        return JsonResult(code=CODE_INVALID_ACCESS, message="存款金额应输入最多有两位小数的数字").response()
#                     if deposit_client1<0:
#                         return JsonResult(code=CODE_INVALID_ACCESS, message="存款金额不能为负数").response()
                    if deposit_client2<deposit_client1:
                        return JsonResult(code=CODE_INVALID_ACCESS, message="存款金额最多输入两位小数").response()
                    try:
                        deposit_client = round(float(deposit_client) * 100)
                        if isinstance(client.balance, int):
                            client.balance += deposit_client
                        else:
                            client.balance = deposit_client
                        data['deposit_client'] = client.balance
                        data['id_client'] = id_client
                        client.save()
                    except Exception:
                        return JsonResult(code=CODE_INVALID_ACCESS, message="存款金额异常").response()
                else:
                    return JsonResult(code=CODE_INVALID_ACCESS, message="存款金额不能为空").response()
            else:
                return JsonResult(code=CODE_INVALID_ACCESS, message="用户不存在").response()
        else:
            return JsonResult(code=CODE_INVALID_ACCESS, message="用户不存在").response()
        #预存成功通知信息
        import datetime
        import time
        nowtime = datetime.datetime.now()
        subtime = nowtime.strftime("%Y-%m-%d %H:%M:%S")
        phone =  client .profile.phone
        username = client.name
        depositstatistical = DepositStatistical()
        depositstatistical.balance = client.balance#当前余额
        depositstatistical.client = client#关联用户
        depositstatistical.amount = deposit_client#本次操作金额
        depositstatistical.create_time = subtime
        depositstatistical.save()
        
#         transaction = Transaction()
#         transaction.client = client
#         transaction.amount = deposit_client/100
#         transaction.create_time = subtime
#         transaction.save()
        
        
        if int(client.balance/100)  >= 500:
               content = "您预存金额:"+str(deposit_client/100)+"已经成功预存!"+"预存余额已调整为:"+str(client.balance/100)+"元，如果有疑问请联系运之宝客服15910731816。"
               ad_content = "手机"+str(phone)+"/姓名（"+str(username)+"）的用户于："+str(subtime)+"预存金额"+str(deposit_client/100)+"元。"
        else:
                content = "您预存金额:"+str(deposit_client/100)+"已经成功预存!"+"预存余额已调整为:"+str(client.balance/100)+"元，预存余额低于500，为了避免余额不足导致无法提交订单，请尽快补充预存，如果有疑问请联系运之宝客服15910731816。"
                ad_content = "手机"+str(phone)+"/姓名（"+str(username)+"）的用户于："+str(subtime)+"预存金额"+str(deposit_client/100)+"元。预存余额为："+str(client.balance/100)+"元，余额不足500，请联系客户继续缴存。"
        try:
            touser = client.wx_id
            send_wx_message(touser,content)
            
            string_tools = tools_string.StringTools()
            ad_touser = string_tools.get_string("administrator_wx_id")
            send_wx_message(ad_touser,ad_content)
        except:
            return JsonResult(code=CODE_SUCCESS, data=data, message="存款成功,但微信发送失败，此用户可能未登陆公众号").response()
        
        
        return JsonResult(code=CODE_SUCCESS, data=data, message="存款成功").response()
    else:
        return JsonResult(code=CODE_INVALID_ACCESS).response()


#后台预存统计
@login_required
@AdminRequired
def deposit_statistical(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')

        request.session['search_keyword_balance'] = search_keyword
        request.session['page_index_balance'] = 1
        state = request_tool.get_parameter("certification_goal")
        get_parameter = "?certification_goal={0}".format(state)
        return HttpResponseRedirect(reverse('bms:deposit_statistical', args=[1, ]) + get_parameter)

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_balance', '')
        request.session['search_keyword_balance'] = ''

        balance_set = DepositStatistical.objects()
        balance_set = request_tool.deposit_statistical_filter(balance_set=balance_set, keyword=search_keyword)
        if search_keyword:
            count = len(balance_set)
        else:
            count = balance_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_balance'] = paging['page_index']
        balance_set = balance_set[paging['start_item']:paging['end_item']]
        data['balances'] = balance_set
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/deposit_statistical.html', data, context)
    
    
#第三方支付预存统计
@login_required
@AdminRequired
def wx_deposit_statistical(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')

        request.session['search_keyword_balance'] = search_keyword
        request.session['page_index_balance'] = 1
        state = request_tool.get_parameter("certification_goal")
        get_parameter = "?certification_goal={0}".format(state)
        return HttpResponseRedirect(reverse('bms:wx_deposit_statistical', args=[1, ]) + get_parameter)

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_balance', '')

        balance_set = Transaction.objects()
        balance_set = request_tool.transaction_filter(balance_set=balance_set, keyword=search_keyword)
        count = balance_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_balance'] = paging['page_index']
        balance_set = balance_set[paging['start_item']:paging['end_item']]
        data['balances'] = balance_set
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/wx_deposit_statistical.html', data, context)



#－－－－－－－－－－－－－－－－－－－－－－－－－－中介人员－－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def intermediary_people_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')

        request.session['search_keyword_claim'] = search_keyword
        request.session['page_index_claim'] = 1
        return HttpResponseRedirect(reverse('bms:intermediary_people_list', args=[1, ]))

    elif request.method == 'GET':
        message = request.session.get('message', '')
        request.session['message'] = ''
        search_keyword = request.session.get('search_keyword_claim', '')
        intermediarys = IntermediaryPeople.objects().filter(profile__phone__contains=search_keyword)
        #intermediarys = IntermediaryPeople.objects()
        count = intermediarys.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_claim'] = paging['page_index']
        intermediary_people_lists = intermediarys[paging['start_item']:paging['end_item']]
        data['intermediary_people_lists'] = intermediary_people_lists
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/intermediary_people_list.html', data, context)


@login_required
@AdminRequired
def intermediary_people_create(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_intermediary_people', '1')
    data['page_index'] = page_index
#     intermediary_set = Intermediary.objects().filter(state=True)#保险中介
#     data['intermediary_set'] = intermediary_set
    if request.method == 'POST':
        request_tool.save_log()
        data['posted_data'] = request.POST
        request.session['request_post_data'] = request.POST
        # nickname = request.POST.get('nickname', '')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        intermediary_id = request.POST.get('intermediary_id', '')
        name = request.POST.get('name', '')
        re_password = request.POST.get('re_password', '')
        user = DocumentTools.get_user(phone)
        #验证是否获取了中介渠道信息
        if intermediary_id:
            intermediary_set1 = Intermediary.objects(id=intermediary_id).first()
            if  not intermediary_set1:
                request.session['message'] = '网络不稳定，未找到对应保险中介，请稍后再试'
                return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        else:
            request.session['message'] = '请选择保险中介'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        #验证手机号格式
        if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', phone):
            request.session['message'] = '请输入正确的手机号码'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        if user is not None:
            request.session['message'] = '手机号已存在'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        count=0
        #检查手机号是否和理赔人员冲突
        try:
            count=Claim.objects(profile__phone=phone).count()
        except:
            count=0
        if count>0:
            request.session['message'] = '您输入的手机号已存在'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        #检查手机号是否和已有保险中介人员冲突
        try:
            count=IntermediaryPeople.objects(profile__phone=phone).count()
        except:
            count=0
        if count>0:
            request.session['message'] = '您输入的手机号已存在，请检查后重新输入或联系管理员修改手机号归属。'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))

        if password == '':
            request.session['message'] = '密码不能为空'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
            
        if re_password == '':
            request.session['message'] = '确认密码不能为空'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        if len(password)>20:
            request.session['message'] = '密码长度不能超过20个字符'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        if password != re_password:
            request.session['message'] = '两次密码不一致'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        username = DocumentTools.get_username()
        password = hashlib.sha1(password.encode('utf-8')).hexdigest()
        user = User(username=username, password=make_password(password))
        user.first_name = 'intermediary'
        if request.POST.get('active', '') == 'show':
            user.is_active = True
        else:
            user.is_active = False
        test_message=''
        if request.POST.get('active', '') == 'show' and intermediary_set1.state != True:
            user.is_active = False
            test_message='，由于当前中介渠道未激活，所以中介人员不能设置为激活状态。'
            
        user.save()

        profile = UserProfile(phone=phone, user_id=user.id)
        intermediary_people = IntermediaryPeople(user=user, profile=profile)
        intermediary_people.name = name
        intermediary_people.intermediary = intermediary_set1
        intermediary_people.save()
        request.session['request_post_data'] =''
        request.session['message'] = '创建中介人员成功' + test_message
        return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
#         return HttpResponseRedirect(reverse('bms:intermediary_people_list', args=[page_index, ]))

    if request.method == 'GET':
        data['page_index'] = page_index
        return HttpResponseRedirect(reverse('bms:intermediary_list', args=[page_index, ]))
    
    
    
    
   #中介人员详情已经弃用 
@login_required
@AdminRequired
def intermediary_people_detail(request, intermediary_people_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_claim', '1')
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    data['page_index'] = page_index
    data['intermediary_people_id'] = intermediary_people_id
    intermediary_set = Intermediary.objects().filter(state=True)#保险中介
    data['intermediary_set'] = intermediary_set
    intermediary_people = IntermediaryPeople.objects(id=intermediary_people_id).first()
    if intermediary_people:
        data['intermediary_people'] = intermediary_people
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:intermediary_people_list', args=[ page_index, ]))
    return render_to_response('bms/user/intermediary_people_detail.html', data, context)

#修改中介人员信息
@login_required
@AdminRequired
def intermediary_people_edit(request, intermediary_people_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_claim', '1')
    intermediary_people = IntermediaryPeople.objects(id=intermediary_people_id).first()
    if not intermediary_people:
        request.session['message'] = '未找到对应的中介人员'
        return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
    data['intermediary_people'] = intermediary_people
    data['page_index'] = page_index
    data['intermediary_people_id'] = intermediary_people_id
#     intermediary_set = Intermediary.objects().filter(state=True)#保险中介
#     data['intermediary_set'] = intermediary_set

    if request.method == 'POST':
        request_tool.save_log()
        if request.POST['password'] != '':
            new_password = request.POST['password']
            re_password = request.POST['re_password']
            if new_password =="" or re_password=="" :
                request.session['message'] = '密码或再次输入密码都不能为空'
                return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
            if len(new_password)>20:
                request.session['message'] = '密码最多输入20个字符'
                return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
            if new_password != re_password:
                request.session['message'] = '两次输入密码不一致'
                return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
            DocumentTools.reset_password(new_password, intermediary_people.user)
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        intermediary_id = request.POST.get('intermediary_id', '')
        if name != '':
            intermediary_people.name = name
         #验证手机号格式
        if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', phone):
            request.session['message'] = '请输入正确的手机号码'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        
        #检查是否是理赔人员
        count=0
        try:
            count=Claim.objects(profile__phone=phone).count()
            if count >0:
                request.session['message'] = '手机号与理赔人员冲突，请联系管理员，确认手机号归属'
                return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        except:
            count=0
        #检查手机号是否和已有保险中介人员冲突
        try:
            count=IntermediaryPeople.objects(profile__phone=phone).count()
        except:
            count=0
        if phone != intermediary_people.profile.phone and DocumentTools.get_user(phone) is not None :
            request.session['message'] = '手机号已存在'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        if phone != intermediary_people.profile.phone  and count>=1:
            request.session['message'] = '手机号已存在。'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        if count>=2:
            request.session['message'] = '手机号已存在,请检查后重新输入。'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        if request.POST.get('active', '') == 'show':
            intermediary_people.user.is_active = True
        else:
            intermediary_people.user.is_active = False
        test_message=''
        if request.POST.get('active', '') == 'show' and intermediary_people.intermediary.state != True:
            intermediary_people.user.is_active = False
            test_message='，由于当前中介渠道未激活，所以中介人员不能设置为激活状态。'
        intermediary_people.profile.phone = phone
        
        if intermediary_id:
            intermediary_set = Intermediary.objects(id=intermediary_id).first()
            if intermediary_set:
                intermediary_people.intermediary = intermediary_set
            else:
                request.session['message'] = '网络不稳定，未找到对应保险中介，请稍后再试'
                return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        else:
            request.session['message'] = '请选择保险中介'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
        
        intermediary_people.user.save()
        intermediary_people.save()
        request.session['message'] = '修改成功' +test_message
        return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary_id, ]))
    return HttpResponseRedirect(reverse('bms:intermediary_list', args=[1, ]))
#     return render_to_response('bms/user/intermediary_people_detail.html', data, context)


#创建二维码图片
@login_required
@AdminRequired
def create_code_pic(request,client_id):
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
    except Exception as e:
        message=str(e)
        return'保存路径失败，请稍后点击更新二维码'

#生成二维码图片
@login_required
@AdminRequired
def build_code_pic(request, client_id):
    context = RequestContext(request)
    data = {}
    if request.method == 'POST':
        user_type = request.POST.get('user_type', '')
    else:
        user_type = request.GET.get('user_type', '')
    #根据用户身份区分返回页面
    if user_type == 'transport':
        return_bug ='bms:transport_list'
        return_page ='bms:transport_detail'
    elif user_type == 'driver':
        return_bug ='bms:driver_list'
        return_page ='bms:driver_detail'
    elif user_type == 'boss':
        return_bug ='bms:boss_list'
        return_page ='bms:boss_detail'
    elif user_type == 'owner':
        return_bug ='bms:owner_list'
        return_page ='bms:owner_detail'
    elif user_type == 'registered':
        return_bug ='bms:registered_list'
        return_page ='bms:registered_detail'
    else:
        return_bug ='bms:transport_list'
        return_page ='bms:transport_detail'
    #根据用户身份区分返回页面结束
    try:
        request.session['code_message'] = '生成二维码部分'
        client = Client.objects(id=client_id).first()
        #return HttpResponseRedirect(reverse('bms:transport_detail', args=[client_id ]))
    except:
        request.session['code_message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse(return_bug, args=[1 ]))
    try:
        create_code = create_code_pic(request, client_id)
        if create_code != 'success':
            request.session['code_message'] = str(create_code)
            return HttpResponseRedirect(reverse(return_bug, args=[1 ]))
    except:
        request.session['code_message'] = '网络不稳定，生成二维码失败'
        return HttpResponseRedirect(reverse(return_bug, args=[1 ]))

    return HttpResponseRedirect(reverse(return_page, args=[client_id ]))
    


#补充用户信息
@login_required
@AdminRequired
def add_user_information(request, registered_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_certificate', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    request_tool = RequestTools(request)
    data['user_types'] = Client.USER_TYPE
    try:
        registered = Client.objects(id=registered_id).first()
    except:
        request_tool.set_message('没有找到对应的注册用户.')
        return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
    if not registered:
        request_tool.set_message('没有找到对应的注册用户。')
        return HttpResponseRedirect(reverse('bms:registered_list', args=['1', ]))
    
    count = Certificate.objects(client=registered).count()
#     if count > 1:
#         request_tool.set_message('用户不能二次认证')
#         return HttpResponseRedirect(reverse('bms:registered_list', args=['1', ]))
    if request.method == 'POST':
        request.session['posted_data'] = request.POST
        try:
            if count > 0:
                certificate = Certificate.objects(client=registered).first()
            else:
                certificate = Certificate()
            certificate = bms_tools.validation_certificate_new(certificate)
            certificate.client = registered
            certificate.save()
            request.session['message'] = '补充信息成功请查看'
#             return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))
        except CustomError as e:
            request.session['message']  = e.message
            return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))
        except Exception as e:
            print(traceback.format_exc())
            request.session['message']  = str(e)
            return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))
        try:
            certificate.verify()
            request.session['message'] = '补充信息同步成功请查看'
        except Exception as e:
            message= str(e)
            print(traceback.format_exc())
            request.session['message']  = str(e)
            return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))
        return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))
        #return render_to_response('bms/user/certificate_create.html', data, context)
    elif request.method == 'GET':
        return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))


#补充用户局部信息
@login_required
@AdminRequired
def improve_part_information(request, registered_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_certificate', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    request_tool = RequestTools(request)
    data['user_types'] = Client.USER_TYPE
    try:
        registered = Client.objects(id=registered_id).first()
    except:
        request_tool.set_message('没有找到对应的注册用户.')
        return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
    if not registered:
        request_tool.set_message('没有找到对应的注册用户。')
        return HttpResponseRedirect(reverse('bms:registered_list', args=['1', ]))
    
    count = Certificate.objects(client=registered).count()
    if request.method == 'POST':
        request.session['posted_data'] = request.POST
        try:
            if count > 0:
                certificate = Certificate.objects(client=registered).first()
            else:
                certificate = Certificate()
            certificate = bms_tools.validation_part_imformation(certificate)
            certificate.save()
            request.session['message'] = '补充信息成功请查看'
#             return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))
        except CustomError as e:
            request.session['message']  = e.message
            return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))
        except Exception as e:
            print(traceback.format_exc())
            request.session['message'] = str(e)
            return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))
        try:
            certificate.verify()
            request.session['message'] = '补充信息同步成功请查看'
        except Exception as e:
            message= str(e)
            request.session['message']  = str(e)
            return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))
        return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))
        #return render_to_response('bms/user/certificate_create.html', data, context)
    elif request.method == 'GET':
        return HttpResponseRedirect(reverse('bms:registered_detail', args=[registered.id, ]))
#修改用户密码
@login_required
@AdminRequired
def change_user_password(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_registered', '1')
    data['page_index'] = page_index

    if request.method == 'POST':
        request_tool.save_log()     #保存日志
        registered_id = request.POST['registered_id']
        try:
            registered = Client.objects(id=registered_id).first()
            if Client.objects(id=registered_id).count()==0:
                request.session['password_message']=str(registered.profile.phone)+'网络不稳定，未获取到修改密码参数.'
                return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        except:
            request.session['password_message']=str(registered.profile.phone)+'网络不稳定，未获取到修改密码参数'
            return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        if request.POST['password'] != '':
            new_password = request.POST['password']
            re_password = request.POST['re_password']
            if re_password =="":
                request.session['password_message']= str(registered.profile.phone)+'确认密码未输入'
                return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
            if len(new_password) > 20:
                request.session['password_message']=str(registered.profile.phone)+ '密码最多20字'
                return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
            if re_password != new_password:
                request.session['password_message']= str(registered.profile.phone)+'两次密码不一致，请检查后重新输入'
                return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
            DocumentTools.reset_password(new_password, registered.user)
        else:
            request.session['password_message']=str(registered.profile.phone)+ '修改密码不能为空'
            return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        try:
            registered.user.save()
            registered.save()
        except Exception as e:
            message=str(e)
            request.session['password_message']= '网络延迟'+message+str(registered.profile.phone)+'修改密码失败，请稍后 再试'
            return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        request.session['password_message']='用户'+str(registered.profile.phone)+'：修改密码成功'
        return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
    else:
        return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
    
    
    #修改用户状态
@login_required
@AdminRequired
def change_user_type(request,registered_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_registered', '1')
    data['page_index'] = page_index

    if request.method == 'GET':
        request_tool.save_log()     #保存日志
#         registered_id = request.POST['registered_id']
        try:
            registered = Client.objects(id=registered_id).first()
            if Client.objects(id=registered_id).count()==0:
                request.session['password_message']='网络不稳定，未获取到用户信息.'
                return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        except:
            request.session['password_message']='网络不稳定，未获取到用户信息'
            return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        type = request.GET.get('type', '')
        if request.GET.get('type', '') == 'fail':
            registered.user.is_active = False
        else:
            registered.user.is_active = True
        try:
            registered.user.save()
            registered.save()
        except Exception as e:
            message=str(e)
            request.session['password_message']= '网络延迟'+message+'修改用户状态失败，请稍后 再试'
            return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        request.session['password_message']='用户'+str(registered.profile.phone)+'：修改用户状态成功'
        return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
    else:
        return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
    
    
    
#后台支付统计
@login_required
@AdminRequired
def payment_statistical(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_payment'] = search_keyword
        return HttpResponseRedirect(reverse('bms:payment_statistical', args=[page_index, ]) )
#         state = request_tool.get_parameter("certification_goal")
#         get_parameter = "?certification_goal={0}".format(state)
#         return HttpResponseRedirect(reverse('bms:deposit_statistical', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_payment', '')
        request.session['search_keyword_payment'] = ''
        payment_list1 = PaymentStatistical.objects()
#         count = payment_list.count()
        if search_keyword:
            test_list=[]
            for payment_detail in payment_list1:
                if search_keyword in payment_detail.client.profile.phone:
                    test_list.append(payment_detail)
            count=len(test_list)
            payment_list = test_list
        else:
            payment_list =PaymentStatistical.objects()
            count = payment_list.count()
                    
        #balance_set = request_tool.deposit_statistical_filter(balance_set=balance_set, keyword=search_keyword)
        #count = payment_list.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        payment_list = payment_list[paging['start_item']:paging['end_item']]
        data['payment_list'] = payment_list
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/payment_statistical.html', data, context)
    
   #导出付款信息 
@login_required
@AdminRequired
def payment_export(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('bms:payment_statistical', args=[1, ]) )
        search_keyword = request.POST.get('search_keyword', '')
        
    try:
        search_keyword = request.POST.get('search_keyword', '')
#         product_set = PaymentStatistical.objects().filter(Q(name__contains=keyword))
        
        payment_list1 = PaymentStatistical.objects()
        if search_keyword:
            test_list=[]
            for payment_detail in payment_list1:
                if search_keyword in payment_detail.client.profile.phone:
                    test_list.append(payment_detail)
            count=len(test_list)
            payment_list = test_list
        else:
            payment_list =PaymentStatistical.objects()
            count = payment_list.count()
        if count == 0:
            request.session['message'] = '没有筛选出对应订单，请选择订单后导出文件'
            return HttpResponseRedirect(reverse('bms:payment_statistical', args=[1, ]) )

        if payment_list:
            export_tools = ExcelExportTools()
            file_url = export_tools.export1(payment_list, PaymentStatistical.INSURANCE_FIELD_TUPLE1)
            print(file_url)
            url = static('/static/'+file_url)
            # request_tool.set_message('导出成功')
            return HttpResponseRedirect(url)
        else:
            request_tool.set_message('没有找到要导入的订单')
            return HttpResponseRedirect(reverse('bms:payment_statistical', args=[1, ]) )
    except CustomError as e:
        request_tool.set_message(e.message)
    except Exception as e:
        print(traceback.format_exc())
        request_tool.set_message(str(e))
    return HttpResponseRedirect(reverse('bms:payment_statistical', args=[1, ]) )

#修改用户基本信息
@login_required
@AdminRequired
def change_user_imformation(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_registered', '1')
    data['page_index'] = page_index

    if request.method == 'POST':
        request_tool.save_log()     #保存日志
        registered_id = request.POST['edit_user_id']
        try:
            registered = Client.objects(id=registered_id).first()
            if Client.objects(id=registered_id).count()==0:
                request.session['password_message']='网络不稳定，未获取到用户信息.'
                return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        except:
            request.session['password_message']='网络不稳定，未获取到用户信息'
            return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        #修改用户手机号
        phone = request.POST.get('user_phone', '')
        if phone != registered.profile.phone and DocumentTools.get_user(phone) is not None:
            request.session['password_message']= '手机号已存在'
            return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        
        #修改推荐人
        referee_phone=request.POST.get('referee_phone')
        referee_phone=referee_phone or None
        if referee_phone is None:
            registered.referee =referee_phone
        elif referee_phone==registered.profile.phone:
            request.session['password_message']='用户'+str(registered.profile.phone)+'推荐人不可填写本人手机号'
            return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        elif DocumentTools.get_user(referee_phone) is None:
            request.session['password_message']= '用户'+str(registered.profile.phone)+'推荐人不存在，请检查您所填写的号码'
            return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
        else:
            referee_user=Client.objects(profile__phone=referee_phone).first()
            registered.referee = referee_user.user
        registered.profile.phone = phone
        registered.user.save()
        registered.save()
    
        request.session['password_message']='用户'+str(registered.profile.phone)+'：修改用户信息成功'
        return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))
    else:
        return HttpResponseRedirect(reverse('bms:registered_list', args=[page_index, ]))