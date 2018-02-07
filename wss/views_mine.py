from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from wss.tools import *
#js_ticket
from wss.views_ticket import *
from common.models import *
from common.decorators import ExceptionRequired
from common.decorators import AdminRequired
from wss.tools_wechat import OpenidViewRequired
from django.contrib.auth.decorators import login_required

import time
import pingpp
import json

from wss.views_sendmessage import  send_wx_message
from common import tools_string
from requests.api import request
from common.driver_dict import *
from wss.tools import DocumentWssTools
from common.tools_legoo import *
import datetime
#二维码
import qrcode
#2017/06/09测试汇聚宝传值
from bms.views_order import order_pass_test
#2017/12/08分页
from common.tools import  PageTools
#登陆
def land(request):
    context = RequestContext(request)
    data = {}
    if request.method == 'POST':
        request_tool = RequestTools(request)
        advice = request_tool.get_parameter('advice')
        suggestion = Suggestions()
        try:
            suggestion.description = advice
            suggestion.save()
        except Exception:
            data['advice'] = advice
            data['message'] = "提交失败，请重新提交"
            return render_to_response('wss/mine/suggestions.html', data, context)
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:success'))

    elif request.method == 'GET':
        return render_to_response('wss/mine/suggestions.html', data, context)


#我的账户
@ExceptionRequired
@OpenidViewRequired
@JSAPI_TICKET_Required
def my_account(request):

    print("进入我的账户方法")
    context = RequestContext(request)
    print(request.user.username)
    data={}
    data=CREAT_DATA_CONTENT(request)
    access_token=cache.get('token',None)
    data["access_token"] = access_token
    #client = Client.objects(id='58cf5da0478c92746ee23f2f').first()
    try:
        client = Client.objects(user=request.user).first()
        wx_id =  client.wx_id
#         if not wx_id:
#             data["message"] = '没有用户微信ID'
#             return render_to_response('wss/bind.html', data, context)
    except:
        data["message"] = '未找到对应用户'
        return render_to_response('wss/bind.html', data, context)
    mine_headimgurl1=""
    try:
            mine_detail_url='https://api.weixin.qq.com/cgi-bin/user/info?access_token='+access_token+'&openid='+wx_id+'&lang=zh_CN'
            print(mine_detail_url)
            a = urllib.request.urlopen(mine_detail_url)
            OPEN_ID = a.read().decode("utf-8")
            jsonO = json.loads(OPEN_ID)
            mine_headimgurl = jsonO["headimgurl"]
            print(mine_headimgurl)
            if mine_headimgurl:
                mine_headimgurl1 = mine_headimgurl
        #except:
    except:
        mine_headimgurl1 = ""
    if mine_headimgurl1:
        data["mine_headimgurl"] = mine_headimgurl1
    else:
       data["mine_headimgurl"] = ""
    if request.method == 'POST':
        request_tool = RequestTools(request)
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_account'))

    elif request.method == 'GET':
        data['client'] = client
        year = datetime.datetime.now().strftime("%Y")
        start_year = datetime.datetime.strptime("{0}-01-01 00:00:00".format(year), DATETIME_STRING)
        end_year = datetime.datetime.strptime("{0}-12-31 23:59:59".format(year), DATETIME_STRING)
        order_year_set = Ordering.objects(client=client).filter((Q(pay_time__gt=start_year) & Q(pay_time__lt=end_year))|Q(state='paid')|Q(state='done'))

        month = datetime.datetime.now().strftime("%Y-%m")
        year_month = datetime.datetime.now().strftime("%Y")
        month_month = datetime.datetime.now().strftime("%m")
        if month_month == '12':
            month_next = str(int(year_month) + 1) + "-" + '01'
        else:
            month_next = year_month + "-" + str(int(month_month) + 1)
        start_month = datetime.datetime.strptime("{0}-01 00:00:00".format(month), DATETIME_STRING)
        end_month = datetime.datetime.strptime("{0}-01 00:00:00".format(month_next), DATETIME_STRING)
        order_month_set = Ordering.objects(client=client).filter((Q(pay_time__gt=start_month) & Q(pay_time__lt=end_month))&(Q(state='paid')|Q(state='done')))

        pay_price_year = 0
        pay_price_month = 0
        for order in order_year_set:
            pay_price_year += order.pay_price
        data['pay_price_year'] = pay_price_year
        print('当年前：'+str(pay_price_year))
        for order in order_month_set:
            pay_price_month += order.pay_price
        print('当月前：'+str(pay_price_year))
        data['pay_price_month'] = pay_price_month
        coupon_count = 0
        use_coupon_set = UseCoupon.objects(client=client)
        if use_coupon_set:
            for use_coupon in use_coupon_set:
                if use_coupon.coupon.end_date > datetime.datetime.now():
                    coupon_count += 1
        data['coupon_count'] = coupon_count
        #二维码
#         code_pic = request.session.get('code_pic', '')
#         request.session['code_pic'] =''
#         if code_pic:
#             data['code_pic'] = code_pic
#         else:
#             data['code_pic'] = 'close'
        return render_to_response('wss/mine/my_account.html', data, context)


#我的 预存保费
@OpenidViewRequired
def stored_premium(request):
    context = RequestContext(request)
    request_tool = RequestTools(request)
    client = Client.objects(user=request.user).first()
    data = {}
    if request.method == 'POST':
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_order'))
    elif request.method == 'GET':
        return render_to_response('wss/mine/stored_permium.html', data, context)


# 支付余额
@login_required
@csrf_exempt
def pay_user_balance(request):
    context = RequestContext(request)
    data = {}
    client = Client.objects.get(user=request.user)
    if request.method == 'POST':

        try:
            site_setting = SiteSettings.get_settings()
            # pingpp.api_key = 'sk_live_NwVpl5A28vrdDloQnO24In3R'
            # pingpp.api_key = 'sk_test_eTuzbPLmbXXPSmnbr1P8G4W1'
            pingpp.api_key = site_setting.pingpp_api_key
            channel = request.POST['channel']
            # 支付钱数
            stored_permium = request.POST.get('stored_permium', '')
            print('*******************************'+stored_permium)
            stored_permium = float(stored_permium)

            # 元转分
            stored_permium *= 100
            state_flag = request.POST['state_flag']
            order_id = request.POST.get('order_id', '')
            # 随机生成21位数，用于订单号
            order_no = FormatTools.get_random_paper_id()
            client_ip = request.META['REMOTE_ADDR']
            # price = math.ceil(order.need_pay_price * 100)
            # print(price)
            ch = pingpp.Charge.create(
                order_no=order_no,
                # channel='wx_pub',
                channel=channel,
                amount=round(stored_permium),
                subject='微信公众号付款',
                body='您即将支付{0}元'.format(round(stored_permium) / 100.0),
                currency='cny',
                app=dict(id=site_setting.pingpp_app_id),
                client_ip=client_ip,
                extra={'open_id': '{0}'.format(client.wx_id)}
                # extra={'product_id': 'f13a1f31as3d1fa6f6a456'}
            )
            
            if order_id: #微信支付时
                tlist = Transaction.objects(order_id=order_id).first()
                if tlist:    #订单交易记录已存在，但交易未完成，更新交易记录
                   tlist.update(set__order_no=order_no)
                   tlist.update(set__amount=stored_permium / 100.0)
                   tlist.update(set__channel=channel)
                   tlist.update(set__pingpp_no=ch.pingpp_id)
                   tlist.update(set__status="init")
                   tlist.update(set__result="未付款")
                   tlist.update(set__create_time=datetime.datetime.now())
                   if state_flag:
                       tlist.update(set__p_type=state_flag)
                   tlist.save()
                else:   #订单交易记录不存在，插入交易记录
                    createTransaction(order_no,stored_permium,channel,client,ch,state_flag,order_id)
            else:   #预存时
                createTransaction(order_no,stored_permium,channel,client,ch,state_flag,order_id)
            data['ch'] = ch
            print(ch)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResult(code=CODE_INTERNAL_SERVER_ERROR, message=str(e)).response()
        return JsonResult(code=CODE_SUCCESS, data=data).response()
    elif request.method == 'GET':
        return render_to_response('wss/mine/stored_permium.html', data, context)

def createTransaction(order_no,stored_permium,channel,client,ch,state_flag,order_id):
    try:
            transaction = Transaction()
            transaction.order_no = order_no
            transaction.amount = stored_permium / 100.0
            transaction.channel = channel
            transaction.user = client.user
            transaction.client = client
            transaction.pingpp_no = ch.pingpp_id
            transaction.status = "init"
            transaction.result = "未付款"
            if state_flag:
                transaction.p_type = state_flag
            transaction.order_id = order_id
            transaction.save()
    except Exception as e:
            print(traceback.format_exc())
# 支付成功 pay_ordering
# 支付余额
# @login_required
@csrf_exempt
def pay_result(request):
    print('*************************************')
    json_str = request.body.decode('utf-8')
    data_json = json.loads(json_str)
    print(data_json)
    request_tool = RequestTools(request)
    order_no = data_json['data']['object']['order_no']
    print("订单号********："+str(order_no))
    transaction = Transaction.objects(order_no=order_no).first()
    if not transaction:
        transaction.update(set__result='付款失败,该订单不存在!')
        transaction.update(set__status="failure")
        print("进入************if not transaction")
        return HttpResponse(status=500)
#     elif transaction.status  != "init":
#         print("进入************elif transaction.status != ")
#         transaction.update(set__result='付款失败')
#         transaction.update(set__status="failure")
#         return HttpResponse(status=500)

    if data_json['type'] == "charge.succeeded":
        print("进入****** if request_tool.get_parameter")
        transaction.update(set__status="success")
        transaction_no = data_json['data']['object']['transaction_no']
        print("交易号*********："+str(transaction_no))
        transaction.update(set__transaction_no=transaction_no)
        transaction.update(set__result='已付款')
        # 支付成功：pingxx的模拟支付回调
        amount = data_json['data']['object']['amount']
        import datetime
        import time
        nowtime = datetime.datetime.now()
        if transaction.p_type == "wx_deposit":
            transaction.client.balance += amount
            transaction.client.save()
        elif transaction.p_type == "wx_pay":
            if transaction.order_id:        
                order = Ordering.objects(id=transaction.order_id).first()
                order.update(set__state="paid")
                order.update(set__pay_price=amount)
                order.update(set__pay_time=nowtime)
                order.save()
        transaction.save()
        #手机端预存成功短信通知
        subtime = nowtime.strftime("%Y-%m-%d %H:%M:%S")
        phone =  transaction.client .profile.phone
        username = transaction.client.name
        string_tools = tools_string.StringTools()
        ad_touser = string_tools.get_string("administrator_wx_id")
        touser = transaction.client.wx_id
        if transaction.p_type == "wx_deposit":
            if int(transaction.client.balance/100)  >= 500:
                   content = "您预存金额:"+str(amount/100)+"已经成功预存!"+"预存余额已调整为:"+str(transaction.client.balance/100)+"元，如果有疑问请联系运之宝客服15910731816。"
                   ad_content = "手机"+str(phone)+"/姓名（"+str(username)+"）的用户于："+str(subtime)+"预存金额"+str(amount/100)+"元。"
            else:
                    content = "您预存金额:"+str(amount/100)+"已经成功预存!"+"预存余额已调整为:"+str(transaction.client.balance/100)+"元，预存余额低于500，为了避免余额不足导致无法提交订单，请尽快补充预存，如果有疑问请联系运之宝客服15910731816。"
                    ad_content = "手机"+str(phone)+"/姓名（"+str(username)+"）的用户于："+str(subtime)+"预存金额"+str(amount/100)+"元。预存余额为："+str(transaction.client.balance/100)+"元，余额不足500，请联系客户继续缴存。"
        elif transaction.p_type == "wx_pay": 
            content = "您的订单:"+str(order_no)+"已经成功支付!支付金额为"+str(amount/100)+"元，如有问题，请联系管理员。"
            ad_content = "手机号为"+str(phone)+"的用户于："+str(subtime)+"支付订单费用"+str(amount/100)+"元。订单号"+str(order_no)+"请管理员尽快处理订单！"
#    ***********************************测试微信段调用传单接口******************************************************************
#             try:
#                 if transaction.order_id:        
#                     order_test = Ordering.objects(id=transaction.order_id).first()
#                 else:
#                     order_test=''
#             except:
#                 order_test=''
#             if not order_test:
#                 gly_wx='oqgGUvz6B64uBI5oa8Z23yV8M_xM'
#                 send_wx_message(gly_wx,'未查找到订单信息')
#             if order_test.state=='paid':
#                 gly_wx='oqgGUvz6B64uBI5oa8Z23yV8M_xM'
#                 send_wx_message(gly_wx,'测试步骤1')
#                 if order_test.insurance_product.create_way == 'hjb' and not order_test.third_paper_id:
#                     try:
#                         order_pass_detail=order_pass_test(request, order_test.id)
#                         if order_pass_detail !='success':
#                             content1 = "用户订单:"+str(order_no)+"已经成功支付!提交汇聚宝过程出错注意查看。出错信息："+str(order_pass_detail)
#                             send_wx_message(gly_wx,content1)
#                     except Exception as e :
#                         content1 = "用户订单:"+str(order_no)+"已经成功支付!提交汇聚宝过程出错注意查看。出错信息："+str(e)
#                         send_wx_message(gly_wx,content1)
#                     except ParameterError as e:
#                         content1 = "用户订单:"+str(order_no)+"已经成功支付!提交汇聚宝过程出错注意查看。出错信息："+str(e)
#                         send_wx_message(gly_wx,content1)

#    ***********************************测试微信段调用传单接口end******************************************************************
            
        send_wx_message(touser,content)
        send_wx_message(ad_touser,ad_content)
        return HttpResponse(status=200)
    else:
        transaction.update(set__result='付款失败')
        transaction.update(set__status="failure")
        transaction.save()
        print("进入************if*********************************")
        return HttpResponse(status=500)


#我的支付详情
@OpenidViewRequired
def pay_detail(request):
    context = RequestContext(request)
    request_tool = RequestTools(request)
    client = Client.objects(user=request.user).first()
   # client = Client.objects(id='574e37d79a8f2b0e2a811ff2').first()
    data = {}
    if request.method == 'POST':
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_order'))
    elif request.method == 'GET':
        transaction_set = Transaction.objects(client=client,p_type='wx_deposit')
        data['transactions'] = transaction_set
        backstage_set = DepositStatistical.objects(client=client)
        data['backstage_set'] = backstage_set
        return render_to_response('wss/mine/transaction.html', data, context)


#我的优惠券列表
@OpenidViewRequired
@JSAPI_TICKET_Required
def coupon_list(request):
    context = RequestContext(request)
    request_tool = RequestTools(request)
    client = Client.objects(user=request.user).first()
    data={}
    data=CREAT_DATA_CONTENT(request)
    if request.method == 'POST':
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_order'))
    elif request.method == 'GET':
        client_coupon_set = UseCoupon.objects(client=client)
        data['client_coupons'] = client_coupon_set
        return render_to_response('wss/mine/coupon_list.html', data, context)


#我的优惠券详情
@OpenidViewRequired
@JSAPI_TICKET_Required
def coupon_detail(request, coupon_id):
    context = RequestContext(request)
    request_tool = RequestTools(request)
    # client = Client.objects(user=request.user).first()
    data={}
    data=CREAT_DATA_CONTENT(request)
    if request.method == 'POST':
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_order'))
    elif request.method == 'GET':
        coupon = Coupon.objects(id=coupon_id).first()
        data['coupon'] = coupon
        return render_to_response('wss/mine/coupon_detail.html', data, context)


#我的订单
@OpenidViewRequired
@JSAPI_TICKET_Required
def order_list(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    try:
        client = Client.objects(user=request.user).first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    if not client:
        data['message'] = '网络延迟未获取用户信息。'
        return render_to_response('wss/warn.html', data, context)
    url_test= str(settings.QUCHEXIAN_URL)
    QCX_url = url_test+"/mobile/myBillIndex?yzb=2&phone="+str(client.profile.phone)
    data['QCX_url'] = QCX_url
    
    request_tool = RequestTools(request)
    state = request_tool.get_parameter('state', '')
    data["order_list_state"] = 'all'
   
    if request.method == 'POST':
        # 根据用户类型转向特定页面
        #return HttpResponseRedirect(reverse('wss:my_order'))
         order_set = Ordering.objects(client=client,is_hidden=False)
         search_keyword = request.POST.get('search_keyword', '')
         if search_keyword :
            data['search'] = search_keyword
            order_set = request_tool.wx_my_order_filter(order_set=order_set, keyword=search_keyword)
        
         data['orders'] = order_set
         data['orders_wait'] = order_set.filter(Q(state='wait'))
         data['orders_init'] = order_set.filter(Q(state='init'))
         data['orders_paid'] = order_set.filter(Q(state='paid'))
         data['orders_done'] = order_set.filter(Q(state='done'))
         data['order_page']="my_order"
         return render_to_response('wss/mine/order_list.html', data, context)
    elif request.method == 'GET':
        if state == 'year':
            year = datetime.datetime.now().strftime("%Y")
            start_year = datetime.datetime.strptime("{0}-01-01 00:00:00".format(year), DATETIME_STRING)
            end_year = datetime.datetime.strptime("{0}-12-31 23:59:59".format(year), DATETIME_STRING)
            order_year_set = Ordering.objects(client=client).filter( ( Q(pay_time__gt=start_year) & Q(pay_time__lt=end_year) )&(Q(state='paid')|Q(state='done')))
#             order_year_set = Ordering.objects(client=client).filter((Q(pay_time__gt=start_year) & Q(pay_time__lt=end_year))|Q(state='paid')|Q(state='done'))
            data['orders'] = order_year_set
        elif state == 'month':

            month = datetime.datetime.now().strftime("%Y-%m")
            year_month = datetime.datetime.now().strftime("%Y")
            month_month = datetime.datetime.now().strftime("%m")
            if month_month == '12':
                month_next = str(int(year_month) + 1) + "-" + '01'
            else:
                month_next = year_month + "-" + str(int(month_month) + 1)
            start_month = datetime.datetime.strptime("{0}-01 00:00:00".format(month), DATETIME_STRING)
            end_month = datetime.datetime.strptime("{0}-01 00:00:00".format(month_next), DATETIME_STRING)
          #  order_month_set1 = Ordering.objects(client=client).filter(pay_time__gt=start_month )
            #order_month_set = order_month_set1.filter(Q(state='paid')|Q(state='done'))
            order_month_set = Ordering.objects(client=client).filter((Q(pay_time__gt=start_month) & Q(pay_time__lt=end_month))&(Q(state='paid')|Q(state='done')))

            data['orders'] = order_month_set
        else:
            data['order_page']="my_order"
   
            order_set = Ordering.objects(client=client,is_hidden=False)
            data['orders_wait'] = order_set.filter(Q(state='wait'))
            data['orders'] = order_set
            data['orders_init'] = order_set.filter(Q(state='init'))
            data['orders_paid'] = order_set.filter(Q(state='paid'))
            data['orders_done'] = order_set.filter(Q(state='done'))
        return render_to_response('wss/mine/order_list.html', data, context)


#订单详情
@OpenidViewRequired
@JSAPI_TICKET_Required
def order_detail(request, order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    if request.method == 'POST':
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_order'))

    elif request.method == 'GET':
        order = Ordering.objects(id=order_id).first()
        data['order'] = order
        return render_to_response('wss/mine/order_detail.html', data, context)


#清单详情
@OpenidViewRequired
@JSAPI_TICKET_Required
def batch_list(request, order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    if request.method == 'POST':
        request_tool = RequestTools(request)
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_order'))

    elif request.method == 'GET':
        order = Ordering.objects(id=order_id).first()
        data['order'] = order
        return render_to_response('wss/mine/batch_list.html', data, context)


    #清单详情图片
@OpenidViewRequired
@JSAPI_TICKET_Required
def batch_list_pic(request, order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    if request.method == 'POST':
        request_tool = RequestTools(request)
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_order'))

    elif request.method == 'GET':
        order = Ordering.objects(id=order_id).first()
        data['order'] = order
        return render_to_response('wss/mine/batch_list_pic.html', data, context)


    #电子保单图片
@OpenidViewRequired
@JSAPI_TICKET_Required
def insurance_list_pic(request, order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    if request.method == 'POST':
        request_tool = RequestTools(request)
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_order'))

    elif request.method == 'GET':
        order = Ordering.objects(id=order_id).first()
        data['order'] = order
        return render_to_response('wss/mine/insurance_list_pic.html', data, context)




#建议和意见
@CODE_View_Required
@JSAPI_TICKET_Required
def suggestions(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    if request.method == 'POST':
        request_tool = RequestTools(request)
        advice = request_tool.get_parameter('advice')
        suggestion = Suggestions()
        try:
            suggestion.description = advice
            suggestion.save()
        except Exception:
            data['advice'] = advice
            data['message'] = "提交失败，请重新提交"
            return render_to_response('wss/mine/suggestions.html', data, context)
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:success'))

    elif request.method == 'GET':
        return render_to_response('wss/mine/suggestions.html', data, context)


#联系客服
@CODE_View_Required
@JSAPI_TICKET_Required
def contact(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/mine/contact.html', data, context)

#我的车库
@OpenidViewRequired
def my_car_list(request):
    context = RequestContext(request)
    data={}
    client = Client.objects(user=request.user).first()
    #client = Client.objects(profile__phone='13856782311').first()
    data=CREAT_DATA_CONTENT(request)
#     car_sets = CarCertificate.objects(client=client)
#     data['car_sets'] = car_sets
    #2017/12/08修改流程
    #return render_to_response('wss/mine/my_car_list.html', data, context)
    return render_to_response('wss/mine/insurance_stewardship.html', data, context)
    

#创建车库
@OpenidViewRequired
def my_car_create(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    #client = Client.objects(profile__phone='13856782311').first()
    client = Client.objects(user=request.user).first()
    request_tool = RequestTools(request)
    wss_tools = DocumentWssTools(request)
    nowtime = datetime.datetime.now()
    subtime = nowtime.strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            certificate = CarCertificate()
            certificate = wss_tools.validation_create_car(certificate)
            certificate.client = client
            certificate.save()
             #通知管理员进行车辆审核
            phone =  certificate.client.profile.phone
            content = "手机号码"+str(phone)+"已经提交车辆审核信息，提交时间"+str(subtime)+"请审核！"
            string_tools = tools_string.StringTools()
            touser = string_tools.get_string("administrator_wx_id")
            send_wx_message(touser,content)
            data['message'] = '申请成功，等待审核'
            return HttpResponseRedirect(reverse('wss:myCar_list'))
        except CustomError as e:
           # get_parameter = "?message={0}".format(str(e))
            #return HttpResponseRedirect(reverse('wss:myCar_create')+get_parameter)
            data['message'] = e.message
            return render_to_response('wss/mine/my_car_create.html', data, context)
        except Exception as e:
            data['message'] = e.message
            return render_to_response('wss/mine/my_car_create.html', data, context)
#             get_parameter = "?message={0}".format(str(e))
#             return HttpResponseRedirect(reverse('wss:myCar_create')+get_parameter)
    else:
        years = []
        curryear = nowtime.strftime("%Y")
        init = 2015
        len =   int(curryear)-init+1
        for i in range(len): 
            years.append(init+i)       
        data['years'] = years
        data['len'] = len
        data['pc'] = ProvinceCode
        data['letters'] = Letter
        data['message'] = request.GET.get("message","").strip("'")
        return render_to_response('wss/mine/my_car_create.html', data, context)
#参考样例
@OpenidViewRequired
def reference_pic(request,type_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    if request.method == 'GET':
        if int(type_id) in [1,2,3]:
            data['img_url'] = 'pic/default/example'+type_id+'.jpg'
        elif  int(type_id) == 4:
            data['img_url'] = 'pic/default/example'+type_id+'.png'
    return render_to_response('wss/mine/my_car_ref_pic.html', data, context)
#车辆详情
@OpenidViewRequired
def my_car_detail(request,car_id):
    context = RequestContext(request)
    data={}
    if request.method == 'GET':
        car = CarCertificate.objects(id=car_id).first()
       #根据注册时间计算车龄
        car_age = calculate_car_age(car.issue_date)
        car.issue_date = car_age
        #保费合计金额（交强险+商业险）
        total_price =  car.liability_price+car.commercial_price+car.liability_tax
        #净费
        net_price =  total_price-car.oil_card_price
        data['car']=car
        data['total_price']=total_price
        data['net_price']=net_price
        return render_to_response('wss/mine/my_car_detail.html', data, context)
    
#编辑车辆信息
@OpenidViewRequired
def my_car_edit(request,car_id):
    context = RequestContext(request)
    data={}
    car_list = CarCertificate.objects(id=car_id).first()
    if request.method == 'POST':
         wss_tools = DocumentWssTools(request)
         try:
             car_list = wss_tools.validation_edit_car(car_list)
             car_list.save()
         except CustomError as e:
             get_parameter = "?message={0}".format(str(e))
             return HttpResponseRedirect(reverse('wss:car_edit', args=[car_list.id, ]) + get_parameter)
         return HttpResponseRedirect(reverse('wss:myCar_list'))
    else:
        short = car_list.plate_number[0:1]
        letter = car_list.plate_number[1:2]
        batch_plate_number = car_list.plate_number[-5:]
        data['car'] = car_list
        data['pc'] = ProvinceCode
        data['letters'] = Letter
        data['sel_short'] = short
        data['sel_letter'] = letter
        data['batch_plate_number'] = batch_plate_number
        data['message'] = request.GET.get('message','').strip("'")
        return render_to_response('wss/mine/my_car_edit.html', data, context)  

    
#删除车辆信息
@OpenidViewRequired
def my_car_delete(request,car_id):
    context = RequestContext(request)
    data={}
    if request.method == 'GET':
        car_list = CarCertificate.objects(id=car_id).first()
        if car_list:
            for image_url in car_list.plate_image_left:
                image_tools = ImageTools()
                image_tools.delete(image_url)
            car_list.delete()
        return HttpResponseRedirect(reverse('wss:myCar_list'))
    
#计算车龄
def calculate_car_age(registerdate):
        '''Calculates the age'''
        try:
            registerYear = registerdate.strftime("%Y")
            registerMonth = registerdate.strftime("%m")
            registerDate = registerdate.strftime("%d")
            nowtime = datetime.datetime.now()
            currYear = nowtime.strftime("%Y")
            currMonth = nowtime.strftime("%m")
            currDate = nowtime.strftime("%d")
            year = int(currYear) -int(registerYear); 
            month = int(currMonth)-int(registerMonth);
            date = int(currDate)-int(registerDate);
            if (year == 0):
                return 0
            elif (year >=1):
                if (month == 0):
                    if (date<0):
                            return  year-1
                    else:
                             return year
                elif(month <0) :
                    return  year-1
                else:
                    return  year
        except Exception as e:
            return e
 #上传       
@OpenidViewRequired
def my_car_upload(request,car_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    wss_tools = DocumentWssTools(request)
    nowtime = datetime.datetime.now()
    subtime = nowtime.strftime("%Y-%m-%d %H:%M:%S")
    certificate = CarCertificate.objects(id=car_id).first()
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            certificate = wss_tools.validation_create_car(certificate)
            certificate.save()
             #通知管理员进行车辆审核
            phone =  certificate.client.profile.phone
            content = "手机号码"+str(phone)+"已经提交车辆审核信息，提交时间"+str(subtime)+"请审核！"
            string_tools = tools_string.StringTools()
            touser = string_tools.get_string("administrator_wx_id")
            send_wx_message(touser,content)
            data['message'] = '申请成功，等待审核'
            return HttpResponseRedirect(reverse('wss:myCar_list'))
        except CustomError as e:
            get_parameter = "?message={0}".format(str(e))
            return HttpResponseRedirect(reverse('wss:car_upload',args=[certificate.id, ]) + get_parameter)
        except Exception as e:
            get_parameter = "?message={0}".format(str(e))
            return HttpResponseRedirect(reverse('wss:car_upload',args=[certificate.id, ]) + get_parameter)
    else:
        #车牌号回显
        plate_number = certificate.plate_number
        if plate_number:
            data["short"] = plate_number[0:3]
            data["batch_plate_number"] = plate_number[3:8]
        data['message'] = request.GET.get("message","").strip("'")
        data['posted_data'] = certificate
        return render_to_response('wss/mine/my_car_upload.html', data, context)  
    
    
    
    #我的车险订单
@OpenidViewRequired
@JSAPI_TICKET_Required
def car_order_list(request,order_state):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    
    client = Client.objects(user=request.user).first()
    #client = Client.objects(id='577dede653bc2b145bba28ff').first()
    clientphone = client.profile.phone
    request_tool = RequestTools(request)
    state = request_tool.get_parameter('state', '')
    order_state=order_state
    if request.method == 'POST':
        # 根据用户类型转向特定页面
        #return HttpResponseRedirect(reverse('wss:my_order'))
         if order_state == "all":      
                     order_set = InquiryInfo.objects(client=client, hidden=True)
                     data['order_state']="全部"
         else:
                  order_set = InquiryInfo.objects(client=client,state=order_state, hidden=True)
         search_keyword = request.POST.get('search_keyword', '')
         if search_keyword :
            data['search'] = search_keyword
            order_set = order_set.filter( Q(paper_id__contains=search_keyword)|Q(plate_number__contains=search_keyword) )
#             order_set = request_tool.wx_jdcbx_filter(order_set=order_set, keyword=search_keyword)
         if order_set:
             data['orders'] = order_set
         data['orders_verify'] = order_set.filter(Q(state='verify'))
         data['orders_price'] = order_set.filter(Q(state='price'))
         data['orders_wait'] = order_set.filter(Q(state='wait'))
         data['orders_init'] = order_set.filter(Q(state='init'))
         data['orders_paid'] = order_set.filter(Q(state='paid'))
         data['orders_done'] = order_set.filter(Q(state='done'))
         data['orders_fail'] = order_set.filter(Q(state='fail'))
         data['order_page']="my_order"
         return render_to_response('wss/mine/car_order_list.html', data, context)
    elif request.method == 'GET':
        if state == 'year':
            year = datetime.datetime.now().strftime("%Y")
            start_year = datetime.datetime.strptime("{0}-01-01 00:00:00".format(year), DATETIME_STRING)
            end_year = datetime.datetime.strptime("{0}-12-31 23:59:59".format(year), DATETIME_STRING)
            order_year_set = InquiryInfo.objects(client=client).filter( ( Q(pay_time__gt=start_year) & Q(pay_time__lt=end_year) )&(Q(state='paid')|Q(state='done')))
#             order_year_set = Ordering.objects(client=client).filter((Q(pay_time__gt=start_year) & Q(pay_time__lt=end_year))|Q(state='paid')|Q(state='done'))
            data['orders'] = order_year_set
        elif state == 'month':

            month = datetime.datetime.now().strftime("%Y-%m")
            year_month = datetime.datetime.now().strftime("%Y")
            month_month = datetime.datetime.now().strftime("%m")
            if month_month == '12':
                month_next = str(int(year_month) + 1) + "-" + '01'
            else:
                month_next = year_month + "-" + str(int(month_month) + 1)
            start_month = datetime.datetime.strptime("{0}-01 00:00:00".format(month), DATETIME_STRING)
            end_month = datetime.datetime.strptime("{0}-01 00:00:00".format(month_next), DATETIME_STRING)
          #  order_month_set1 = Ordering.objects(client=client).filter(pay_time__gt=start_month )
            #order_month_set = order_month_set1.filter(Q(state='paid')|Q(state='done'))
            order_month_set = InquiryInfo.objects(client=client).filter((Q(pay_time__gt=start_month) & Q(pay_time__lt=end_month))&(Q(state='paid')|Q(state='done')))

            data['orders'] = order_month_set
        else:
            data['order_page']="my_order"
            if order_state == "all":      
                     order_set = InquiryInfo.objects(client=client, hidden=True)
                     data['order_state']="全部"
            else:
                  order_set = InquiryInfo.objects(client=client,state=order_state, hidden=True)
            if order_state == "verify":      
                data['order_state']="待审核"
            elif  order_state == "price":      
                 data['order_state']="询价中"
            elif  order_state == "wait":      
                  data['order_state']="待确认"
            elif  order_state == "init":      
                  data['order_state']="未支付"
            elif  order_state == "paid":      
                  data['order_state']="已支付"
            elif  order_state == "done":      
                 data['order_state']="已完成"
            elif  order_state == "fail":      
                 data['order_state']="已驳回"
            data['orders'] = order_set
            data['orders_verify'] = order_set.filter(Q(state='verify'))
            data['orders_price'] = order_set.filter(Q(state='price'))
            data['orders_wait'] = order_set.filter(Q(state='wait'))
            data['orders_init'] = order_set.filter(Q(state='init'))
            data['orders_paid'] = order_set.filter(Q(state='paid'))
            data['orders_done'] = order_set.filter(Q(state='done'))
            data['orders_fail'] = order_set.filter(Q(state='fail'))
        return render_to_response('wss/mine/car_order_list.html', data, context)
    
    
    
    
#生成二维码
@ExceptionRequired
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_build_code_pic(request):
    context = RequestContext(request)
    print(request.user.username)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    try:
        client = Client.objects(user=request.user).first()
    except:
        return HttpResponseRedirect(reverse('wss:my_account'))
    try:
        BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
        phone=client.profile.phone
        path = BASE_ROOT+"/static/pic/user_code/"+str(client.id)+".png" 
        host = request.get_host()
        main_url="http://"+host+"/wss/register_code/?referee_id="+str(client.id)
        img=qrcode.make(str(main_url))
        img.save(path)
    except Exception as e:
        data['message'] = str(e)
        return render_to_response('wss/warn.html', data, context)
    try:
        client.QR_code_image = "/static/pic/user_code/"+str(client.id)+".png" 
        client.save()
    except:
        data['message'] ='网络不稳定，请稍后查看二维码'
        return render_to_response('wss/warn.html', data, context)
    data['code_pic'] ='open'
    data['code_pic_url'] ="/static/pic/user_code/"+str(client.paper_id)+str(phone)+".png" 
    return render_to_response('wss/register_concern.html', data, context)


#订单发送状态
def post_order_detail(request):
    data = {}
    gly_wx='oqgGUvz6B64uBI5oa8Z23yV8M_xM'
    #gly_wx='oYXlSwfedYTw0OtzfRy2SYpPrNE8'
    try:
        send_wx_message(gly_wx,'进入程序')
    except:
        pass
    if request.method == 'POST':
        order_id = request.POST.get('order_id', '')
    else:
        order_id = request.GET.get('order_id', '')
    try:
        if order_id:        
            order_test = Ordering.objects(id=order_id).first()
        else:
            return  JsonResult(data=data, code=CODE_ERROR, message='支付成功，未找到订单信息').response()
    except:
        return  JsonResult(data=data, code=CODE_ERROR, message='网络问题未找到订单信息').response()
    if not order_test:
        try:
            send_wx_message(gly_wx,'未查找到订单信息')
        except:
            pass
        return  JsonResult(data=data, code=CODE_ERROR, message='网络问题未找到订单信息.').response()
    if order_test.state=='paid':
        if order_test.insurance_product.create_way == 'hjb' and not order_test.third_paper_id:
            try:
                send_wx_message(gly_wx,'进入汇聚宝传值')
            except:
                pass
            try:
                order_pass_detail=order_pass_test(request, order_test.id)
                if order_pass_detail !='success':
                    try:
                        content1 = "用户订单:"+str(order_test.id)+"已经成功支付!提交汇聚宝过程出错注意查看。出错信息："+str(order_pass_detail)
                        send_wx_message(gly_wx,content1)
                    except:
                        pass
                    return  JsonResult(data=data, code=CODE_ERROR, message='支付成功，提交信息出错请联系管理员').response()
                else:
                    return JsonResult(data=data, code=CODE_SUCCESS).response()
            except Exception as e :
                content1 = "用户订单:"+str(order_test.paper_id)+"已经成功支付!提交汇聚宝过程出错注意查看。出错信息："+str(e)
                try:
                    send_wx_message(gly_wx,content1)
                except:
                    pass
                return  JsonResult(data=data, code=CODE_ERROR, message='支付成功，提交信息出错请联系管理员').response()
            except ParameterError as e:
                content1 = "用户订单:"+str(order_test.paper_id)+"已经成功支付!提交汇聚宝过程出错注意查看。出错信息："+str(e)
                send_wx_message(gly_wx,content1)
                return  JsonResult(data=data, code=CODE_ERROR, message='支付成功，提交信息出错请联系管理员').response()
        else:#CODE_ERROR = 1     # 访问失败
            return  JsonResult(data=data, code=CODE_ERROR, message='支付成功，请返回订单列表查看信息。').response()
    else:
        return  JsonResult(data=data, code=CODE_ERROR, message='订单未支付，请返回订单列表查看信息').response()
    
#2017/11/20运单保险
#我的订单
@OpenidViewRequired
@JSAPI_TICKET_Required
def yundan_order_list(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    data["order_list_state"] = 'car'
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    if not client:
        data['message'] = '网络延迟未获取用户信息。'
        return render_to_response('wss/warn.html', data, context)
    
    request_tool = RequestTools(request)
    state = request_tool.get_parameter('state', '')
    try:
       order_set = Ordering.objects(client=client,is_hidden=False,product_type='car')
    except Exception as e :
        data['message'] = '网络延迟,查询出错'+str(e)
        return render_to_response('wss/warn.html', data, context)
    if request.method == 'POST':
        # 根据用户类型转向特定页面
        #return HttpResponseRedirect(reverse('wss:my_order'))
         #order_set = Ordering.objects(client=client,is_hidden=False)
         search_keyword = request.POST.get('search_keyword', '')
         if search_keyword :
            data['search'] = search_keyword
            order_set = request_tool.wx_my_order_filter(order_set=order_set, keyword=search_keyword)
        
    data['orders'] = order_set
    data['orders_wait'] = order_set.filter(Q(state='wait'))
    data['orders_init'] = order_set.filter(Q(state='init'))
    data['orders_paid'] = order_set.filter(Q(state='paid'))
    data['orders_done'] = order_set.filter(Q(state='done'))
    data['order_page']="my_order"
    return render_to_response('wss/mine/yundan_order_list.html', data, context)



#－－－－－－－－－－－－－－－－－－－－－－－－－－     员工保险统计      －－－－－－－－－－－－－－－－－－－－－－－－－－
#员工保险列表
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_employee_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    try:
       employee_insurance_list = EmployeeInsurance.objects(client = client,is_hidden=False)
    except Exception as e :
        data['message'] = '网络延迟,查询出错'+str(e)
        return render_to_response('wss/warn.html', data, context)
    count = employee_insurance_list.count()
    page = PageTools()
    paging = page.get_paging(5, page_index, count)
    request.session['page_index_employee'] = paging['page_index']
    employee_insurance_list = employee_insurance_list[paging['start_item']:paging['end_item']]
    data['employee_insurance_list'] = employee_insurance_list
    data['paging'] = paging
    return render_to_response('wss/mine/wx_employee_list.html', data, context)



def wx_employee_detail(request,employee_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    try:
        employee_set = EmployeeInsurance.objects(id=employee_id).first()
        data["employee"]=employee_set
    except Exception as e:
        data['message'] = '网络延迟'+str(e)
        return render_to_response('wss/warn.html', data, context)
    return render_to_response('wss/mine/wx_employee_detail.html', data, context)

#查看保险管家中各个图片
def search_policy_picture(request,policy_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    state = request_tools.get_parameter('policy_state', '')
    data["state"]=str(state)
    data["pic_state"]=""
    data["policy_name"]=""
    if not state:
        data['message'] = '网络延迟,未获取到查看保单记录信息'
        return render_to_response('wss/warn.html', data, context)
    elif state == "employee":
        data["policy_name"]="员工保险保单详情"
        try:
            employee_set = EmployeeInsurance.objects(id=policy_id).first()
            data["policy"]=employee_set
        except Exception as e:
            data['message'] = '网络延迟'+str(e)
            return render_to_response('wss/warn.html', data, context)
    elif state == "freight":
        data["policy_name"]="货运年险保单详情"
        try:
            freight_set = ＦreightInsurance.objects(id=policy_id).first()
            data["policy"]=freight_set
        except Exception as e:
            data['message'] = '网络延迟'+str(e)
            return render_to_response('wss/warn.html', data, context)
    elif state == "personal":
        data["policy_name"]="个人保险保单详情"
        try:
            personal_set = PersonalInsurance.objects(id=policy_id).first()
            data["policy"]=personal_set
        except Exception as e:
            data['message'] = '网络延迟'+str(e)
            return render_to_response('wss/warn.html', data, context)
    elif state == "other_insurance":
        data["policy_name"]="其他保险保单详情"
        try:
            other_insurance_set = OtherInsurance.objects(id=policy_id).first()
            data["policy"]=other_insurance_set
        except Exception as e:
            data['message'] = '网络延迟'+str(e)
            return render_to_response('wss/warn.html', data, context)
    elif state == "car":
        pic_state = request_tools.get_parameter('pic_state', '')
        if not pic_state:
            data['message'] = '网络延迟，未找到查找信息类型，请退出后重试'+str(e)
            return render_to_response('wss/warn.html', data, context)
        elif pic_state not in ['plate','commercial','liability']:
            data['message'] = '网络延迟，未找到查找信息类型，请退出后重试。'+str(e)
            return render_to_response('wss/warn.html', data, context)
        else:
            if pic_state =='plate':
                data["policy_name"]="行驶证图片"
            if pic_state =='liability':
                data["policy_name"]="交强险保单信息"
            if pic_state =='commercial':
                data["policy_name"]="商业险保单信息"
            data["pic_state"]=pic_state
        try:
            car_set = CarCertificate.objects(id=policy_id).first()
            data["policy"]=car_set
        except Exception as e:
            data['message'] = '网络延迟'+str(e)
            return render_to_response('wss/warn.html', data, context)
    else:
        data['message'] = '网络延迟，造成未知错误，请稍后再试'
        return render_to_response('wss/warn.html', data, context)
    return render_to_response('wss/mine/search_policy_picture.html', data, context)

#－－－－－－－－－－－－－－－－－－－－－－－－－－     货运年险统计      －－－－－－－－－－－－－－－－－－－－－－－－－－
#货运年险列表
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_freight_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    try:
       freight_insurance_list = ＦreightInsurance.objects(client = client,is_hidden=False)
    except Exception as e :
        data['message'] = '网络延迟,查询出错'+str(e)
        return render_to_response('wss/warn.html', data, context)
    count = freight_insurance_list.count()
    page = PageTools()
    paging = page.get_paging(5, page_index, count)
    request.session['page_index_freight'] = paging['page_index']
    freight_insurance_list = freight_insurance_list[paging['start_item']:paging['end_item']]
    data['freight_insurance_list'] = freight_insurance_list
    data['paging'] = paging
    return render_to_response('wss/mine/wx_freight_list.html', data, context)



def wx_freight_detail(request,freight_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    try:
        freight_set = ＦreightInsurance.objects(id=freight_id).first()
        data["freight"]=freight_set
    except Exception as e:
        data['message'] = '网络延迟'+str(e)
        return render_to_response('wss/warn.html', data, context)
    return render_to_response('wss/mine/wx_freight_detail.html', data, context)

#－－－－－－－－－－－－－－－－－－－－－－－－－－    个人保险统计      －－－－－－－－－－－－－－－－－－－－－－－－－－
#货运年险列表
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_personal_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    try:
       personal_insurance_list = PersonalInsurance.objects(client = client,is_hidden=False)
    except Exception as e :
        data['message'] = '网络延迟,查询出错'+str(e)
        return render_to_response('wss/warn.html', data, context)
    count = personal_insurance_list.count()
    page = PageTools()
    paging = page.get_paging(5, page_index, count)
    request.session['page_index_personal'] = paging['page_index']
    personal_insurance_list = personal_insurance_list[paging['start_item']:paging['end_item']]
    data['personal_insurance_list'] = personal_insurance_list
    data['paging'] = paging
    return render_to_response('wss/mine/wx_personal_list.html', data, context)



def wx_personal_detail(request,personal_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    try:
        personal_set = PersonalInsurance.objects(id=personal_id).first()
        data["personal"]=personal_set
    except Exception as e:
        data['message'] = '网络延迟'+str(e)
        return render_to_response('wss/warn.html', data, context)
    return render_to_response('wss/mine/wx_personal_detail.html', data, context)

#－－－－－－－－－－－－－－－－－－－－－－－－－－    其他统计      －－－－－－－－－－－－－－－－－－－－－－－－－－
#其他保险列表
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_other_insurance_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    try:
       other_insurance_insurance_list = OtherInsurance.objects(client = client,is_hidden=False)
    except Exception as e :
        data['message'] = '网络延迟,查询出错'+str(e)
        return render_to_response('wss/warn.html', data, context)
    count = other_insurance_insurance_list.count()
    page = PageTools()
    paging = page.get_paging(5, page_index, count)
    request.session['page_index_other_insurance'] = paging['page_index']
    other_insurance_insurance_list = other_insurance_insurance_list[paging['start_item']:paging['end_item']]
    data['other_insurance_insurance_list'] = other_insurance_insurance_list
    data['paging'] = paging
    return render_to_response('wss/mine/wx_other_insurance_list.html', data, context)



def wx_other_insurance_detail(request,other_insurance_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    try:
        other_insurance_set = OtherInsurance.objects(id=other_insurance_id).first()
        data["other_insurance"]=other_insurance_set
    except Exception as e:
        data['message'] = '网络延迟'+str(e)
        return render_to_response('wss/warn.html', data, context)
    return render_to_response('wss/mine/wx_other_insurance_detail.html', data, context)
#－－－－－－－－－－－－－－－－－－－－－－－－－－    保险管家车辆部分      －－－－－－－－－－－－－－－－－－－－－－－－－－
#货运年险列表
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_car_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    try:
       car_insurance_list = CarCertificate.objects(client = client)
    except Exception as e :
        data['message'] = '网络延迟,查询出错'+str(e)
        return render_to_response('wss/warn.html', data, context)
    count = car_insurance_list.count()
    page = PageTools()
    paging = page.get_paging(5, page_index, count)
    request.session['page_index_car'] = paging['page_index']
    car_insurance_list = car_insurance_list[paging['start_item']:paging['end_item']]
    data['car_insurance_list'] = car_insurance_list
    data['paging'] = paging
    return render_to_response('wss/mine/wx_car_list.html', data, context)

def wx_car_detail(request,car_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    data['total_price']=''
    data['net_price']=''
    car_message = request.session.get('car_message', '')
    data["car_message"]=car_message
    request.session['car_message'] = ''
    try:
        car_set = CarCertificate.objects(id=car_id).first()
        data["car"]=car_set
        #保费合计金额（交强险+商业险）
        total_price=car_set.liability_tax+car_set.liability_price+car_set.commercial_price
        #净费
        net_price =  total_price-car_set.oil_card_price
        data['total_price']=total_price
        data['net_price']=net_price
    except Exception as e:
        data['message'] = '网络延迟'+str(e)
        return render_to_response('wss/warn.html', data, context)
    return render_to_response('wss/mine/wx_car_detail.html', data, context)

#修改车辆时间
def wx_change_car_time(request,car_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    time_type = request.POST.get('time_type', '')
    change_time_detail = request.POST.get('change_time_detail', '')
    try:
        car_set = CarCertificate.objects(id=car_id).first()
    except Exception as e:
        data['message'] = '网络延迟'+str(e)
        return render_to_response('wss/warn.html', data, context)
    if change_time_detail:
        try:
            change_time_detail = str(change_time_detail)[0:7]
            change_time_detail=change_time_detail +"-01"  +" 00:00:00"
            change_time_detail= datetime.datetime.strptime(change_time_detail,"%Y-%m-%d %H:%M:%S")
        except Exception as e:
            data['message'] = '网络延迟,获取参数不完成'+str(e)
            return render_to_response('wss/warn.html', data, context)
    else:
        data['message'] = '网络延迟,未获取到您想修改的时间参数'
        return render_to_response('wss/warn.html', data, context)
    if time_type =="license":
       time_name= "运营证到期时间"
       car_set.license_expiration_time=change_time_detail
    elif time_type =="grade":
       time_name= "等级评定到期时间"
       car_set.grade_expiration_time=change_time_detail
    elif time_type =="twolevel":
       time_name= "二级维护到期时间"
       car_set.twolevel_expiration_time=change_time_detail
    elif time_type =="trailer":
       time_name= "挂车车船稅到期时间"
       car_set.trailer_expiration_time=change_time_detail
    elif time_type =="plate":
       time_name= "行驶证校验有效期"
       car_set.plate_expiration_periods=change_time_detail
    else:
        data['message'] = '网络延迟,未获取到您想修改的时间类型。'
        return render_to_response('wss/warn.html', data, context)
    try:
        car_set.save()
    except Exception as e:
        data['message'] = '保存车辆信息出错，错误码'+str(e)
        return render_to_response('wss/warn.html', data, context)
    
    
    request.session['car_message'] = time_name+'修改成功'
    return HttpResponseRedirect(reverse('wss:wx_car_detail', args=[car_set.id, ]) )


#-----------------------------------------------分页获取保险管家各个信息------------------------------------------------------------------------
@OpenidViewRequired
@JSAPI_TICKET_Required
def get_policy_detail(request):
    policy_state = request.GET.get('policy_state', '')
    search_keyword = request.GET.get('search_keyword', '')
    page_index = request.GET.get('page', '')
    context = RequestContext(request)
    data = {}
    try:
        page_index = int(page_index)
    except:
        message= '网络延迟未获取分页信息'
        return  JsonResult(data=data, code=CODE_ERROR, message=message).response()
    request_tool = RequestTools(request)
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
    except:
        message= '网络延迟未获取用户信息'
        return  JsonResult(data=data, code=CODE_ERROR, message=message).response()
    if policy_state =="employee":
        try:
           policy_insurance_list = EmployeeInsurance.objects(client = client,is_hidden=False)
        except Exception as e :
            message= '网络延迟,查询出错'+str(e)
            return  JsonResult(data=data, code=CODE_ERROR, message=message).response()
    elif policy_state =="freight":
        try:
           policy_insurance_list = ＦreightInsurance.objects(client = client,is_hidden=False)
        except Exception as e :
            message= '网络延迟,查询出错'+str(e)
            return  JsonResult(data=data, code=CODE_ERROR, message=message).response()
    elif policy_state =="personal":
        try:
           policy_insurance_list = PersonalInsurance.objects(client = client,is_hidden=False)
        except Exception as e :
            message= '网络延迟,查询出错'+str(e)
            return  JsonResult(data=data, code=CODE_ERROR, message=message).response()
    elif policy_state =="other_insurance":
        try:
           policy_insurance_list = OtherInsurance.objects(client = client,is_hidden=False)
        except Exception as e :
            message= '网络延迟,查询出错'+str(e)
            return  JsonResult(data=data, code=CODE_ERROR, message=message).response()
    
    elif policy_state =="car":
        try:
           policy_insurance_list = CarCertificate.objects(client = client)
        except Exception as e :
            message= '网络延迟,车辆信息查询出错'+str(e)
            return  JsonResult(data=data, code=CODE_ERROR, message=message).response()
    else:
        message= '网络延迟,查询类型'+str(e)
        return  JsonResult(data=data, code=CODE_ERROR, message=message).response()
    count = policy_insurance_list.count()
    page = PageTools()
    paging = page.get_paging(5, page_index, count)
    policy_insurance_list = policy_insurance_list[paging['start_item']:paging['end_item']]
    if len(policy_insurance_list)>0:
        policy_insurance_list_detail=[]
        for policy_insurance_set in policy_insurance_list:
            try:
                policy_set={}
                #区分车辆和其他保险产品
                if policy_state =="car":
                    policy_set["plate_number"]=str(policy_insurance_set.plate_number) or ""
                    #商业险保险期限终止日期
                    if policy_insurance_set.commercial_date_stop:
                        try:
                            commercial_date_stop=str(policy_insurance_set.commercial_date_stop.strftime("%Y年%m月%d日") )
                        except:
                            commercial_date_stop=""
                    else:
                        commercial_date_stop=""
                    policy_set["commercial_date_stop"]=commercial_date_stop
                    #交强险保险期限终止日期
                    if policy_insurance_set.liability_date_stop:
                        try:
                            liability_date_stop=str(policy_insurance_set.commercial_date_stop.strftime("%Y年%m月%d日") )
                        except:
                            liability_date_stop=""
                    else:
                        liability_date_stop=""
                    policy_set["liability_date_stop"]=liability_date_stop#交强险保险期限终止日期
                    #年检时间
                    if policy_insurance_set.plate_expiration_periods:
                        try:
                            plate_expiration_periods=str(policy_insurance_set.plate_expiration_periods.strftime("%Y年%m月%d日") )
                        except:
                            plate_expiration_periods=""
                    else:
                        plate_expiration_periods=""
                    policy_set["plate_expiration_periods"]=plate_expiration_periods#年检时间
                    #运营证到期时间
                    if policy_insurance_set.license_expiration_time:
                        try:
                            license_expiration_time=str(policy_insurance_set.license_expiration_time.strftime("%Y年%m月%d日") )
                        except:
                            license_expiration_time=""
                    else:
                        license_expiration_time=""
                    policy_set["license_expiration_time"]=license_expiration_time#运营证到期时间
                    #等级评定到期时间
                    if policy_insurance_set.grade_expiration_time:
                        try:
                            grade_expiration_time=str(policy_insurance_set.grade_expiration_time.strftime("%Y年%m月%d日") )
                        except:
                            grade_expiration_time=""
                    else:
                        grade_expiration_time=""
                    policy_set["grade_expiration_time"]=grade_expiration_time#等级评定到期时间
                    #二级维护到期时间
                    if policy_insurance_set.twolevel_expiration_time:
                        try:
                            twolevel_expiration_time=str(policy_insurance_set.twolevel_expiration_time.strftime("%Y年%m月%d日") )
                        except:
                            twolevel_expiration_time=""
                    else:
                        twolevel_expiration_time=""
                    policy_set["twolevel_expiration_time"]=twolevel_expiration_time#二级维护到期时间
                    #挂车车船稅到期时间
                    if policy_insurance_set.trailer_expiration_time:
                        try:
                            trailer_expiration_time=str(policy_insurance_set.trailer_expiration_time.strftime("%Y年%m月%d日") )
                        except:
                            trailer_expiration_time=""
                    else:
                        trailer_expiration_time=""
                    policy_set["trailer_expiration_time"]=trailer_expiration_time#挂车车船稅到期时间
                elif  policy_state =="other_insurance":
                    a=1
                    #其他字段第一个
                    if policy_insurance_set.other_list :
                        field_content= policy_insurance_set.other_list[0].field_content
                        policy_set["field_content"]=field_content or ""
                    else:
                        policy_set["field_content"]= ""
                    #到期时间
                    if policy_insurance_set.date_stop :
                        date_stop= policy_insurance_set.date_stop 
                        date_stop = date_stop.strftime("%Y年%m月%d日")
                        policy_set["date_stop"]=date_stop or ""
                    else:
                        policy_set["date_stop"]= ""
                #个人保险部分
                elif  policy_state =="personal" or policy_state =="freight" or policy_state =="employee":
                    #公司名称
                    policy_set["simple_name"]=str(policy_insurance_set.company.simple_name ) or ""
                    #到期时间
                    if policy_insurance_set.date_stop :
                        date_stop= policy_insurance_set.date_stop 
                        date_stop = date_stop.strftime("%Y年%m月%d日")
                        policy_set["date_stop"]=date_stop or ""
                    else:
                        policy_set["date_stop"]= ""
                    #险种
                    if policy_insurance_set.insurance_type:
                        for insurance_type_set in policy_insurance_set.INSURANCE_TYPE:
                            if policy_insurance_set.insurance_type == insurance_type_set[0]:
                                policy_set["insurance_type"]=insurance_type_set[1]
                    else:
                        policy_set["insurance_type"]= ""
                else:
                    policy_set["paper_id"]=str(policy_insurance_set.paper_id) or ""
                    policy_set["simple_name"]=str(policy_insurance_set.company.simple_name ) or ""
                #公共部分
                policy_set["policy_id"]=str(policy_insurance_set.id) or ""
                create_time= policy_insurance_set.create_time 
                create_time_new = create_time.strftime("%Y年%m月%d日")
                policy_set["create_time"]=str(create_time_new)
                policy_insurance_list_detail.append(policy_set)
            except Exception as e :
                #break
                message= '网络延迟,查询出错'+str(e)
                return  JsonResult(data=data, code=CODE_ERROR, message=message).response()
        data['policy_insurance_list'] = policy_insurance_list_detail
    else:
        message= '未获取其他信息'
        return  JsonResult(data=data, code=CODE_ERROR, message=message).response()

    print(data)
    return JsonResult(data=data, code=CODE_SUCCESS).response()



