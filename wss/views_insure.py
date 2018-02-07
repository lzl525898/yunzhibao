from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from wss.tools import *
from common.models import *
from common.decorators import ExceptionRequired
from common.decorators import AdminRequired
# from wss.tools_wechat import
from django.contrib.auth.decorators import login_required
import datetime
import hashlib

#js_ticket
from wss.views_ticket import *

from wss.tools_wechat import OpenidViewRequired

from wss.views_sendmessage import  send_wx_message
from common.driver_dict import *
from pss.views_zhongan import ZhongAnApi
from django.conf import settings
#9/22下载文件
import urllib
import os
#发送短信
import common.tools_m5c_sms as m5c_sms_helper
#10/13转换成图片
#2017/10/26测试汇聚宝传值
from bms.views_order import order_pass_test

# import ghostscript
# from PyPDF2 import PdfFileReader, PdfFileWriter  
# from tempfile import NamedTemporaryFile  
# from PythonMagick import Image
#投保修改
def product_list1(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/insure/product_list.html', data, context)
#投保修改
# @CODE_View_Required
# @JSAPI_TICKET_Required
def product_list(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    product_kinds_list = PlatformProducts.objects().order_by('priority')
    product_kinds_list1 = []
    product_kinds_list2 = []
    for product in product_kinds_list:
        print(product.priority)
        print(product.product_type)
        print(product.wx_product_pic)
        if product.product_type in product_kinds_list1:
            continue
        else:
            
            product_kinds_list1.append(product.product_type)
            test=[product.product_type,product.wx_product_pic]
            product_kinds_list2.append(test)
    data["product_kinds_list"]=product_kinds_list2
    return render_to_response('wss/insure/product_list.html', data, context)

#多余的
def product_detail9(request):
    context = RequestContext(request)
    data = {}
    return render_to_response('wss/insure/product_detail9.html', data, context)

#多余的方法
def product_detail8(request):
    context = RequestContext(request)
    data = {}
    return render_to_response('wss/insure/product_detail8.html', data, context)

# @CODE_View_Required
# @JSAPI_TICKET_Required
def product_detail7(request):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/insure/product_detail7.html', data, context)

@CODE_View_Required
@JSAPI_TICKET_Required
def product_detail6(request):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/insure/product_detail6.html', data, context)

@CODE_View_Required
@JSAPI_TICKET_Required
def product_detail5(request):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/insure/product_detail5.html', data, context)

@CODE_View_Required
@JSAPI_TICKET_Required
def product_detail4(request):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/insure/product_detail4.html', data, context)

@CODE_View_Required
@JSAPI_TICKET_Required
def product_detail3(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/insure/product_detail3.html', data, context)

@CODE_View_Required
@JSAPI_TICKET_Required
def product_detail2(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/insure/product_detail2.html', data, context)

@CODE_View_Required
@JSAPI_TICKET_Required
def product_detail1(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/insure/product_detail1.html', data, context)


#意外保险
@CODE_View_Required
@JSAPI_TICKET_Required
def product_ywx_list(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    product_kinds_list = PlatformProducts.objects(product_type = 'ywx' ).order_by('priority')
    data["product_kinds_list"] =product_kinds_list
    return render_to_response('wss/insure/product_ywx_list.html', data, context)

@CODE_View_Required
@JSAPI_TICKET_Required
def product_ywx_detail1(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request) 
    product_id = request.GET.get("product_id","")
    
    if product_id:
            product_kinds_set = PlatformProducts.objects( id = product_id ).first()
            if product_kinds_set:
                data['product_kinds_set'] = product_kinds_set
            else:
                data['message'] = "未找到对应产品数据"
    else:
        data['message'] = "网络不稳定，未获取信息"
    return render_to_response('wss/insure/introduce_product.html', data, context)
#     return render_to_response('wss/insure/product_ywx_detail1.html', data, context)

@CODE_View_Required
@JSAPI_TICKET_Required
def product_ywx_detail2(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/insure/product_ywx_detail2.html', data, context)


@OpenidViewRequired
@JSAPI_TICKET_Required
def prompt(request):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    if request.method == 'POST':
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_order'))
    elif request.method == 'GET':
        try:
            client = Client.objects(user=request.user).first()
            insure_type = request_tool.get_parameter('type', '')
            data['insure_type'] = insure_type
            if insure_type == 'batch':
                data['docuemnts'] = client.product_batch.documents
            elif insure_type == 'ticket':
                data['docuemnts'] = client.product_ticket.documents
            else:
                return render_to_response('wss/insure/document_detail.html', data, context)
            return render_to_response('wss/insure/prompt.html', data, context)

        except CustomError as e:
            # request.session['message'] = e.message
            data['message'] = e.message
            return render_to_response('wss/insure/product_list.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            # request.session['message'] = str(e)
            return render_to_response('wss/insure/product_list.html', data, context)


def document_detail(request, document_id):
    context = RequestContext(request)
    data = {}
    insurance_document = InsuranceDocument.objects(id=document_id).first()
    data['insurance_document'] = insurance_document
    return HttpResponse(insurance_document.content)
    # return render_to_response('wss/insure/document_detail.html', data, context)


@OpenidViewRequired
@JSAPI_TICKET_Required
def order_create(request):
    context = RequestContext(request)
    referee_id=get_Recommend_id(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    data['test']=referee_id
    request_tool = RequestTools(request)
    insure_type = request_tool.get_parameter("insure_type", "")
    data['insure_type'] = insure_type
    client = Client.objects(user=request.user).first()
    data['client'] = client

    if client.product_batch:
        for batch_document in client.product_batch.documents:
            if "货物清单" in batch_document.name:
                data['document_batch_id'] = batch_document.id
                break

    if client.product_ticket:
        for ticket_document in client.product_ticket.documents:
            if "货物清单" in ticket_document.name:
                data['document_ticket_id'] = ticket_document.id
                break

    # if request.method == 'POST':
        # 根据用户类型转向特定页面

    return render_to_response('wss/insure/order_create.html', data, context)
    # elif request.method == 'GET':
    #     raise InvalidAccessError


@OpenidViewRequired
@JSAPI_TICKET_Required
def order_submit(request):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    wss_tools = DocumentWssTools(request)
    insure_type = request_tool.get_parameter("insure_type", "")
    data['insure_type'] = insure_type
    client = Client.objects(user=request.user).first()
    data['client'] = client
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            
            order = Ordering()
            order = wss_tools.validation_order(order)
            order.submit_style = 'submit'
            order.save()
           #催费微信通知
            crteamtop = request.get_host()
            ordersub_url = "http://"+crteamtop+reverse('wss:order_pay', args=[order.id, ])
            touser = order.client.wx_id
            content = "您有一笔"+str(order.insurance_product.name)+"保险订单，订单号为："+str(order.paper_id)+"，请确保在起运前完成交费，<a href='" +ordersub_url+ "'>点击本条信息进行交费</a>，如果您已完成交费，请忽视本条提醒，有问题请联系运之宝客服15910731868"
            send_wx_message(touser,content)
            # if order.state == 'paid':
            #     request.session['message'] = '投保成功'
            # elif order.state == 'init':
            #     request.session['message'] = '您的余额不足请充值'
        except CustomError as e:
            # request.session['message'] = e.message
            data['message'] = e.message
            return render_to_response('wss/insure/order_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            # request.session['message'] = str(e)
            return render_to_response('wss/insure/order_create.html', data, context)
        return HttpResponseRedirect(reverse('wss:order_pay', args=[order.id, ]))
    elif request.method == 'GET':
        raise InvalidAccessError

#已经弃用了
@OpenidViewRequired
@JSAPI_TICKET_Required
def order_pay(request, order_id):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    wss_tools = DocumentWssTools(request)
    request_tool.check_message(data)
#     client = Client.objects(id='577dede653bc2b145bba28ff').first()
   # client = Client.objects(id='57d760a2cba73c19c2cec462').first()
#test
   # client = Client.objects(id='57ac2dd6cba73c50116c647d').first()
    client = Client.objects(user=request.user).first()
    data['client'] = client
    order = Ordering.objects(id=order_id).first()
    data['order'] = order
    if request.method == 'POST':
        try:
            if order.state != 'init':
                request_tool.set_message('支付订单状态错误')
                return HttpResponseRedirect(reverse('wss:order_pay', args=[order.id, ]))

            password = request_tool.get_parameter('password', '').strip()
            if password:
                password = hashlib.sha1(password.encode('utf-8')).hexdigest()
                if client.password == password:
                    if order.company.paper_id == settings.ZHONGAN_COMPANY_CODE:
                            if order.product_type == "ticket" or order.product_type == "batch":
                                     if order.client.balance >=order.price:
                                         zhonganapi = ZhongAnApi(request)
                                         response = zhonganapi.applyValidate(order.id)
                                         responseinfo = json.loads(response['bizContent'])
                                         if responseinfo['isSuccess'] == "Y":
                                             order.insurance_id = responseinfo['policyNo']
                                             temp =[]
                                             temp.append(responseinfo['epolicyDownloadlink'])
                                             order.insurance_image_list = temp
                                             order.pay_money()
                                             order.state = "done"
                                             order.save()      
                                             if int(order.client.balance/100)  >= 500:
                                                      content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。"
                                             else:
                                                       content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。预存余额不足500，为了避免余额不足导致无法提交订单，请尽快补充预存！"   
                                             touser = order.client.wx_id
                                             send_wx_message(touser,content) 
                                         else:       
                                          request.session['message'] = responseinfo['failMsg']
                                     else:
                                        request_tool.set_message('金额支付不足')
                            else:
                                  request_tool.set_message('众安保险只承保单票保险')
                    else:             
                            if order.client.balance >= order.price:
                                order.pay_money()
                                order.save()
                                if int(order.client.balance/100)  >= 500:
                                        content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。"
                                else:
                                         content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。预存余额不足500，为了避免余额不足导致无法提交订单，请尽快补充预存！"   
                                touser = order.client.wx_id
                                send_wx_message(touser,content)
                                request_tool.set_message('支付成功')
                            else:
                                request_tool.set_message('余额不足，预存余额为{0}元，您至少还须预存{1}元，预存成功后请到“我的”--“我的订单”中选择该订单进行支付'.format(order.client.balance/100, (order.price-order.client.balance)/100))
                                return HttpResponseRedirect(reverse('wss:warn'))
                else:
                    request_tool.set_message('密码错误，请重新输入')
                    return HttpResponseRedirect(reverse('wss:order_pay', args=[order.id, ]))
            else:
                request_tool.set_message('密码不能为空')
                return HttpResponseRedirect(reverse('wss:order_pay', args=[order.id, ]))

        except CustomError as e:
            # request.session['message'] = e.message
            data['message'] = e.message
            return render_to_response('wss/insure/order_pay.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            # request.session['message'] = str(e)
            return render_to_response('wss/insure/order_pay.html', data, context)
        return HttpResponseRedirect(reverse('wss:order_detail', args=[order.id, ]))
    elif request.method == 'GET':
        return render_to_response('wss/insure/order_pay.html', data, context)
    
# def product_type_list(request,product_type):
#     context = RequestContext(request)
#     product_type = product_type
#     data={}
#     insurance_product_set = InsuranceProducts.objects()
#     product_type_name=""
#     if product_type == 'car' :
#         product_type_name="运单保险"
#         insurance_product_set = insurance_product_set.filter(Q(product_type='car')&Q(is_hidden=False)) 
#     elif product_type == 'ticket':
#         product_type_name="单票保险"
#         insurance_product_set = insurance_product_set.filter(Q(product_type='ticket')&Q(is_hidden=False)) 
#     elif product_type == 'batch':
#         product_type_name="车次保险"
#         insurance_product_set = insurance_product_set.filter(Q(product_type='batch')&Q(is_hidden=False)) 
#     else:
#         insurance_product_set = insurance_product_set.filter(Q(product_type=product_type)&Q(is_hidden=False)) 
#     data['product_type_name']=product_type_name
#     data['insurance_product_set']=insurance_product_set
#     print(product_type)
#     return render_to_response('wss/insure/product_type_list.html', data, context)

# def product_detial(request,product_id):
#     context = RequestContext(request)
#     product_id = product_id
#     data={} 
#     if product_id:
#         try:
#             insurance_product_set = InsuranceProducts.objects()
#             insurance_product_set = insurance_product_set.filter(Q(id= product_id )).first()
#             data['insurance_product'] =insurance_product_set
#         except:
#             data['message'] = "未找到对应产品，请返回上一步"
#     return render_to_response('wss/insure/product_detial.html', data, context)




#投保
# @OpenidViewRequired
# @JSAPI_TICKET_Required
# def product_prompt(request):
#     context = RequestContext(request)
#     data = {}
#     data=CREAT_DATA_CONTENT(request)
#     request_tool = RequestTools(request)
#     request_tool.check_message(data)
#     if request.method == 'POST':
#         # 根据用户类型转向特定页面
#         return HttpResponseRedirect(reverse('wss:my_order'))
#     elif request.method == 'GET':
#         product_id=request_tool.get_parameter('product_id', '')
#         try:
#             insurance_product_set = InsuranceProducts.objects()
#             #             client = Client.objects(id='577dede653bc2b145bba28ff').first()
#             insurance_product_set = insurance_product_set.filter(Q(id= product_id )).first()
#             a =insurance_product_set.is_hidden
#             print(insurance_product_set.is_hidden)
#             print(a)
#             if insurance_product_set.is_hidden == False:
#                 data['docuemnts'] = insurance_product_set.documents
#                 data['product_id']=product_id
#             else:
#                data['message'] ="您所选择的产品已下架，请返回上一级选择其他产品"
#                return render_to_response('wss/insure/product_detial.html', data, context) 
# 
#             return render_to_response('wss/insure/product_prompt.html', data, context)
#         except CustomError as e:
#             # request.session['message'] = e.message
#             data['message'] = e.message
#             return render_to_response('wss/insure/product_detial.html', data, context)
#         except Exception as e:
#            # print(traceback.format_exc())
#             data['message'] = str(e)
#             # request.session['message'] = str(e)
#             return render_to_response('wss/insure/product_detial.html', data, context)
        
        
        
# @OpenidViewRequired
# @JSAPI_TICKET_Required
# def order_create_update(request):
#     context = RequestContext(request)
#     referee_id=get_Recommend_id(request)
#     data = {}
#     data=CREAT_DATA_CONTENT(request)
#     data['test']=referee_id
#     request_tool = RequestTools(request)
#     product_id = request_tool.get_parameter("product_id", "")
#     data['product_id']=product_id
#     order = Ordering()
#     data['transport_type']=order.TRANSPORT_TYPE
#     data['common_good_list']=order.COMMON_GOOD
#     data['pack_method_list']=order.PACK_METHOD
#     data['pc'] = ProvinceCode
#     data['letters'] = Letter
#     client = Client.objects(user=request.user).first()
#     data['client'] = client
#     cargo_area_list = CargoArea.objects()
#     data['cargo_area_list'] = cargo_area_list
#     if product_id:
#         try:
#             insurance_product_set = InsuranceProducts.objects()
#             insurance_product_set = insurance_product_set.filter(Q(id= product_id )).first()
#             product_cargo_set=ProductCargo.objects()
#             product_cargo_set=product_cargo_set.filter(Q(product= insurance_product_set ))
#             data['product_cargo_set'] = product_cargo_set
#             
#             for document in insurance_product_set.documents:
#                 if "货物清单" in document.name:
#                     data['document_id'] = document.id
#                     break
# #             client = Client.objects(id='577dede653bc2b145bba28ff').first()
# #             data['insurance_product'] =insurance_product_set
#             if insurance_product_set.is_hidden == False:
#                 data['insurance_product'] =insurance_product_set
#                 data['product_id']=product_id
#             else:
#                data['message'] ="您所投保的产品已下架，请返回上一级选择其他产品"
#                return render_to_response('wss/insure/product_prompt.html', data, context)
# #                return render_to_response('wss/insure/order_create_update.html', data, context)
#         except:
#             data['message'] = "未找到对应产品，请返回上一步"
#             return render_to_response('wss/insure/product_prompt.html', data, context)
#     return render_to_response('wss/insure/order_create_update.html', data, context)
        
        

# @OpenidViewRequired
# @JSAPI_TICKET_Required
# def order_submit_update(request):
#     context = RequestContext(request)
#     data = {}
#     data=CREAT_DATA_CONTENT(request)
#     request_tool = RequestTools(request)
#     wss_tools = DocumentWssTools(request)
#     product_id = request_tool.get_parameter("product_id", "")
#     data['product_id']=product_id
#     #client = Client.objects(id='574e37d79a8f2b0e2a811ff2').first()
#     cargo_area_list = CargoArea.objects()
#     data['cargo_area_list'] = cargo_area_list
#     client = Client.objects(user=request.user).first()
# 
#     data['client'] = client
#     if request.method == 'POST':
#         data['posted_data'] = request.POST
#         data['pc'] = ProvinceCode
#         data['letters'] = Letter
#         try:
#             order = Ordering()
#             #下拉菜单内容
#             data['transport_type']=order.TRANSPORT_TYPE
#             data['common_good_list']=order.COMMON_GOOD
#             data['pack_method_list']=order.PACK_METHOD
#             insurance_product_set = InsuranceProducts.objects()
#             insurance_product_set = insurance_product_set.filter(Q(id= product_id )).first()
#             product_cargo_set=ProductCargo.objects()
#             product_cargo_set=product_cargo_set.filter(Q(product= insurance_product_set ))
#             data['product_cargo_set'] = product_cargo_set
#             for document in insurance_product_set.documents:
#                 if "货物清单" in document.name:
#                     data['document_id'] = document.id
#                     break
#             data['insurance_product'] =insurance_product_set
#             data['insure_type'] =insurance_product_set.product_type
#             #验证订单
#             type=("car","ticket","batch")
#             if insurance_product_set.product_type in type:
#                 order = wss_tools.validation_order_batch(order)
#             else:
#                 data['message'] = '未找到产品对应产品类型，请检查投保产品'
#                 return render_to_response('wss/insure/order_create_update.html', data, context)
# #             order = wss_tools.validation_order1(order)
#             order.submit_style = 'submit'
#             order.save()
#            #催费微信通知
#             crteamtop = request.get_host()
#             ordersub_url = "http://"+crteamtop+reverse('wss:order_pay', args=[order.id, ])
#             touser = order.client.wx_id
#             content = "您有一笔"+str(order.insurance_product.name)+"保险订单，订单号为："+str(order.paper_id)+"，请确保在起运前完成交费，<a href='" +ordersub_url+ "'>点击本条信息进行交费</a>，如果您已完成交费，请忽视本条提醒，有问题请联系运之宝客服15910731868"
#             send_wx_message(touser,content)
#         except CustomError as e:
#             # request.session['message'] = e.message
#             data['message'] = e.message
#             return render_to_response('wss/insure/order_create_update.html', data, context)
#         except Exception as e:
#             print(traceback.format_exc())
#             data['message'] = str(e)
#             # request.session['message'] = str(e)
#             return render_to_response('wss/insure/order_create_update.html', data, context)
#         return HttpResponseRedirect(reverse('wss:order_pay', args=[order.id, ]))
#     elif request.method == 'GET':
#         raise InvalidAccessError  


#产品介绍页面（最新版）
@CODE_View_Required
@JSAPI_TICKET_Required
def introduce_product(request,product_type):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    data['product_type'] = product_type
    try:

        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        client = Client.objects(user=request.user).first()

        data["client"]=client
    except:
        data["client"]=""
    if product_type:
        product_kinds_set = PlatformProducts.objects(product_type = product_type ).first()
        if product_kinds_set:
            data['product_kinds_set'] = product_kinds_set
        else:
            data['message'] = "未找到对应产品数据"
    else:
        data['message'] = "网络不稳定，未获取产品类型"
    return render_to_response('wss/insure/introduce_product.html', data, context)
    
#投保页面(2017)
@OpenidViewRequired
@JSAPI_TICKET_Required
def insure(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    cargo_area_list = CargoArea.objects()
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    try:
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        client = Client.objects(user=request.user).first()
        data["client"]=client
    except:
        data["client"]=""
    data['cargo_area_list'] = cargo_area_list
    cargolist =[]
    cargo_set = Cargo.objects(state = True).order_by('cargo_priority')
    for cargoobj in cargo_set:
                cargolist.append(cargoobj.cargo_name)
    data["cargo_set"] = cargolist
    if request.method == 'GET':
        insure_type = request_tool.get_parameter('type', '')
        data['product_type'] = insure_type
        order = Ordering()
        data['transport_type']=order.TRANSPORT_TYPE
        data['pack_method_list']=order.PACK_METHOD
#         data['pc'] = ProvinceCode
#         data['letters'] = Letter
        
        #cargo_type_list = Cargo.objects(state = True).order_by('ct_priority')

        #data["cargo_list"] = cargo_set
        return render_to_response('wss/insure/order_create_amendment.html', data, context)



#按条件筛选订单订单详情(2017)
# @OpenidViewRequired
# @JSAPI_TICKET_Required
def filter_product(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    wss_tools = DocumentWssTools(request)
    product_type  = request_tool.get_parameter("product_type", "")
    data['product_type'] = product_type
    cargo_area_list = CargoArea.objects()
    data['cargo_area_list'] = cargo_area_list

    order = Ordering()
    data['transport_type']=order.TRANSPORT_TYPE
    data['pack_method_list']=order.PACK_METHOD
    cargolist =[]
    cargo_set = Cargo.objects(state = True).order_by('cargo_priority')
    for cargoobj in cargo_set:
                cargolist.append(cargoobj.cargo_name)
    data["cargo_set"] = cargolist
    #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
    client = Client.objects(user=request.user).first()

    data["client"]=client
    if product_type == 'car' :
        data['name'] = "运单保险"
    elif product_type == 'ticket':
        data['name'] = "单票保险"
    elif product_type == 'batch':
        data['name'] = "车次保险"
    else:
        data['name'] = "您选择的产品类型不存在" 
    if request.method == 'POST':
        # 根据用户类型转向特定页面
        data['posted_data'] = request.POST
        try:
            order = Ordering()
            #下拉菜单
            data['transport_type']=order.TRANSPORT_TYPE
            data['pack_method_list']=order.PACK_METHOD
#             data['pc'] = ProvinceCode
#             data['letters'] = Letter
#             cargo_set = Cargo.objects(state = True).order_by('cargo_priority')
#             data["cargo_set"] = cargo_set
            #cargo_type_list = Cargo.objects(state = True).order_by('ct_priority')
            #data["cargo_type_list"] = cargo_type_list
            order = wss_tools.wss_validation_order(order)
            order.save()
            order_id = order.id
            return HttpResponseRedirect(reverse('wss:order_wait', args=[order_id, ]))
        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('wss/insure/order_create_amendment.html', data, context)
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('wss/insure/order_create_amendment.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('wss/insure/order_create_amendment.html', data, context)
    elif request.method == 'GET':
        return HttpResponseRedirect(reverse('wss:product_list', args=["", ""]))
    
#创建订单，订单未提交状态
def order_wait(request , order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    wss_tools = DocumentWssTools(request)
    order_id=order_id
    if not order_id:
        data["message"] = "未获取订单编码，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        order = Ordering.objects(id=order_id).first()
        
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
    test_state=['paid','done']
    if order.state in test_state:
        data["message"] = "错误码：40010 ，网络不稳定"
        return render_to_response('wss/warn.html', data, context)
    if order:
        #添加判断订单类型
        data["order_product_type"] =order.product_type
        #将订单还原成未选择的订单状态11-21添加测试，测试是否解决选择产品后订单号出现空的情况
#         try:
#             order.insurance_product=None
#             order.company =None
#             order.insurance_type = ''
#             order.paper_id=''
#             order.good_type=''
#             order.insurance_rate=0.0
#             order.price=0
#             order.old_price=0
#             order.coupon=None
#             order.state= 'wait'
#             order.save()
#         except Exception as e:
#             data["message"] = str(e)
#             return render_to_response('wss/warn.html', data, context)
#测试结束
        
        #实时筛选订单可保护信息
        insurable_products_list=[]
        message=''
        try:
            insurable_products_list=wss_tools.wss_validation_insurable_products(order)
        except ParameterError as e:
            message = str(e)
        except CustomError as e:
            message = str(e)
        except Exception as e:
            message= str(e)
        if len(insurable_products_list)==0:
            data['product_detail']='实时询价结果未筛出合适产品，原因：'+str(message)
        else:
            data['product_detail']='实时询价共筛出'+str(len(insurable_products_list))+'款产品可保'
        data['order'] = order
        data['message'] = message
        data['insurable_products_list']=insurable_products_list
        return render_to_response('wss/insure/order_wait.html', data, context)
    else:
       data["message"] = "未获取到订单详情，请稍后重试"
       return render_to_response('wss/warn.html', data, context)
   
#创建订单，选择产品
def order_choose_product(request , order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    wss_tools = DocumentWssTools(request)
    order_id=order_id
    if not order_id:
        data["message"] = "未获取订单编码，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        order = Ordering.objects(id=order_id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
    if order.state != 'wait' and order.state != 'init' :
        data["message"] = "此订单状态，不可修改投保保险公司"
        return render_to_response('wss/warn.html', data, context)
    if request.method == 'POST':
        product_id= request.POST.get('product_id','')
        state= request.POST.get('state','')
    else:
        product_id= request.GET.get('product_id','')
        state= request.GET.get('state','')
    if not product_id:
        data["message"] = "未获取订单选择的产品信息，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        product = InsuranceProducts.objects(id=product_id).first()
    except:
        data["message"] = "网络不稳定，或产品信息不存在"
        return render_to_response('wss/warn.html', data, context)
    if order and product:
        try:
            order.insurance_product=product
            order.company = product.company
            order.product_type = product.product_type
            order.insurance_type = product.insurance_type
#             order.state= 'init'
#             order.save()
        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('wss/warn.html', data, context)
        except CustomError as e:
            data['message'] =e.message
            return render_to_response('wss/warn.html', data, context)
        except Exception as e:
            data['message'] = str(e)
            return render_to_response('wss/warn.html', data, context)
        product_type=order.product_type
        if product_type == 'batch':
            order.commission_ratio = product.commission_ratio
        elif product_type == 'ticket':
            try:
                productCargoall= ProductCargo.objects(cargo=order.cargo,product=product).first()
            except Exception as e:
                data['message'] = '40001-B,未找到对应数据：'+str(e)
                return render_to_response('wss/warn.html', data, context)
            if productCargoall:
                order.good_type = productCargoall.state
            else:
                data['message'] = '40001-D,未找到对应数据：'+str(e)
                return render_to_response('wss/warn.html', data, context)
        try:
            order.state= 'init'
            order.save()
        except Exception as e:
            data['message'] = '40001-C,未找到对应数据：'+str(e)
            return render_to_response('wss/warn.html', data, context)  
        if state =='bms':
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
        return HttpResponseRedirect(reverse('wss:order_detail_update', args=[order.id, ]))
    else:
       data["message"] = "未获取到订单详情，请稍后重试"
       return render_to_response('wss/warn.html', data, context)
    
#创建订单   订单详情页面
# @OpenidViewRequired
# @JSAPI_TICKET_Required
def order_detail_update(request , order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    order_id=order_id
    #添加运单分页返回部分
    order_list_state = request_tool.get_parameter("order_list_state")
    data["order_list_state"] = order_list_state
    if not order_id:
        data["message"] = "未获取订单编码，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        order = Ordering.objects(id=order_id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
    if order:
        #下载文档
        if order.company.paper_id == settings.ZHONGAN_COMPANY_CODE:
            if order.product_type == "ticket" and order.state=="done":
                try:  
                    BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                    file_name=str(order.id)+'.pdf'
                    #os.system("chmod +R 777 "+BASE_ROOT+"/static/order/doc_file/") 
                    path = BASE_ROOT+"/static/order/doc_file/"+file_name
                    #os.system("chmod  -R 777 "+path) 
                    url=order.insurance_image_list[0]
                    urllib.request.urlretrieve(url , path) #python2中用的 urllib.urlretrieve(url1 , path)
                except Exception as e:
                    message =message+str(e)+"网络异常，保单图片下载失败请联系管理管"
                    data['message'] = message
        #下载文档结束
        data['order'] = order
        data['docuemnts'] = order.insurance_product.documents
        return render_to_response('wss/insure/order_confirm.html', data, context)
    else:
       data["message"] = "未获取到订单详情，请稍后重试"
       return render_to_response('wss/warn.html', data, context)
    
    

#编辑订单
@OpenidViewRequired
@JSAPI_TICKET_Required
def order_edit(request , order_id ):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    wss_tools = DocumentWssTools(request)
    cargo_area_list = CargoArea.objects()
    data['cargo_area_list'] = cargo_area_list
    message=request.session.get('wx_delete_pic', '')
    data["message"] = message
    request.session['wx_delete_pic'] = ''
    #2017/07/27添加页面方法
    add_state=''
    if request.method == 'GET':
        add_state   =     request.GET.get('add_state')
    else:
        add_state   =     request.POST.get('add_state') 
    add_state=str(add_state)
    data["add_state"] = add_state
        
    if not order_id:
        data["message"] = "未获取订单编码，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        order = Ordering.objects(id=order_id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
#     try:
    if order:
        data['order'] = order 
        #车牌号回显
        plate_number = order.plate_number
        if plate_number:
            data["short"] = plate_number[0:3]
            data["batch_plate_number"] = plate_number[3:8]
        #包装方式、运输方式回显
        if order.product_type == "ticket":

#             cargo_type_list = Cargo.objects(state = True).order_by('ct_priority')
#             data["cargo_type_list"] = cargo_type_list#货物大类
            cargo_set = Cargo.objects(state = True)
#             cargo_type = order.cargo.cargo_type
            data["cargo_set"] = cargo_set#货物对象列表
            
            pack_method_list=order.PACK_METHOD
            try:
                pack_family = ""
                test =0
                for pack_method in pack_method_list:
                    for pack_detail in pack_method[1]:
                        if pack_detail[0]==order.pack_method:
                            a=pack_detail[1]
                            test=1
                            break
                    if test==1:
                        pack_family = pack_method[0][0]
                        break
                data["pack_family"]=pack_family
            except:
                data['message'] = order.pack_method+"未找到订单对应的包装方式"
            transport_type_list=order.TRANSPORT_TYPE
            try:
                transport_type_val = ""
                for transport_type in transport_type_list:
                        if transport_type[0] == order.transport_type:
                            transport_type_val = transport_type[1]
                            break
                data["transport_type"] = transport_type_val
            except:
                data['message'] = order.pack_method+"未找到订单对应的包装方式"
                return render_to_response('wss/insure/order_edit.html', data, context)

        cargolist =[]
        cargo_set = Cargo.objects(state = True).order_by('cargo_priority')
        for cargoobj in cargo_set:
                cargolist.append(cargoobj.cargo_name)
        data["cargo_set"] = cargolist            
        if request.method == 'GET':
            
            return render_to_response('wss/insure/order_edit.html', data, context)
        else:
            try:
                order = wss_tools.wss_validation_order(order)
                order.save()
                #2017/11/30订单编辑后清空众安信息
                order.tb_client_type=""
                order.holderCertNo=""
                order.taxpayerRegNum=""
                order.tb_holderCertType=""
                order.bb_insureCertType=""
                order.bb_insureCertNo=""
                order.plate_number_plus=""
                #清空结束
                order_id = order.id
                return HttpResponseRedirect(reverse('wss:order_wait', args=[order.id, ]))
            except CustomError as e:
                # request.session['message'] = e.message
                data['message'] = e.message
                return render_to_response('wss/insure/order_edit.html', data, context)
            except ParameterError as e:
                data['message'] = e.message
                return render_to_response('wss/insure/order_edit.html', data, context)
            except Exception as e:
                data['message'] = str(e)
                return render_to_response('wss/insure/order_edit.html', data, context)
                
    else:
       data["message"] = "未获取到订单详情，请稍后重试"
       return render_to_response('wss/warn.html', data, context)
#     except Exception as e:
#             data['message'] = str(e)
#             return render_to_response('wss/warn.html', data, context)

#2017/6/28复制一单
def order_copy(request , order_id ):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    wss_tools = DocumentWssTools(request)
    cargo_area_list = CargoArea.objects()
    data['cargo_area_list'] = cargo_area_list
    message=request.session.get('wx_delete_pic', '')
    data["message"] = message
    request.session['wx_delete_pic'] = ''
    if not order_id:
        data["message"] = "未获取订单编码，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        order = Ordering.objects(id=order_id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
#     try:
    if order:
        data['order'] = order 
        #车牌号回显
        plate_number = order.plate_number
        if plate_number:
            data["short"] = plate_number[0:3]
            data["batch_plate_number"] = plate_number[3:8]
        #包装方式、运输方式回显
        if order.product_type == "ticket":
            cargo_set = Cargo.objects(state = True)
            data["cargo_set"] = cargo_set#货物对象列表
            pack_method_list=order.PACK_METHOD
            try:
                pack_family = ""
                test =0
                for pack_method in pack_method_list:
                    for pack_detail in pack_method[1]:
                        if pack_detail[0]==order.pack_method:
                            a=pack_detail[1]
                            test=1
                            break
                    if test==1:
                        pack_family = pack_method[0][0]
                        break
                data["pack_family"]=pack_family
            except:
                data['message'] = order.pack_method+"未找到订单对应的包装方式"
                return render_to_response('wss/warn.html', data, context)
            transport_type_list=order.TRANSPORT_TYPE
            try:
                transport_type_val = ""
                for transport_type in transport_type_list:
                        if transport_type[0] == order.transport_type:
                            transport_type_val = transport_type[1]
                            break
                data["transport_type"] = transport_type_val
            except:
                data['message'] = order.pack_method+"未找到订单对应的包装方式"
                return render_to_response('wss/warn.html', data, context)

        cargolist =[]
        cargo_set = Cargo.objects(state = True).order_by('cargo_priority')
        for cargoobj in cargo_set:
                cargolist.append(cargoobj.cargo_name)
        data["cargo_set"] = cargolist    
        return render_to_response('wss/insure/order_copy.html', data, context)        
                
    else:
       data["message"] = "未获取到订单详情，请稍后重试"
       return render_to_response('wss/warn.html', data, context)

    
#删除订单
@OpenidViewRequired
@JSAPI_TICKET_Required
def order_delete(request , order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    order_id = order_id
    if order_id:
        try:
            order = Ordering.objects(id= order_id).first()
            if order:
                state=order.state
                if order.state == "init" or order.state == 'wait':
                    order.delete()
                    data["message"] = "删除订单成功"
                    return HttpResponseRedirect(reverse('wss:order_list'))
                    #return render_to_response('wss/success.html', data, context)
                else :
                    data["message"] = "已支付订单不可删除，如需修改请联系管理员"
                    return render_to_response('wss/warn.html', data, context)
            else:
                data["message"] = "未找到订单信息，请检查您想删除的定单"
                return render_to_response('wss/warn.html', data, context)
        except:
            data["message"] = "删除订单失败，请联系管理员"
            return render_to_response('wss/warn.html', data, context)
    else:
        data["message"] = "未找到订单信息，请检查您想删除的定单"
        return render_to_response('wss/warn.html', data, context)


#支付订单
@OpenidViewRequired
@JSAPI_TICKET_Required
def order_pay_update1(request, order_id):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    wss_tools = DocumentWssTools(request)
    request_tool.check_message(data)
#     client = Client.objects(id='577dede653bc2b145bba28ff').first()
    #client = Client.objects(id='57edf1fc478c927845e9935f').first()
#test
   # client = Client.objects(id='57ac2dd6cba73c50116c647d').first()
    client = Client.objects(user=request.user).first()
    data['client'] = client
    order = Ordering.objects(id=order_id).first()
    data['order'] = order
    if request.method == 'POST':
        try:
            if order.state != 'init':
                request_tool.set_message('支付订单状态错误')
                return HttpResponseRedirect(reverse('wss:order_pay_update', args=[order.id, ]))

            password = request_tool.get_parameter('password', '').strip()
            if password:
                password = hashlib.sha1(password.encode('utf-8')).hexdigest()
                if client.password == password:
                    if order.company.paper_id == settings.ZHONGAN_COMPANY_CODE:
                            if order.product_type == "ticket"or order.product_type == "batch":
                                     if order.client.balance >=order.price:
                                         zhonganapi = ZhongAnApi(request)
                                         response = zhonganapi.applyValidate(order.id)
                                         responseinfo = json.loads(response['bizContent'])
                                         if responseinfo['isSuccess'] == "Y":
                                             order.insurance_id = responseinfo['policyNo']
                                             temp =[]
                                             temp.append(responseinfo['epolicyDownloadlink'])
                                             order.insurance_image_list = temp
                                             order.pay_money()
                                             order.state = "done"
                                             order.save()  
                                             if int(order.client.balance/100)  >= 500:
                                                     content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。"
                                             else:
                                                      content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。预存余额不足500，为了避免余额不足导致无法提交订单，请尽快补充预存！"   
                                             touser = order.client.wx_id
                                             send_wx_message(touser,content)     
                                         else:      
                                             request.session['message'] = responseinfo['failMsg']
                                     else:
                                        request_tool.set_message('金额支付不足')
                            else:
                                  request_tool.set_message('众安保险只承保单票保险')
                    else:             
                            message2=""
                            if order.client.balance >= order.price:
                                order.pay_money()
                                order.save()
                                #2017 添加支付统计
                                try:
                                    if PaymentStatistical.objects(order=order).count()==0:
                                        payment_statistical = PaymentStatistical()
                                    else:
                                        payment_statistical = PaymentStatistical.objects(order=order).first()
                                    payment_statistical.client = order.client
                                    payment_statistical.price = order.price
                                    payment_statistical.order = order
                                    payment_statistical.order_type = order.product_type
                                    payment_statistical.state = 'wx_price'
                                    payment_statistical.save()
                                except Exception as e :
                                    message= '付款成功，网络延迟付款记录保存失败：'+str(e)
                                    request_tool.set_message(message)
                                if int(order.client.balance/100)  >= 500:
                                        content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。"
                                else:
                                         content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。预存余额不足500，为了避免余额不足导致无法提交订单，请尽快补充预存！"   
                                #下载文档
                                if order.company.paper_id == settings.ZHONGAN_COMPANY_CODE:
                                    if order.product_type == "ticket" and order.state == "done":
                                        BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                                        file_name=str(order.id)+'.pdf'
                                        path = BASE_ROOT+"/static/order/doc_file/"+file_name
                                        url=order.insurance_image_list
                                        print(url)
                                        try:  
                                            urllib.request.urlretrieve(url , path) #python2中用的 urllib.urlretrieve(url1 , path)
                                        except Exception as e:
                                            print(str(e))
                                            message2 = "1"
                                 #下载文档结束
                                touser = order.client.wx_id
                                send_wx_message(touser,content)
                                if message2=="1":
                                    request_tool.set_message("支付成功,但由于网络不稳定，保单图片下载失败，可稍后刷新订单详情或联系管理员")
                                else:
                                    request_tool.set_message('支付成功')
                            else:
                                request_tool.set_message('余额不足，预存余额为{0}元，您至少还须预存{1}元，预存成功后请到“我的”--“我的订单”中选择该订单进行支付'.format(order.client.balance/100, (order.price-order.client.balance)/100))
                                return HttpResponseRedirect(reverse('wss:warn'))
                else:
                    request_tool.set_message('密码错误，请重新输入')
                    return HttpResponseRedirect(reverse('wss:order_pay_update', args=[order.id, ]))
            else:
                request_tool.set_message('密码不能为空')
                return HttpResponseRedirect(reverse('wss:order_pay_update', args=[order.id, ]))

        except CustomError as e:
            # request.session['message'] = e.message
            data['message'] = e.message
            return render_to_response('wss/insure/order_pay_update.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            # request.session['message'] = str(e)
            return render_to_response('wss/insure/order_pay_update.html', data, context)
#         #2017 添加支付统计
#         try:
#             if PaymentStatistical.objects(order=order).count()==0:
#                 payment_statistical = PaymentStatistical()
#             else:
#                 payment_statistical = PaymentStatistical.objects(order=order).first()
#             payment_statistical.client = order.client
#             payment_statistical.price = order.price
#             payment_statistical.order = order
#             payment_statistical.order_type = order.product_type
#             payment_statistical.state = 'wx_price'
#             payment_statistical.save()
#         except Exception as e :
#             message= '付款成功，网络延迟付款记录保存失败：'+str(e)
#             request_tool.set_message(message)
        return HttpResponseRedirect(reverse('wss:order_detail_update', args=[order.id, ]))
    elif request.method == 'GET':
        return render_to_response('wss/insure/order_pay_update.html', data, context)
    
    
def get_packs_list(request):
    data = {}
    try:
        order = Ordering()
        pack_method_list=order.PACK_METHOD
        packs_list = []
        i = 1
        for pack_method in pack_method_list:
            firstDict =  getDict(pack_method[0][0],str(i))

            sec = []
            for second in pack_method[1]: 
                  secondDict = getDict(second[1],second[0])
                  sec.append(secondDict)
            firstDict['sub'] = sec
            packs_list.append(firstDict)
            i+=1
        data["packs_list"]=json.dumps(packs_list,ensure_ascii=False,indent=2)
        return JsonResult(data=data, code=CODE_SUCCESS).response()
    except:
        return  JsonResult(data=data, code=CODE_ERROR, message='网络错误，请重新加载').response()
    
def getDict(name,code):
    dict = {}
    dict.setdefault("name",name)
    dict.setdefault("code",code)
    return dict

def get_cargos_list(request):
#     data = {}
#     try:
#         cargoTypeList = CargoType.objects(ct_state=True).order_by("ct_priority")
#         cargos_list = []
#         i = 1
#         for cargoType in cargoTypeList:
#             firstDict =  getDict(cargoType['ct_name'],str(i))
#             sec = []
#             cargos = Cargo.objects(cargo_type=cargoType,state =True)
#             for cargo in cargos: 
#                   secondDict = getDict(cargo['cargo_name'],cargo['cargo_number'])
#                   sec.append(secondDict)
#             firstDict['sub'] = sec
#             cargos_list.append(firstDict)
#             i+=1
#         data["cargos_list"]=json.dumps(cargos_list,ensure_ascii=False,indent=2)
#         return JsonResult(data=data, code=CODE_SUCCESS).response()
#     except:
#         return  JsonResult(data=data, code=CODE_ERROR, message='网络错误，请重新加载').response()
    
    data = {}
    try:
        cargoList = Cargo.objects(state =True).order_by("cargo_priority")
        cargos_list = []
        for cargo in cargoList:
            firstDict = getDict(cargo['cargo_name'],cargo['cargo_number'])
            print(cargo['cargo_name'])
            cargos_list.append(firstDict)
        data["cargos_list"]=json.dumps(cargos_list,ensure_ascii=False,indent=2)
        return JsonResult(data=data, code=CODE_SUCCESS).response()
    except:
        return  JsonResult(data=data, code=CODE_ERROR, message='网络错误，请重新加载').response()



    #删除车次图片
def wx_delete_batch_pic(request, order_id):
    context = RequestContext(request)
    image_url = request.POST.get('image_batch_url_delete', '')
    if image_url:
        try:
            image_tools = ImageTools()
            image_tools.delete(image_url)
            order = Ordering.objects(id=order_id).first()
            order.batch_image_list.remove(image_url)
            order.save()
            request.session['wx_delete_pic'] = "删除图片成功"
        except Exception as e:
            request.session['wx_delete_pic'] = '删除失败：{0}'.format(e)
    else:
        request.session['wx_delete_pic'] = '未找到对应图片'
    return HttpResponseRedirect(reverse('wss:order_edit', args=[order_id, ]))

#车辆保险入口
def auto_insurance(request):
 data = {}
 context = RequestContext(request)

 return render_to_response('wss/insure/auto_insurance.html', data, context)
 
 
 #机动车辆保险页面
@OpenidViewRequired
@JSAPI_TICKET_Required
def insure_enquiry(request):
     data = {}
     context = RequestContext(request)
     request_tool = RequestTools(request)
     request_tool.check_message(data)
#      jdclbx_order = InquiryInfo()

     #client = Client.objects(user=request.user).first()
     try:
         client = Client.objects(user=request.user).first()
         #client = Client.objects(id='574e37d79a8f2b0e2a811ff2').first()
         if client:
             pass
#                 jdclbx_order.client = client
         else:
                data['message'] = '用户不存在'
                return render_to_response('wss/insure/auto_insurance.html', data, context)
     except:
             data['message'] = '用户信息获取失败，请清理缓存后重试'   
             return render_to_response('wss/insure/auto_insurance.html', data, context)

     car_type = request_tool.get_parameter('car_type', '').strip()
     home_city = request_tool.get_parameter('wx_home_city', '').strip()
     short = request_tool.get_parameter('short', '').strip()
     wx_plate_number = request_tool.get_parameter('wx_plate_number', '').strip()
     wx_jiancheng = []
     wx_jiancheng =  short.split(' ')
     intermediary_set= Intermediary.objects()
     intermediary_city = []
     intermediary_car = []
     car_type_list = InquiryInfo.ORDER_CAR_TYPE   #车辆类型
     
     if request.method == 'POST':
         data['posted_data'] = request.POST
         #车辆城市审核
         home_citylist=[]
         if home_city:  
             home_citylist = home_city.split(' ')
             try:
                 cargoshi = CargoArea.objects(name__contains=home_citylist[1])
                 city_code=''
                 if cargoshi:
                      for cargoshiobj in cargoshi:
                          if  cargoshiobj.level =="2":
                              city_code = cargoshiobj.code
                              break         
                 else:
                      data['message'] = '选择城市错误！'
                      return render_to_response('wss/insure/auto_insurance.html', data, context)
                 if not city_code:
                     data['message'] = '未找到对应城市！'
                     return render_to_response('wss/insure/auto_insurance.html', data, context)
             except:
                  data['message'] = '选择城市错误！'
                  return render_to_response('wss/insure/auto_insurance.html', data, context)    
         else:
                data['message'] = '请选择城市！'
                return render_to_response('wss/insure/auto_insurance.html', data, context)
        #车辆类型审核
         if car_type:  
            for car_type_obj in car_type_list:
                  if car_type_obj[1]==car_type:
#                         jdclbx_order.order_car_type = car_type_obj[0]
                        order_car_type = car_type_obj[0]
                        break  
         else: 
            data['message'] = '请选择车辆类型！'
            return render_to_response('wss/insure/auto_insurance.html', data, context)
        #车牌号审核
         short_number = wx_jiancheng[0]
         if  wx_plate_number:
             if re.match(r'^[a-z_A-Z_0-9]{5}$', wx_plate_number):
                wx_plate_number = wx_plate_number.upper()
                plate_number = str(short)+' '+str(wx_plate_number)
                
#                 jdclbx_order.plate_number = str(short)+' '+str(wx_plate_number)
             else:
               data['message'] = '您输入的车牌号不正确，请输入五位由英文或数字组合的字符串'
               return render_to_response('wss/insure/auto_insurance.html', data, context)
         else:
                data['message'] = '请填写车牌号！'
                return render_to_response('wss/insure/auto_insurance.html', data, context)   
        #2017添加验证部分
        #根据车牌号和订单货物大类筛选适合本订单的保险中介渠道
         intermediary_list = Intermediary.objects.filter(state = True, order_car_type__icontains=order_car_type, plate_number_list__icontains=short_number )
         test_count =intermediary_list.count()
         if test_count == 0:
            data['message'] = "暂未开通"+str(car_type) + '车牌号为' + str(short_number)+ '部分投保业务'
            return render_to_response('wss/insure/auto_insurance.html', data, context)
         else:
            intermediary_list_test=[]
            user_set = User.objects(is_active=True)
            for intermediary_detail in intermediary_list:
                try:
                    intermediary_people_count = IntermediaryPeople.objects(intermediary =intermediary_detail , user__in=user_set ).count()
                    if intermediary_people_count>0:
                        intermediary_list_test.append(intermediary_detail)
                except:
                    pass
            if len(intermediary_list_test)<=0:
                data['message'] = "暂未开通"+str(car_type) + '车牌号为' + str(short_number)+ '部分投保业务。'
                return render_to_response('wss/insure/auto_insurance.html', data, context)
         
         try: 
             request.session['city_code'] = city_code#传递所选城市
             request.session['plate_number'] = plate_number#传递车牌号
             request.session['order_car_type'] = order_car_type#传递车辆类型
             return HttpResponseRedirect(reverse('wss:jdclbx_order_create_new', ))
#                 return render_to_response('wss/insure/ai_car_info.html', data, context)
         except Exception as e:
                print(traceback.format_exc())
                data['message'] = str(e)   
                return render_to_response('wss/insure/auto_insurance.html', data, context)  
     else:
        return render_to_response('wss/insure/auto_insurance.html', data, context)
   
 
#车辆信息
# @OpenidViewRequired
# @JSAPI_TICKET_Required
def insure_enquiry_user(request):
 data = {}
 context = RequestContext(request)
 request_tool = RequestTools(request)
 request_tool.check_message(data)
 paper_id = request_tool.get_parameter('paper_id', '').strip()
#  short_number = request_tool.get_parameter('short_number').strip()       #车牌号第一位
#  plate_number = request_tool.get_parameter('plate_number').strip()       #车牌号后五位
#  car_type = request_tool.get_parameter('car_type', '').strip()
#  holder = request_tool.get_parameter('holder', '').strip()
#  use_property = request_tool.get_parameter('use_property', '').strip()
#  brand_digging = request_tool.get_parameter('brand_digging', '').strip()
#  car_number = request_tool.get_parameter('car_number', '').strip()
#  engine_number = request_tool.get_parameter('engine_number', '').strip()
#  issue_date = request_tool.get_parameter('issue_date', '').strip()
#  load_weight = request_tool.get_parameter('load_weight', '').strip()
 national_image = request.FILES.get('national_image', '')   #行驶证正面
 national_image_down = request.FILES.get('national_image_down', None)     #行驶证反面
 jdclbx_order = InquiryInfo.objects(paper_id = paper_id).first()
 data["paper_id"] = jdclbx_order.paper_id   
 if request.method == 'POST':
     #行驶证正面
     if national_image:
                image_tool = ImageTools()
                try:
                    id_card_up_url = image_tool.save(request_file=national_image, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_card_up_url:
                        jdclbx_order.plate_image_left=id_card_up_url
                    else:
                         data['message'] = '行驶证正面图片上传失败！'
                         return render_to_response('wss/insure/ai_car_info.html', data, context)
                except:
                     data['message'] = '保存行驶证正面失败！'
                     return render_to_response('wss/insure/ai_car_info.html', data, context)
     else:
          data['message'] = '请添加驶证正面！'
          return render_to_response('wss/insure/ai_car_info.html', data, context)
     #行驶证背面
     if national_image_down:
                image_tool = ImageTools()
                try:
                    id_card_down_url = image_tool.save(request_file=national_image_down, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_card_down_url:
                        jdclbx_order.plate_image_right=id_card_down_url
                    else:
                        data['message'] = '行驶证背面图片上传失败！'
                        return render_to_response('wss/insure/ai_car_info.html', data, context)
                except:
                     data['message'] = '保存行驶证背面失败！'
                     return render_to_response('wss/insure/ai_car_info.html', data, context)
     else:
          data['message'] = '请添加驶证背面！'
          return render_to_response('wss/insure/ai_car_info.html', data, context)
#      if  national_image and  national_image_down:
#             #车牌号
#         if short_number  and plate_number:
#             if re.match(r'^[a-z_A-Z_0-9]{5}$', plate_number):
#                 plate_number = plate_number.upper()
#                 jdclbx_order.plate_number = short_number + ' ' + plate_number
#             else:
#                  request_tool.set_message('您输入的车牌号不正确，请输入英文或数字！')
#         else:
#             request_tool.set_message('请输入车牌号')
#          #车辆类型
#         if car_type:
#             jdclbx_order.car_type = car_type
#         else:
#             request_tool.set_message('请选择车辆类型')
#         #所有人
#         if holder:
#             jdclbx_order.holder = holder
#         else:
#              request_tool.set_message('请输入所有人')
#         #使用性质
#         if use_property:
#             jdclbx_order.use_property = use_property
#         else:
#             request_tool.set_message('请选择使用性质')
#         #品牌型号
#         if brand_digging:
#             jdclbx_order.brand_digging = brand_digging
#         else:
#              request_tool.set_message('请输入品牌型号')
#         #车辆识别代码
#         if car_number:
#             jdclbx_order.car_number = car_number
#         else:
#             request_tool.set_message('请输入车辆识别代码')
#         #发动机号
#         if engine_number:
#             jdclbx_order.engine_number = engine_number
#         else:
#             request_tool.set_message('请输入发动机号')
#         #注册日期
#         if issue_date:
#             jdclbx_order.issue_date = issue_date
#         else:
#             request_tool.set_message('请输入车辆注册日期')
#      
#         #核载质量(Kg)
#         if load_weight:
#             jdclbx_order.load_weight = load_weight
#         if  not load_weight:
#             request_tool.set_message('请输入核载质量')
     try:
           jdclbx_order.save()  
     except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)                
     
 return render_to_response('wss/insure/ai_user.html', data, context)
 
 #车险投保人和被保人信息
# @OpenidViewRequired
# @JSAPI_TICKET_Required
def enquiry_insure_type(request):
 data = {}
 context = RequestContext(request)
 request_tool = RequestTools(request)
 request_tool.check_message(data)
 paper_id = request_tool.get_parameter('paper_id', '').strip()
 jdclbx_order = InquiryInfo.objects(paper_id = paper_id).first()
 ismatchxsz = request_tool.get_parameter('ismatchxsz', '').strip()#是否与行驶证相同 on
 #录入投保人信息--个人
 user_classify = request_tool.get_parameter('user_classify').strip()       #投保人身份选择
 applicant_name = request_tool.get_parameter('wx_applicant_name').strip()       #投保人姓名
 #certificate_number = request_tool.get_parameter('certificate_number').strip()       #身份证号
 carded_image = request.FILES.get('carded_image', '')   #身份证正面
 carded_image_down = request.FILES.get('carded_image_down', None)     #身份证反面
 applicant_phone = request_tool.get_parameter('applicant_phone').strip()       #投保人手机号
  #录入投保人信息--单位
 applicant_company_name = request_tool.get_parameter('applicant_company_name').strip()       #单位名称
 #organ_number = request_tool.get_parameter('organ_number').strip()       #证件号
 national_image_yingye = request.FILES.get('national_image_yingye', None)     #身份证反面
  #录入投保人信息--被保人
 ismatchtbr = request_tool.get_parameter('ismatchtbr').strip()       #是否与投保人相同
 insured_name = request_tool.get_parameter('insured_name').strip()       #被保人姓名
 insured_phone = request_tool.get_parameter('insured_phone').strip()       #被保人手机号
 policy_address = request_tool.get_parameter('policy_address').strip()       #保单邮寄地址
 detailed_address = request_tool.get_parameter('detailed_address').strip()       #保单邮寄地址
 

 data["paper_id"] = jdclbx_order.paper_id   
 if request.method == 'POST':
     if ismatchxsz == "on":
         if user_classify == "个人":
              jdclbx_order.user_classify ="personal"
              jdclbx_order.applicant_name = "同行驶证"
              #身份证正面
              if carded_image:
                        image_tool = ImageTools()
                        try:
                            id_card_up_url = image_tool.save(request_file=carded_image, file_folder=ImageFolderType.jdclbx, old_file='')
                            if id_card_up_url:
                                jdclbx_order.id_card_up=id_card_up_url
                            else:
                                 data['message'] = '身份证正面图片上传失败！'
                                 return render_to_response('wss/insure/ai_user.html', data, context)
                        except:
                             data['message'] = '保存身份证正面失败！'
                             return render_to_response('wss/insure/ai_user.html', data, context)
              else:
                  data['message'] = '请添加身份证证正面！'
                  return render_to_response('wss/insure/ai_user.html', data, context)
              
              #身份证背面
              if carded_image_down:
                        image_tool = ImageTools()
                        try:
                            id_card_down_url = image_tool.save(request_file=carded_image_down, file_folder=ImageFolderType.jdclbx, old_file='')
                            if id_card_down_url:
                                jdclbx_order.id_card_down=id_card_down_url
                            else:
                                data['message'] = '身份证背面图片上传失败！'
                                return render_to_response('wss/insure/ai_user.html', data, context)
                        except:
                             data['message'] = '保存身份证背面失败！'
                             return render_to_response('wss/insure/ai_user.html', data, context)
              else:
                      data['message'] = '请添加身份证证背面！'
                      return render_to_response('wss/insure/ai_user.html', data, context)
              if applicant_phone:
                  if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', applicant_phone):
                      data['message'] = '请输入正确的投保人手机号'
                      return render_to_response('wss/insure/ai_user.html', data, context)
                  jdclbx_order.applicant_phone = applicant_phone
              else:
                   data['message'] = '投保人手机号不能为空！'
                   return render_to_response('wss/insure/ai_user.html', data, context) 
         elif user_classify == "单位":
             jdclbx_order.user_classify = 'unit'
             jdclbx_order.applicant_company_name = "同行驶证"
              #营业执照
             if national_image_yingye:
                        image_tool = ImageTools()
                        try:
                            id_card_yingye_url = image_tool.save(request_file=national_image_yingye, file_folder=ImageFolderType.jdclbx, old_file='')
                            if id_card_yingye_url:
                                jdclbx_order.business_license_image=id_card_yingye_url
                            else:
                                data['message'] = '证件图片上传失败！'
                                return render_to_response('wss/insure/ai_user.html', data, context)
                        except:
                             data['message'] = '保存证件图片失败！'
                             return render_to_response('wss/insure/ai_user.html', data, context)
             else:
                      data['message'] = '请添加证件图片！'
                      return render_to_response('wss/insure/ai_user.html', data, context)
             if applicant_phone:
                 if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', applicant_phone):
                      data['message'] = '请输入正确的投保人手机号'
                      return render_to_response('wss/insure/ai_user.html', data, context)
                 jdclbx_order.applicant_phone = applicant_phone
             else:
                   data['message'] = '投保人手机号不能为空！'
                   return render_to_response('wss/insure/ai_user.html', data, context) 
     else:
          if user_classify == "个人":
              jdclbx_order.user_classify = 'personal'
              if applicant_name:
                     jdclbx_order.applicant_name = applicant_name
              else:
                     data['message'] = '投保人姓名不能为空！'
                     return render_to_response('wss/insure/ai_user.html', data, context) 
              #身份证正面
              if carded_image:
                        image_tool = ImageTools()
                        try:
                            id_card_up_url = image_tool.save(request_file=carded_image, file_folder=ImageFolderType.jdclbx, old_file='')
                            if id_card_up_url:
                                jdclbx_order.id_card_up=id_card_up_url
                            else:
                                 data['message'] = '身份证正面图片上传失败！'
                                 return render_to_response('wss/insure/ai_user.html', data, context)
                        except:
                             data['message'] = '保存身份证正面失败！'
                             return render_to_response('wss/insure/ai_user.html', data, context)
              else:
                  data['message'] = '请添加身份证证正面！'
                  return render_to_response('wss/insure/ai_user.html', data, context)
              
              #身份证背面
              if carded_image_down:
                        image_tool = ImageTools()
                        try:
                            id_card_down_url = image_tool.save(request_file=carded_image_down, file_folder=ImageFolderType.jdclbx, old_file='')
                            if id_card_down_url:
                                jdclbx_order.id_card_down=id_card_down_url
                            else:
                                data['message'] = '身份证背面图片上传失败！'
                                return render_to_response('wss/insure/ai_user.html', data, context)
                        except:
                             data['message'] = '保存身份证背面失败！'
                             return render_to_response('wss/insure/ai_user.html', data, context)
              else:
                      data['message'] = '请添加身份证证背面！'
                      return render_to_response('wss/insure/ai_user.html', data, context)
              if applicant_phone:
                  if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', applicant_phone):
                      data['message'] = '请输入正确的投保人手机号'
                      return render_to_response('wss/insure/ai_user.html', data, context)
                  jdclbx_order.applicant_phone = applicant_phone
              else:
                   data['message'] = '投保人手机号不能为空！'
                   return render_to_response('wss/insure/ai_user.html', data, context) 
          elif user_classify == "单位":
             jdclbx_order.user_classify = 'unit'
             if applicant_company_name:
                 jdclbx_order.applicant_company_name = applicant_company_name
             else:
                 data['message'] = '公司名称不能为空！'
                 return render_to_response('wss/insure/ai_user.html', data, context) 
              #营业执照
             if national_image_yingye:
                        image_tool = ImageTools()
                        try:
                            id_card_yingye_url = image_tool.save(request_file=national_image_yingye, file_folder=ImageFolderType.jdclbx, old_file='')
                            if id_card_yingye_url:
                                jdclbx_order.business_license_image=id_card_yingye_url
                            else:
                                data['message'] = '证件图片上传失败！'
                                return render_to_response('wss/insure/ai_user.html', data, context)
                        except:
                             data['message'] = '保存证件图片失败！'
                             return render_to_response('wss/insure/ai_user.html', data, context)
             else:
                      data['message'] = '请添加证件图片！'
                      return render_to_response('wss/insure/ai_user.html', data, context)
             if applicant_phone:
                 if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', applicant_phone):
                      data['message'] = '请输入正确的投保人手机号'
                      return render_to_response('wss/insure/ai_user.html', data, context)
                 jdclbx_order.applicant_phone = applicant_phone
             else:
                   data['message'] = '投保人手机号不能为空！'
                   return render_to_response('wss/insure/ai_user.html', data, context) 
     if ismatchtbr == "on":
             jdclbx_order.insured_name =  "同投保人姓名"
             jdclbx_order.insured_phone = applicant_phone
             if policy_address:
                  jdclbx_order.mail_address = policy_address
             else:
                 data['message'] = '邮寄地址不能为空！'
                 return render_to_response('wss/insure/ai_user.html', data, context)     
             if detailed_address:
                      jdclbx_order.policy_address = detailed_address
             else:
                    data['message'] = '详细地址不能为空！'
                    return render_to_response('wss/insure/ai_user.html', data, context) 
            
     else:
         if insured_name:
             jdclbx_order.insured_name = insured_name
         else:
             data['message'] = '被保人姓名不能为空！'
             return render_to_response('wss/insure/ai_user.html', data, context) 
         if insured_phone:
             if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', insured_phone):
                      data['message'] = '请输入正确的被保人手机号'
                      return render_to_response('wss/insure/ai_user.html', data, context)
             jdclbx_order.insured_phone = insured_phone
         else:
             data['message'] = '被保人电话不能为空！'
             return render_to_response('wss/insure/ai_user.html', data, context) 
         if policy_address:
                  jdclbx_order.mail_address = policy_address
         else:
                 data['message'] = '邮寄地址不能为空！'
                 return render_to_response('wss/insure/ai_user.html', data, context)     
         if detailed_address:
                      jdclbx_order.policy_address = detailed_address
         else:
                    data['message'] = '详细地址不能为空！'
                    return render_to_response('wss/insure/ai_user.html', data, context) 
     try:
           jdclbx_order.save()  
     except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)    
            return render_to_response('wss/insure/ai_user.html', data, context)             
     data["paper_id"] = jdclbx_order.paper_id      
 return render_to_response('wss/insure/ai_insurance_type.html', data, context) 
 
 #选择险种
# @OpenidViewRequired
# @JSAPI_TICKET_Required
def insurance_period(request):
 
    data = {}
    context = RequestContext(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    paper_id = request_tool.get_parameter('paper_id', '').strip()

    liability_state = request_tool.get_parameter('liability_state').strip()       #交强险
    vehicle_vessel_tax_state = request_tool.get_parameter('vehicle_vessel_tax_state').strip()       #车船税
    third_insurance = request_tool.get_parameter('third_insurance').strip()       #三者险
    damage_insurance = request_tool.get_parameter('damage_insurance').strip()       #车损险
    glass_insurance = request_tool.get_parameter('glass_insurance').strip()       #玻璃险
    driver_insurance = request_tool.get_parameter('driver_insurance').strip()       #司机险
    theft_insurance = request_tool.get_parameter('theft_insurance').strip()       #盗抢险
    passenger_insurance = request_tool.get_parameter('passenger_insurance').strip()       #乘客险
    iop_insurance = request_tool.get_parameter('iop_insurance').strip()       #不计免赔险
    autoignition_insurance = request_tool.get_parameter('autoignition_insurance').strip()       #自燃损失
    wading_insurance = request_tool.get_parameter('wading_insurance').strip()       #涉水险
    scratch_insurance = request_tool.get_parameter('scratch_insurance').strip()       #划痕险
    try:
        jdclbx_order = InquiryInfo.objects(paper_id = paper_id).first()
        if not jdclbx_order:
            data['message'] = '网络延迟，未获取到订单信息，请稍后再试。'
            return render_to_response('wss/insure/ai_insurance_type.html', data, context)
    except:
        data['message'] = '网络延迟，未获取到订单信息，请稍后再试'
        return render_to_response('wss/insure/ai_insurance_type.html', data, context)
    if request.method == 'POST':
             data['posted_data'] = request.POST
             #交强险
             if liability_state=="on":
                      jdclbx_order.liability_state = True
                      data['liability_state'] = '1'
             else:
                      jdclbx_order.liability_state = False
              #车船税
             if vehicle_vessel_tax_state=="on":
                     jdclbx_order.vehicle_vessel_tax_state = True
             else:
                     jdclbx_order.vehicle_vessel_tax_state = False
  
             if third_insurance == "不投保":
                      jdclbx_order.third_insurance = 0
             else:
                      jdclbx_order.third_insurance  = int(third_insurance.rstrip("万"))*10000
                      data['shangye_state'] = '1'
              #车损险
             if damage_insurance=="on":
                     jdclbx_order.damage_insurance = True
                     data['shangye_state'] = '1'
             else:
                     jdclbx_order.damage_insurance = False
             #玻璃险
             if glass_insurance== "不投保":
                     jdclbx_order.glass_insurance = "no"    
             elif glass_insurance== "进口":
                   jdclbx_order.glass_insurance = "import" 
                   data['shangye_state'] = '1'   
             elif  glass_insurance== "国产":
                   jdclbx_order.glass_insurance = "china"  
                   data['shangye_state'] = '1'  
             #司机险
             if driver_insurance == "不投保":
                    jdclbx_order.driver_insurance= 0
             else:
                    jdclbx_order.driver_insurance=  int(driver_insurance.rstrip("万"))*10000
                    data['shangye_state'] = '1'
             #盗抢险
             if theft_insurance=="on":
                   jdclbx_order.theft_insurance = True
                   data['shangye_state'] = '1'
             else:
                   jdclbx_order.theft_insurance = False
              #乘客险
             if passenger_insurance == "不投保":
                     jdclbx_order.passenger_insurance = 0
             else:
                     jdclbx_order.passenger_insurance = int(passenger_insurance.rstrip("万"))*10000
                     data['shangye_state'] = '1'
             #不计免赔险
             if iop_insurance=="on":
                    jdclbx_order.iop_insurance = True
                    data['shangye_state'] = '1'
             else:
                    jdclbx_order.iop_insurance = False
             #自燃损失
             if autoignition_insurance=="on":
                jdclbx_order.autoignition_insurance = True
                data['shangye_state'] = '1'
             else:
                jdclbx_order.autoignition_insurance = False
             #涉水险
             if wading_insurance=="on":
                    jdclbx_order.wading_insurance = True
                    data['shangye_state'] = '1'
             else:
                jdclbx_order.wading_insurance = False
             #划痕险
             if scratch_insurance  == "不投保":
                  jdclbx_order.scratch_insurance = 0
             elif scratch_insurance  == "2千":
                  jdclbx_order.scratch_insurance = 2000
                  data['shangye_state'] = '1'
             elif scratch_insurance  == "5千":
                  jdclbx_order.scratch_insurance = 5000
                  data['shangye_state'] = '1'
             elif scratch_insurance  == "1万":
                  jdclbx_order.scratch_insurance = 10000
                  data['shangye_state'] = '1'
             elif scratch_insurance  == "2万":
                  jdclbx_order.scratch_insurance = 20000
                  data['shangye_state'] = '1'
    if not liability_state and not vehicle_vessel_tax_state and third_insurance == "不投保" and not damage_insurance and glass_insurance== "不投保" and driver_insurance == "不投保" and not theft_insurance and passenger_insurance == "不投保"  and not iop_insurance and not autoignition_insurance and not wading_insurance and  scratch_insurance  == "不投保":
              data['message'] = '商业险和交强险请选择一种'
              return render_to_response('wss/insure/ai_insurance_type.html', data, context) 
    try:
           jdclbx_order.save()  
    except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)                
    data["paper_id"] = jdclbx_order.paper_id                      
    return render_to_response('wss/insure/insurance_period.html', data, context) 


#车险保险起期
# @OpenidViewRequired
# @JSAPI_TICKET_Required
def start_inquiry(request):
 data = {}
 context = RequestContext(request)
 request_tool = RequestTools(request)
 request_tool.check_message(data)
 paper_id = request_tool.get_parameter('paper_id', '').strip()
 data["paper_id"] = paper_id
 shangye_state = request_tool.get_parameter('shangye_state', '').strip()#是否选择了商业险
 data["shangye_state"] = shangye_state
 liability_state_on = request_tool.get_parameter('liability_state_on', '').strip()  #是否选择了交强险
 data["liability_state"] = liability_state_on
 shangye_pic_list=[]
 business_license_list = []
 id_card_list = []
 try:
     jdclbx_order = InquiryInfo.objects(paper_id = paper_id).first()
     if not jdclbx_order:
         data['message'] = '网络不稳定，未获取当前订单信息。'
         return render_to_response('wss/insure/insurance_period.html', data, context) 
 except:
     data['message'] = '网络不稳定，未获取当前订单信息'
     return render_to_response('wss/insure/insurance_period.html', data, context) 
 if request.method == 'POST':
    data['posted_data'] = request.POST
 
 if liability_state_on == "1":
         liability_expectStartTime = request_tool.get_parameter('liability_expectStartTime').strip()       #交强险保险起期
       
         if liability_expectStartTime:
             now = datetime.now()
             otherStyleTime = now.strftime("%Y-%m-%d ")
             if otherStyleTime > liability_expectStartTime:
                data['message'] ='交强险保险起期不能早于当前时间'
                return render_to_response('wss/insure/insurance_period.html', data, context)
             data['liability_state'] = '1'
             jdclbx_order.liability_expectStartTime = liability_expectStartTime
         else:
                 data['message'] = '交强险保险起期不能为空！'
                 return render_to_response('wss/insure/insurance_period.html', data, context)
                # return render_to_response('wss/insure/insurance_period.html', data, context) 
 if shangye_state == "1":
         commercial_expectStartTime = request_tool.get_parameter('commercial_expectStartTime').strip()       #商业险保险起期
        
         if commercial_expectStartTime:
             now = datetime.now()
             otherStyleTime = now.strftime("%Y-%m-%d ")
             if otherStyleTime > commercial_expectStartTime:
                data['message'] ='商业险保险起期不能早于当前时间'
                return render_to_response('wss/insure/insurance_period.html', data, context)
             data['shangye_state'] = '1'
             jdclbx_order.commercial_expectStartTime = commercial_expectStartTime
         else:
                 data['message'] = '商业险保险起期不能为空！'
                 return render_to_response('wss/insure/insurance_period.html', data, context)
                 #return render_to_response('wss/insure/insurance_period.html', data, context) 
 try:
           jdclbx_order.save()  
 except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)  
 if  jdclbx_order.business_license_image: 
        business_license_imaga = '/static/'+ jdclbx_order.business_license_image
        business_license_list.append(business_license_imaga)
        data['id_card_list'] = business_license_list  
 if  jdclbx_order.id_card_up and  jdclbx_order.id_card_down:
       id_card_up= '/static/'+jdclbx_order.id_card_up
       id_card_down =  '/static/'+jdclbx_order.id_card_down
       id_card_list.append(id_card_up)
       id_card_list.append(id_card_down)
       data['id_card_list'] = id_card_list   
 data['order'] = jdclbx_order   

 return render_to_response('wss/insure/jdclbx_order_detail.html', data, context) 

#车险订单详情
@OpenidViewRequired
@JSAPI_TICKET_Required
def  jdclbx_detail(request , order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    order_id=order_id
    shangye_pic_list = []
    jiaoqiang_pic_list = []
    #添加动态获取返回列表地址
    history_url=''
    try:
        host = request.get_host()
        history_url="http://"+host+"/wss/mine/my_order/"
    except:
        pass
    data["history_url"] =history_url
    if not order_id:
        data["message"] = "未获取订单编码，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        jdclbx_order = InquiryInfo.objects(id=order_id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
    if jdclbx_order.state =='wait':
#          intermediaryPrice = IntermediaryPrice.objects(order=jdclbx_order)
         #2017添加筛选部分
         try:
             intermediaryPrice=[]
             intermediary_price_list=IntermediaryPrice.objects(order=jdclbx_order).order_by('order_price_add_profit')
             if intermediary_price_list.count()>0:
                 company_list=[]
                 for intermediary_price in intermediary_price_list:
                     if intermediary_price.company not in company_list:
                         company_list.append(intermediary_price.company)
                         intermediaryPrice.append(intermediary_price)  
         except:
             data["message"] = "网络不稳定，查找报价公司失败"
             return render_to_response('wss/warn.html', data, context)
         
         data['intermediaryPrice'] = intermediaryPrice  
         data['count'] = len(intermediaryPrice)
         return render_to_response('wss/insure/insurance_list.html', data, context) #询价后的保险列表
    if jdclbx_order.state =='done':
        if jdclbx_order.commercial_image_list:
              for  shangye in jdclbx_order.commercial_image_list:
                       shangye_pic = '/static/'+shangye
                       shangye_pic_list.append(shangye_pic)
              data['shangye_pic_list'] = shangye_pic_list  
              data['id_card_list'] = shangye_pic_list  
        else:
            data['shangye_pic_list'] = jdclbx_order.liability_image_list
        if jdclbx_order.liability_image_list:
              for  jiaoqiang in jdclbx_order.liability_image_list:
                     jiaoqiang_pic = '/static/'+jiaoqiang
                     jiaoqiang_pic_list.append(jiaoqiang_pic)
              data['jiaoqiang_pic_list'] = jiaoqiang_pic_list     
              data['id_card_list'] = jiaoqiang_pic_list         
        else:
             data['jiaoqiang_pic_list'] = jdclbx_order.commercial_image_list       
    #解决微信页面bug
    jdclbx_intermediary=''
    data['discount_price'] = ''
    if jdclbx_order.state =='done' or jdclbx_order.state =='init' or jdclbx_order.state =='paid' :
        try:
            jdclbx_intermediary = IntermediaryPrice.objects(order=jdclbx_order,company=jdclbx_order.company,insurance_intermediary=jdclbx_order.insurance_intermediary).first()
            #优惠金额
            data['discount_price'] =jdclbx_intermediary.order_price_all - jdclbx_intermediary.order_price_add_profit 
        except Exception as e:
            data["message"] = str(e)
            return render_to_response('wss/warn.html', data, context)
    data['intermediary'] = jdclbx_intermediary                     
    data['order'] = jdclbx_order   
    return render_to_response('wss/insure/car_insurance_detail.html', data, context) 


#车险询价列表详情
@OpenidViewRequired
@JSAPI_TICKET_Required
def  jdclbx_intermediary_detail(request , intermediary_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    intermediary_id=intermediary_id
    business_license_list =[]
    id_card_list = []
    if not intermediary_id:
        data["message"] = "未获取订单编码，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        jdclbx_intermediary = IntermediaryPrice.objects(id=intermediary_id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
    if  jdclbx_intermediary.order.business_license_image: 
                business_license_imaga = '/static/'+ jdclbx_intermediary.order.business_license_image
                business_license_list.append(business_license_imaga)
                data['id_card_list'] = business_license_list  
                data['jiaoqiang_pic_list'] = business_license_list   
                data['shangye_pic_list'] = business_license_list
    if  jdclbx_intermediary.order.id_card_up and  jdclbx_intermediary.order.id_card_down:
               id_card_up= '/static/'+jdclbx_intermediary.order.id_card_up
               id_card_down =  '/static/'+jdclbx_intermediary.order.id_card_down
               id_card_list.append(id_card_up)
               id_card_list.append(id_card_down)
               data['id_card_list'] = id_card_list   
               data['jiaoqiang_pic_list'] = id_card_list   
               data['shangye_pic_list'] = id_card_list
    data['order'] = jdclbx_intermediary.order   
    data['intermediary'] = jdclbx_intermediary   
    #2017添加页面计算
    if jdclbx_intermediary.order.state == 'wait' or jdclbx_intermediary.order.state == 'init' or  jdclbx_intermediary.order.state == 'paid' or  jdclbx_intermediary.order.state == 'done' :
        intermediary=jdclbx_intermediary
        if intermediary.intermediary_profit_point>intermediary.liability_process_price:
            data['liability_price'] = round((intermediary.liability_price*(1-intermediary.liability_process_price/100)  +intermediary.liability_price*intermediary.liability_process_price/100)/100,4)
        else:
            data['liability_price'] = round((intermediary.liability_price*(1-intermediary.liability_process_price/100)  +intermediary.liability_price*intermediary.intermediary_profit_point/100)/100,4)
        data['vessel_price'] = round((intermediary.vehicle_vessel_price/100),4)
        #商业险
        commercial_process_price1=intermediary.commercial_process_price#手续费比例
        if intermediary.intermediary_profit_point>commercial_process_price1:
            intermediary_profit_point1=commercial_process_price1
        else:
            intermediary_profit_point1 =intermediary.intermediary_profit_point#利润点
        data['third_insurance_price'] = round((intermediary.third_insurance_price*(1-commercial_process_price1/100)  +intermediary.third_insurance_price*intermediary_profit_point1/100)/100,4)
        data['damage_insurance_price'] = round((intermediary.damage_insurance_price*(1-commercial_process_price1/100)  +intermediary.damage_insurance_price*intermediary_profit_point1/100)/100,4)
        data['glass_insurance_price'] = round((intermediary.glass_insurance_price*(1-commercial_process_price1/100)  +intermediary.glass_insurance_price*intermediary_profit_point1/100)/100,4)
        data['driver_insurance_price'] = round((intermediary.driver_insurance_price*(1-commercial_process_price1/100)  +intermediary.driver_insurance_price*intermediary_profit_point1/100)/100,4)
        data['passenger_insurance_price'] = round((intermediary.passenger_insurance_price*(1-commercial_process_price1/100)  +intermediary.passenger_insurance_price*intermediary_profit_point1/100)/100,4)
        data['theft_insurance_price'] = round((intermediary.theft_insurance_price*(1-commercial_process_price1/100)  +intermediary.theft_insurance_price*intermediary_profit_point1/100)/100,4)
        data['iop_insurance_price'] = round((intermediary.iop_insurance_price*(1-commercial_process_price1/100)  +intermediary.iop_insurance_price*intermediary_profit_point1/100)/100,4)
        data['autoignition_insurance_price'] = round((intermediary.autoignition_insurance_price*(1-commercial_process_price1/100)  +intermediary.autoignition_insurance_price*intermediary_profit_point1/100)/100,4)
        data['wading_insurance_price'] = round((intermediary.wading_insurance_price*(1-commercial_process_price1/100)  +intermediary.wading_insurance_price*intermediary_profit_point1/100)/100,4)
        data['scratch_insurance_price'] = round((intermediary.scratch_insurance_price*(1-commercial_process_price1/100)  +intermediary.scratch_insurance_price*intermediary_profit_point1/100)/100,4)
        #优惠金额
        data['discount_price'] =intermediary.order_price_all - intermediary.order_price_add_profit 
        
        
    return render_to_response('wss/insure/car_insurance_detail.html', data, context) 

#车险确认投保
@OpenidViewRequired
@JSAPI_TICKET_Required
def  jdclbx_confirm_insurance(request , intermediary_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)

    client = Client.objects(user=request.user).first()
    #client = Client.objects(id='574e37d79a8f2b0e2a811ff2').first()
   # client = Client.objects(id='58105ffbcba73c19dc4b4b59').first()

    data['client'] = client
    intermediary_id=intermediary_id
    business_license_list = []
    id_card_list =[]
    if not intermediary_id:
        data["message"] = "未获取订单编码，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        jdclbx_intermediary = IntermediaryPrice.objects(id=intermediary_id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
    try:
        jdclbx_order = InquiryInfo.objects(id=jdclbx_intermediary.order.id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
    if jdclbx_intermediary:
         jdclbx_order.company = jdclbx_intermediary.company
         geng =  jdclbx_intermediary.company.name
         jdclbx_order.insurance_intermediary = jdclbx_intermediary.insurance_intermediary
         jdclbx_order.price = jdclbx_intermediary.order_price_add_profit
         jdclbx_order.intermediary_price = jdclbx_intermediary.order_price_no_process
         jdclbx_order.state = 'init'
    try:
           jdclbx_order.save() 
           data['order'] = jdclbx_order
    except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)   
            return render_to_response('wss/warn.html', data, context)                
    return HttpResponseRedirect(reverse('wss:jdclbx_detail', args=[jdclbx_order.id, ]))
#     if request.method == 'POST': 
#         return HttpResponseRedirect(reverse('wss:jdclbx_detail', args=[jdclbx_order.id, ]))
#           if jdclbx_order.client.balance < jdclbx_order.price:
#              data["message"] = "用户余额不足，请先充值"
#              return render_to_response('wss/warn.html', data, context)
#           else:
#               jdclbx_order.pay_money()
#               jdclbx_order.save() 
#               request_tool.set_message('支付成功')
#               data['order'] = jdclbx_order
#               
#               return render_to_response('wss/insure/car_insurance_detail.html', data, context)
#     elif request.method == 'GET':
        
#         if  jdclbx_order.business_license_image: 
#                     business_license_imaga = '/static/'+ jdclbx_order.business_license_image
#                     business_license_list.append(business_license_imaga)
#                     data['id_card_list'] = business_license_list  
#                     data['shangye_pic_list'] = business_license_list   
#                     data['jiaoqiang_pic_list'] = business_license_list   
#         if  jdclbx_order.id_card_up and  jdclbx_order.id_card_down:
#                        id_card_up= '/static/'+jdclbx_order.id_card_up
#                        id_card_down =  '/static/'+jdclbx_order.id_card_down
#                        id_card_list.append(id_card_up)
#                        id_card_list.append(id_card_down)
#                        data['id_card_list'] = id_card_list   
#                        data['shangye_pic_list'] = id_card_list   
#                        data['jiaoqiang_pic_list'] = id_card_list   
#         return render_to_response('wss/insure/car_insurance_detail.html', data, context)

 
#确认支付(暂时不需要了)
# @OpenidViewRequired
# @JSAPI_TICKET_Required
def  jdclbx_confirm_pay(request , order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    #client = Client.objects(id='58105ffbcba73c19dc4b4b59').first()
    client = Client.objects(user=request.user).first()
    data['client'] = client
    jdclbx_order = InquiryInfo.objects(id=order_id).first()
    data['order'] = jdclbx_order
    if request.method == 'POST':
        try:
            if jdclbx_order.state != 'init':
                request_tool.set_message('支付订单状态错误')
                return HttpResponseRedirect(reverse('wss:jdclbx_confirm_pay', args=[order.id, ]))

            password = request_tool.get_parameter('password', '').strip()
            if password:
                password = hashlib.sha1(password.encode('utf-8')).hexdigest()
                if client.password == password:
                       if jdclbx_order.client.balance < jdclbx_order.price:
                                 data["message"] = "用户余额不足，请先充值"
                                 return render_to_response('wss/insure/jdclbx_pay.html', data, context)
                       else:
                                  jdclbx_order.pay_money()
                                  jdclbx_order.save() 
                                  request_tool.set_message('支付成功')
                                  data['order'] = jdclbx_order
                                  return render_to_response('wss/insure/car_insurance_detail.html', data, context)
                else:
                      data['message'] = "密码错误"
                      return render_to_response('wss/insure/jdclbx_pay.html', data, context)
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('wss/insure/jdclbx_pay.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('wss/insure/jdclbx_pay.html', data, context)
    elif request.method == 'GET':
           return render_to_response('wss/insure/jdclbx_pay.html', data, context)

#编辑订单基本信息
# @OpenidViewRequired
# @JSAPI_TICKET_Required
def jdclbx_baseinfo_edit(request , order_id ):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    wss_tools = DocumentWssTools(request)
    plate_number = []
    if not order_id:
        data["message"] = "未获取订单编码，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        jdclbx_order = InquiryInfo.objects(id=order_id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
#     try:
    if jdclbx_order:
        data['order'] = jdclbx_order   
        plate_number=jdclbx_order.plate_number.split(' ')      
        data['short'] = plate_number[0]+" "+plate_number[1]
        data['wx_plate_number'] = plate_number[2]        
        if request.method == 'GET': 
            
      
#              shengcode = jdclbx_order.city.code[0:2]
#              cargoshen = CargoArea.objects(code=shengcode,level ='1').first()
#              geng = cargoshen.name+' '+ jdclbx_order.city.name
#        
#              data['city'] = cargoshen.name+' '+ jdclbx_order.city.name
             
             return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)
        else:
             chongxinxunjia_state = request_tool.get_parameter('chongxinxunjia_state', '').strip()
             short = request_tool.get_parameter('short', '').strip()
             wx_plate_number = request_tool.get_parameter('wx_plate_number', '').strip()
            # home_city = request_tool.get_parameter('wx_home_city', '').strip()
             car_type = request_tool.get_parameter('wx_car_type', '').strip()
              #录入投保人信息--个人
             user_classify = request_tool.get_parameter('wx_user_classify').strip()       #投保人身份选择
             applicant_name = request_tool.get_parameter('wx_applicant_name').strip()       #投保人姓名
             #certificate_number = request_tool.get_parameter('wx_certificate_number').strip()       #身份证号
             applicant_phone = request_tool.get_parameter('wx_applicant_phone').strip()       #投保人手机号
              #录入投保人信息--单位
             applicant_company_name = request_tool.get_parameter('applicant_company_name').strip()       #单位名称
             #organ_number = request_tool.get_parameter('wx_organ_number').strip()       #证件号
              
              #录入投保人信息--被保人
             insured_name = request_tool.get_parameter('wx_insured_name').strip()       #被保人姓名
             insured_phone = request_tool.get_parameter('wx_insured_phone').strip()       #被保人手机号
             wx_mail_address = request_tool.get_parameter('wx_mail_address').strip()       #保单邮寄地址
             wx_policy_address = request_tool.get_parameter('wx_policy_address').strip()       #保详细地址
             national_image = request.FILES.get('national_image', '')   #行驶证正面
             national_image_down = request.FILES.get('national_image_down', None)     #行驶证反面
             card_up = request.FILES.get('card_up', '')   #身份证正面
             card_down = request.FILES.get('card_down', None)     #身份证反面
             license_image = request.FILES.get('license_image', '')   #营业执照照片
           
              
             car_type_list = InquiryInfo.ORDER_CAR_TYPE                 #车辆类型
#              home_citylist=[]
#              if home_city:  
#                     home_citylist = home_city.split(' ')
#                     count = len(home_citylist)
#                     if  count ==1:
#                           cargoshi = CargoArea.objects(name__contains=home_citylist[0])
#                     elif count ==2:
#                           cargoshi = CargoArea.objects(name__contains=home_citylist[1])
#                     if cargoshi:
#                            for cargoshiobj in cargoshi:
#                                if  cargoshiobj.level =="2":
#                                    jdclbx_order.city = cargoshiobj
#                                    break         
#                     else:
#                            data['message'] = '选择城市错误！'
#                            return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)
#              else:
#                  data['message'] = '请选择城市！'
#                  return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)
             wx_jiancheng = []
             wx_jiancheng =  short.split(' ')
             intermediary_set= Intermediary.objects()
             intermediary_city = []
             intermediary_car = []
             
             for intermediaryobj in intermediary_set:
                    if wx_jiancheng[0] in intermediaryobj.plate_number_list:
                        
                                   intermediary_city.append(intermediaryobj)
                                 
             if intermediary_city:
                       if car_type:  
                                    for car_type_obj in car_type_list:
                                          if car_type_obj[1]==car_type:
                                                jdclbx_order.order_car_type = car_type_obj[0]
                                                break    
                                    for intermediary_city_obj in  intermediary_city:
                                           if  jdclbx_order.order_car_type in intermediary_city_obj.order_car_type:
                                                  intermediary_car.append(intermediary_city_obj)
                       else:
                                        data['message'] = '请选择车辆类型！'
                                        return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)
             else:
                  data['message'] = '车牌所在城市暂时不可保！'
                  return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
                                 
             if intermediary_car:
                  if  wx_plate_number:
                         jdclbx_order.plate_number = str(short)+' '+str(wx_plate_number)
                  else:
                          data['message'] = '请填写车牌号！'
                          return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)               
                  
             else:
                  data['message'] = '暂时没有可保的车辆类型！'
                  return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)        
             
             if user_classify == "个人":
                      jdclbx_order.user_classify = 'personal'
                      jdclbx_order.business_license_image = ""
                      if applicant_name:
                             jdclbx_order.applicant_name = applicant_name
                      else:
                             data['message'] = '投保人姓名不能为空！'
                             return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
#                       if certificate_number:
#                              jdclbx_order.certificate_number = certificate_number
#                       else:
#                            data['message'] = '投保人身份证不能为空！'
#                            return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
                      if applicant_phone:
                          jdclbx_order.applicant_phone = applicant_phone
                      else:
                           data['message'] = '投保人手机号不能为空！'
                           return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
             elif user_classify == "单位":
                     jdclbx_order.user_classify = 'unit'
                     jdclbx_order.id_card_up = ""
                     jdclbx_order.id_card_down = ""
                     if applicant_company_name:
                         jdclbx_order.applicant_company_name = applicant_company_name
                     else:
                         data['message'] = '公司名称不能为空！'
                         return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
#                      if organ_number:
#                              jdclbx_order.organ = organ_number
#                      else:
#                            data['message'] = '单位证件号不能为空！'
#                            return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
                     if applicant_phone:
                          jdclbx_order.applicant_phone = applicant_phone
                     else:
                           data['message'] = '投保人手机号不能为空！'
                           return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)   
                     if applicant_phone:
                          jdclbx_order.applicant_phone = applicant_phone
                     else:
                           data['message'] = '投保人手机号不能为空！'
                           return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)   
             if wx_mail_address:
                      jdclbx_order.mail_address = wx_mail_address
             else:
                    data['message'] = '邮寄地址不能为空！'
                    return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
             if wx_policy_address:
                      jdclbx_order.policy_address = wx_policy_address
             else:
                    data['message'] = '详细地址不能为空！'
                    return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
              
              #身份证正面更新
             if card_up:
                image_tool = ImageTools()
                try:
                    id_card_up_url = image_tool.save(request_file=card_up, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_card_up_url:
                        jdclbx_order.id_card_up=id_card_up_url
                        jdclbx_order.certificate_number = ""
     
                    else:
                         data['message'] = '身份证正面图片上传失败！'
                         return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)
                except:
                     data['message'] = '更新身份证正面失败！'
                     return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
              #身份证背面更新
             if card_down:
                image_tool = ImageTools()
                try:
                    id_card_down_url = image_tool.save(request_file=card_down, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_card_down_url:
                        jdclbx_order.id_card_down=id_card_down_url
                        jdclbx_order.certificate_number = ""
                   
                    else:
                         data['message'] = '身份证背面图片上传失败！'
                         return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)
                except:
                     data['message'] = '更新身份证背面失败！'
                     return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
              
              #营业执照更新
             if license_image:
                image_tool = ImageTools()
                try:
                    id_license_image_url = image_tool.save(request_file=license_image, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_license_image_url:
                        jdclbx_order.business_license_image=id_license_image_url
                        jdclbx_order.organ = ""
                    else:
                         data['message'] = '营业执照图片上传失败！'
                         return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)
                except:
                     data['message'] = '更新营业执照失败！'
                     return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
              #行驶证正更新面
             if national_image:
                image_tool = ImageTools()
                try:
                    id_card_up_url = image_tool.save(request_file=national_image, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_card_up_url:
                        jdclbx_order.plate_image_left=id_card_up_url
                        jdclbx_order.holder = ""
                        jdclbx_order.use_property = ""
                        jdclbx_order.brand_digging = "" 
                        jdclbx_order.car_number = ""
                        jdclbx_order.engine_number = ""
                        jdclbx_order.issue_date = ""
                        jdclbx_order.people_number = ""
                        jdclbx_order.load_weight = ""
                    else:
                         data['message'] = '行驶证正面图片上传失败！'
                         return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)
                except:
                     data['message'] = '更新行驶证正面失败！'
                     return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)

             #行驶证背面更新
             if national_image_down:
                        image_tool = ImageTools()
                        try:
                            id_card_down_url = image_tool.save(request_file=national_image_down, file_folder=ImageFolderType.jdclbx, old_file='')
                            if id_card_down_url:
                                jdclbx_order.plate_image_right=id_card_down_url
                                jdclbx_order.holder = ""
                                jdclbx_order.use_property = ""
                                jdclbx_order.brand_digging = "" 
                                jdclbx_order.car_number = ""
                                jdclbx_order.engine_number = ""
                                jdclbx_order.issue_date = ""
                                jdclbx_order.people_number = ""
                                jdclbx_order.load_weight = ""
                            else:
                                data['message'] = '行驶证背面图片上传失败！'
                                return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)
                        except:
                             data['message'] = '更新行驶证背面失败！'
                             return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)             
             try:
                   jdclbx_order.save()  
             except Exception as e:
                   print(traceback.format_exc())
                   data['message'] = str(e)     
             data['order'] = jdclbx_order       
             data['chongxinxunjia_state'] = chongxinxunjia_state  
             return render_to_response('wss/insure/jdclbx_edit_list.html', data, context)    
    else:
       data["message"] = "未获取到订单详情，请稍后重试"
       return render_to_response('wss/jdclbx_baseinfo_edit.html', data, context)
   
   
#编辑订单保险信息
# @OpenidViewRequired
# @JSAPI_TICKET_Required
def jdclbx_insurance_edit(request , order_id ):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    wss_tools = DocumentWssTools(request)
    if not order_id:
        data["message"] = "未获取订单编码，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        jdclbx_order = InquiryInfo.objects(id=order_id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
#     try:
    if jdclbx_order:
        data['order'] = jdclbx_order 
                
        if request.method == 'GET': 
             if  jdclbx_order.third_insurance ==0:
                       data['third_insurance'] = '不投保'
             else:
                      data['third_insurance'] = str(int(jdclbx_order.third_insurance/10000))+"万"
             #玻璃险
             if jdclbx_order.glass_insurance == "no"  :
                     data['glass_insurance'] = '不投保'
             elif  jdclbx_order.glass_insurance == "import" :
                     data['glass_insurance'] = '进口'
             elif  jdclbx_order.glass_insurance =="china"  :
                     data['glass_insurance'] = '国产'
             #司机险
             if  jdclbx_order.driver_insurance==0:
                     data['driver_insurance'] = '不投保'
             else:
                     data['driver_insurance'] = str(int(jdclbx_order.driver_insurance/10000))+"万"
              #乘客险
             if  jdclbx_order.passenger_insurance ==0:
                     data['passenger_insurance'] = '不投保'
             else:
                     data['passenger_insurance'] = str(int(jdclbx_order.passenger_insurance/10000))+"万"
             #划痕险
             if  jdclbx_order.scratch_insurance==0:
                  data['scratch_insurance'] = '不投保'
             elif  jdclbx_order.scratch_insurance ==2000:
                  data['scratch_insurance'] = '2千'
             elif  jdclbx_order.scratch_insurance == 5000:
                  data['scratch_insurance'] = '5千'
             elif jdclbx_order.scratch_insurance == 10000:
                  data['scratch_insurance'] = '1万'
             elif jdclbx_order.scratch_insurance == 20000:
                  data['scratch_insurance'] = '2万'
             if jdclbx_order.liability_expectStartTime:
                          data['liability_expectStartTime'] =jdclbx_order.liability_expectStartTime.strftime('%Y-%m-%d')
             if jdclbx_order.commercial_expectStartTime:
                          data['commercial_expectStartTime'] =  jdclbx_order.commercial_expectStartTime.strftime('%Y-%m-%d')
                          
             return render_to_response('wss/insure/jdclbx_insurance_edit.html', data, context)
        else:
             chongxinxunjia_state = request_tool.get_parameter('chongxinxunjia_state', '').strip()
             liability_state = request_tool.get_parameter('liability_state').strip()       #交强险
             vehicle_vessel_tax_state = request_tool.get_parameter('vehicle_vessel_tax_state').strip()       #车船税
             third_insurance = request_tool.get_parameter('third_insurance').strip()       #三者险
             damage_insurance = request_tool.get_parameter('damage_insurance').strip()       #车损险
             glass_insurance = request_tool.get_parameter('glass_insurance').strip()       #玻璃险
             driver_insurance = request_tool.get_parameter('driver_insurance').strip()       #司机险
             theft_insurance = request_tool.get_parameter('theft_insurance').strip()       #盗抢险
             passenger_insurance = request_tool.get_parameter('passenger_insurance').strip()       #乘客险
             iop_insurance = request_tool.get_parameter('iop_insurance').strip()       #不计免赔险
             autoignition_insurance = request_tool.get_parameter('autoignition_insurance').strip()       #自燃损失
             wading_insurance = request_tool.get_parameter('wading_insurance').strip()       #涉水险
             scratch_insurance = request_tool.get_parameter('scratch_insurance').strip()       #划痕险
      
             liability_expectStartTime = request_tool.get_parameter('liability_expectStartTime').strip()       #交强险保险起期
             commercial_expectStartTime = request_tool.get_parameter('commercial_expectStartTime').strip()       #商业险保险起期
    
             if liability_state=="on":
                      jdclbx_order.liability_state = True
             else:
                      jdclbx_order.liability_state = False
              #车船税
             if vehicle_vessel_tax_state=="on":
                     jdclbx_order.vehicle_vessel_tax_state = True
             else:
                     jdclbx_order.vehicle_vessel_tax_state = False
  
             if third_insurance == "不投保":
                      jdclbx_order.third_insurance = 0
             else:
                      jdclbx_order.third_insurance  = int(third_insurance.rstrip("万"))*10000
              #车损险
             if damage_insurance=="on":
                     jdclbx_order.damage_insurance = True
             else:
                     jdclbx_order.damage_insurance = False
             #玻璃险
             if glass_insurance== "不投保":
                     jdclbx_order.glass_insurance = "no"    
             elif glass_insurance== "进口":
                   jdclbx_order.glass_insurance = "import"    
             elif  glass_insurance== "国产":
                   jdclbx_order.glass_insurance = "china"    
             #司机险
             if driver_insurance == "不投保":
                    jdclbx_order.driver_insurance= 0
             else:
                    jdclbx_order.driver_insurance=  int(driver_insurance.rstrip("万"))*10000
             #盗抢险
             if theft_insurance=="on":
                   jdclbx_order.theft_insurance = True
             else:
                   jdclbx_order.theft_insurance = False
              #乘客险
             if passenger_insurance == "不投保":
                     jdclbx_order.passenger_insurance = 0
             else:
                     jdclbx_order.passenger_insurance = int(passenger_insurance.rstrip("万"))*10000
             #不计免赔险
             if iop_insurance=="on":
                    jdclbx_order.iop_insurance = True
             else:
                    jdclbx_order.iop_insurance = False
             #自燃损失
             if autoignition_insurance=="on":
                jdclbx_order.autoignition_insurance = True
             else:
                jdclbx_order.autoignition_insurance = False
             #涉水险
             if wading_insurance=="on":
                    jdclbx_order.wading_insurance = True
             else:
                jdclbx_order.wading_insurance = False
             #划痕险
             if scratch_insurance  == "不投保":
                  jdclbx_order.scratch_insurance = 0
             elif scratch_insurance  == "2千":
                  jdclbx_order.scratch_insurance = 2000
             elif scratch_insurance  == "5千":
                  jdclbx_order.scratch_insurance = 5000
             elif scratch_insurance  == "1万":
                  jdclbx_order.scratch_insurance = 10000
             elif scratch_insurance  == "2万":
                  jdclbx_order.scratch_insurance = 20000
             if liability_expectStartTime:
                jdclbx_order.liability_expectStartTime = liability_expectStartTime
             if commercial_expectStartTime:
                 jdclbx_order.commercial_expectStartTime = commercial_expectStartTime
             if not liability_state and not vehicle_vessel_tax_state and third_insurance == "不投保" and not damage_insurance and glass_insurance== "不投保" and driver_insurance == "不投保" and not theft_insurance and passenger_insurance == "不投保"  and not iop_insurance and not autoignition_insurance and not wading_insurance and  scratch_insurance  == "不投保":
                      data['message'] = '商业险和交强险请选择一种'
                      return render_to_response('wss/insure/jdclbx_insurance_edit.html', data, context) 
             try:
                   jdclbx_order.save()  
             except Exception as e:
                    print(traceback.format_exc())
                    data['message'] = str(e)                
             data['order'] = jdclbx_order
             data['chongxinxunjia_state'] = chongxinxunjia_state  
             return render_to_response('wss/insure/jdclbx_edit_list.html', data, context)    
    else:
       data["message"] = "未获取到订单详情，请稍后重试"
       return render_to_response('wss/warn.html', data, context)

#编辑订单列表
# @OpenidViewRequired
# @JSAPI_TICKET_Required
def jdclbx_edit_list(request , order_id ):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    wss_tools = DocumentWssTools(request)
    jdclbx_order = InquiryInfo.objects(id=order_id).first()
    business_license_list = []
    id_card_list =[]
    data['order'] = jdclbx_order
    if request.method == 'GET':
          return render_to_response('wss/insure/jdclbx_edit_list.html', data, context)
    else:
           intermediaryRate_set = IntermediaryRate.objects(jdclbx_order=jdclbx_order)
           if intermediaryRate_set:
                   for intermediaryRate in intermediaryRate_set:
                              intermediaryRate.delete()
           intermediaryPrice_set = IntermediaryPrice.objects(order=jdclbx_order)
           if intermediaryPrice_set:
               for intermediaryPrice in intermediaryPrice_set:
                   intermediaryPrice.delete()
           jdclbx_order.state = "verify"
           jdclbx_order.intermediary_list=[]
           try:
                  jdclbx_order.save()  
           except Exception as e:
                 print(traceback.format_exc())
                 data['message'] = str(e)
                 return render_to_response('wss/insure/jdclbx_edit_list.html', data, context)
           if  jdclbx_order.business_license_image: 
                    business_license_imaga = '/static/'+ jdclbx_order.business_license_image
                    business_license_list.append(business_license_imaga)
                    data['id_card_list'] = business_license_list  
                    data['shangye_pic_list'] = business_license_list   
                    data['jiaoqiang_pic_list'] = business_license_list   
           if  jdclbx_order.id_card_up and  jdclbx_order.id_card_down:
                       id_card_up= '/static/'+jdclbx_order.id_card_up
                       id_card_down =  '/static/'+jdclbx_order.id_card_down
                       id_card_list.append(id_card_up)
                       id_card_list.append(id_card_down)
                       data['id_card_list'] = id_card_list   
                       data['shangye_pic_list'] = id_card_list   
                       data['jiaoqiang_pic_list'] = id_card_list   
           data['order'] = jdclbx_order   
           return render_to_response('wss/insure/car_insurance_detail.html', data, context) 
    
    
#删除订单
@OpenidViewRequired
@JSAPI_TICKET_Required
def jdclbx_order_delete(request , order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    order_id = order_id
    if order_id:
        try:
            jdclbx_order = InquiryInfo.objects(id=order_id).first()
        except:
            data["message"] = "未找到订单信息，请检查您想删除的定单"
            return render_to_response('wss/warn.html', data, context)
        if not jdclbx_order:
            data["message"] = "网络不稳定，未找到订单信息"
            return render_to_response('wss/warn.html', data, context)
        #删除中介报价内容
        try:
            intermediary_price_list=IntermediaryPrice.objects(order=jdclbx_order)
            if intermediary_price_list:
                for intermediary_price_detail in intermediary_price_list:
                    intermediary_price_detail.delete()
        except Exception as e:
            data['message'] = str(e)+"删除报价信息失败"
            return render_to_response('wss/warn.html', data, context)
        #删除添加中介手续费内容
        try:
            intermediary_rate_list=IntermediaryRate.objects(jdclbx_order=jdclbx_order)
            if intermediary_rate_list:
                for intermediary_rate_detail in intermediary_rate_list:
                    intermediary_rate_detail.delete()
        except Exception as e:
            data['message'] = str(e)+"删除手续费失败"
            return render_to_response('wss/warn.html', data, context)
        #删除订单信息
        try:
            jdclbx_order.delete()
            data['message'] = "删除成功"
            return render_to_response('wss/success.html', data, context)
        except Exception as e:
            data['message'] = str(e)+"删除订单信息失败"
            return render_to_response('wss/warn.html', data, context)
        
        
#         if jdclbx_order.state == "wait" or jdclbx_order.state == "init" :
#            intermediaryRate = IntermediaryRate.objects(jdcbx_order=jdclbx_order).first()
#            if intermediaryRate:
#                    intermediaryRate.delete()
#            intermediaryPrice = IntermediaryPrice.objects(order=jdclbx_order).first()
#            if intermediaryPrice:
#                    intermediaryPrice.delete()
#            jdclbx_order.delete()
#            data["message"] = "删除订单成功"
           #return HttpResponseRedirect(reverse('wss:car_order_list'))
           #return render_to_response('wss/success.html', data, context)
    else:
        data["message"] = "未找到订单信息，请检查您想删除的定单"
        return render_to_response('wss/warn.html', data, context)

   #行驶证图片详情
@OpenidViewRequired
@JSAPI_TICKET_Required
def  driving_license_pic(request, order_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_order'))

    elif request.method == 'GET':
        picture_type = request_tool.get_parameter('type').strip()       #查看图片类型
        if not picture_type:
            data["message"] = "网络不稳定，未获取到您要查看的证件照片类型"
            return render_to_response('wss/warn.html', data, context)
        data['picture_type'] = picture_type
        jdclbx_order = InquiryInfo.objects(id=order_id).first()
        data['order'] = jdclbx_order
        return render_to_response('wss/insure/jdclbx_driving_pic.html', data, context)



#编辑订单信息
@OpenidViewRequired
@JSAPI_TICKET_Required
def jdclbx_order_edit(request , order_id ):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    wss_tools = DocumentWssTools(request)
    plate_number = []
    if not order_id:
        data["message"] = "未获取订单编码，请稍后重试"
        return render_to_response('wss/warn.html', data, context)
    try:
        jdclbx_order = InquiryInfo.objects(id=order_id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
#     try:
    if jdclbx_order:
        data['order'] = jdclbx_order   
        plate_number=jdclbx_order.plate_number.split(' ')      
        data['short'] = plate_number[0]+" "+plate_number[1]
        data['wx_plate_number'] = plate_number[2]        
        if request.method == 'GET': 
             if  jdclbx_order.third_insurance ==0:
                       data['third_insurance'] = '不投保'
             else:
                      data['third_insurance'] = str(int(jdclbx_order.third_insurance/10000))+"万"
             #玻璃险
             if jdclbx_order.glass_insurance == "no"  :
                     data['glass_insurance'] = '不投保'
             elif  jdclbx_order.glass_insurance == "import" :
                     data['glass_insurance'] = '进口'
             elif  jdclbx_order.glass_insurance =="china"  :
                     data['glass_insurance'] = '国产'
             #司机险
             if  jdclbx_order.driver_insurance==0:
                     data['driver_insurance'] = '不投保'
             else:
                     data['driver_insurance'] = str(int(jdclbx_order.driver_insurance/10000))+"万"
              #乘客险
             if  jdclbx_order.passenger_insurance ==0:
                     data['passenger_insurance'] = '不投保'
             else:
                     data['passenger_insurance'] = str(int(jdclbx_order.passenger_insurance/10000))+"万"
             #划痕险
             if  jdclbx_order.scratch_insurance==0:
                  data['scratch_insurance'] = '不投保'
             elif  jdclbx_order.scratch_insurance ==2000:
                  data['scratch_insurance'] = '2千'
             elif  jdclbx_order.scratch_insurance == 5000:
                  data['scratch_insurance'] = '5千'
             elif jdclbx_order.scratch_insurance == 10000:
                  data['scratch_insurance'] = '1万'
             elif jdclbx_order.scratch_insurance == 20000:
                  data['scratch_insurance'] = '2万'
             if jdclbx_order.liability_expectStartTime:
                          data['liability_expectStartTime'] =jdclbx_order.liability_expectStartTime.strftime('%Y-%m-%d')
             if jdclbx_order.commercial_expectStartTime:
                          data['commercial_expectStartTime'] =  jdclbx_order.commercial_expectStartTime.strftime('%Y-%m-%d')
                          
#回显城市     
#              shengcode = jdclbx_order.city.code[0:2]
#              cargoshen = CargoArea.objects(code=shengcode,level ='1').first()
#              geng = cargoshen.name+' '+ jdclbx_order.city.name
#        
#              data['city'] = cargoshen.name+' '+ jdclbx_order.city.name
             
             return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)
        else:
             chongxinxunjia_state = request_tool.get_parameter('chongxinxunjia_state', '').strip()
             short = request_tool.get_parameter('short', '').strip()
             wx_plate_number = request_tool.get_parameter('wx_plate_number', '').strip()
            # home_city = request_tool.get_parameter('wx_home_city', '').strip()
             car_type = request_tool.get_parameter('wx_car_type', '').strip()
              #录入投保人信息--个人
             user_classify = request_tool.get_parameter('wx_user_classify').strip()       #投保人身份选择
             applicant_name = request_tool.get_parameter('wx_applicant_name').strip()       #投保人姓名
             #certificate_number = request_tool.get_parameter('wx_certificate_number').strip()       #身份证号
             applicant_phone = request_tool.get_parameter('wx_applicant_phone').strip()       #投保人手机号
              #录入投保人信息--单位
             applicant_company_name = request_tool.get_parameter('applicant_company_name').strip()       #单位名称
             #organ_number = request_tool.get_parameter('wx_organ_number').strip()       #证件号
              
              #录入投保人信息--被保人
             insured_name = request_tool.get_parameter('wx_insured_name').strip()       #被保人姓名
             insured_phone = request_tool.get_parameter('wx_insured_phone').strip()       #被保人手机号
             wx_mail_address = request_tool.get_parameter('wx_mail_address').strip()       #保单邮寄地址
             wx_policy_address = request_tool.get_parameter('wx_policy_address').strip()       #保详细地址
             national_image = request.FILES.get('national_image', '')   #行驶证正面
             national_image_down = request.FILES.get('national_image_down', None)     #行驶证反面
             card_up = request.FILES.get('card_up', '')   #身份证正面
             card_down = request.FILES.get('card_down', None)     #身份证反面
             license_image = request.FILES.get('license_image', '')   #营业执照照片
             
             #保险类型
             liability_state = request_tool.get_parameter('liability_state').strip()       #交强险
             vehicle_vessel_tax_state = request_tool.get_parameter('vehicle_vessel_tax_state').strip()       #车船税
             third_insurance = request_tool.get_parameter('third_insurance').strip()       #三者险
             damage_insurance = request_tool.get_parameter('damage_insurance').strip()       #车损险
             glass_insurance = request_tool.get_parameter('glass_insurance').strip()       #玻璃险
             driver_insurance = request_tool.get_parameter('driver_insurance').strip()       #司机险
             theft_insurance = request_tool.get_parameter('theft_insurance').strip()       #盗抢险
             passenger_insurance = request_tool.get_parameter('passenger_insurance').strip()       #乘客险
             iop_insurance = request_tool.get_parameter('iop_insurance').strip()       #不计免赔险
             autoignition_insurance = request_tool.get_parameter('autoignition_insurance').strip()       #自燃损失
             wading_insurance = request_tool.get_parameter('wading_insurance').strip()       #涉水险
             scratch_insurance = request_tool.get_parameter('scratch_insurance').strip()       #划痕险
      
             liability_expectStartTime = request_tool.get_parameter('liability_expectStartTime').strip()       #交强险保险起期
             commercial_expectStartTime = request_tool.get_parameter('commercial_expectStartTime').strip()       #商业险保险起期
              
           
#城市选择
#              home_citylist=[]
#              if home_city:  
#                     home_citylist = home_city.split(' ')
#                     count = len(home_citylist)
#                     if  count ==1:
#                           cargoshi = CargoArea.objects(name__contains=home_citylist[0])
#                     elif count ==2:
#                           cargoshi = CargoArea.objects(name__contains=home_citylist[1])
#                     if cargoshi:
#                            for cargoshiobj in cargoshi:
#                                if  cargoshiobj.level =="2":
#                                    jdclbx_order.city = cargoshiobj
#                                    break         
#                     else:
#                            data['message'] = '选择城市错误！'
#                            return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)
#              else:
#                  data['message'] = '请选择城市！'
#                  return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context)
             car_type_list = InquiryInfo.ORDER_CAR_TYPE                 #车辆类型
             wx_jiancheng = []
             wx_jiancheng =  short.split(' ')
             intermediary_set= Intermediary.objects()
             intermediary_city = []
             intermediary_car = []
             
             for intermediaryobj in intermediary_set:
                    if wx_jiancheng[0] in intermediaryobj.plate_number_list:
                        
                                   intermediary_city.append(intermediaryobj)
                                 
             if intermediary_city:
                       if car_type:  
                                    for car_type_obj in car_type_list:
                                          if car_type_obj[1]==car_type:
                                                jdclbx_order.order_car_type = car_type_obj[0]
                                                break    
                                    for intermediary_city_obj in  intermediary_city:
                                           if  jdclbx_order.order_car_type in intermediary_city_obj.order_car_type:
                                                  intermediary_car.append(intermediary_city_obj)
                       else:
                                        data['message'] = '请选择车辆类型！'
                                        return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)
             else:
                  data['message'] = '车牌所在城市暂时不可保！'
                  return render_to_response('wss/insure/jdclbx_order_edit.html', data, context) 
                                 
             if intermediary_car:
                  if  wx_plate_number:
                         jdclbx_order.plate_number = str(short)+' '+str(wx_plate_number)
                  else:
                          data['message'] = '请填写车牌号！'
                          return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)               
                  
             else:
                  data['message'] = '暂时没有可保的车辆类型！'
                  return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)        
             
             if user_classify == "个人":
                      jdclbx_order.user_classify = 'personal'
                      jdclbx_order.business_license_image = ""
                      if applicant_name:
                             jdclbx_order.applicant_name = applicant_name
                      else:
                             data['message'] = '投保人姓名不能为空！'
                             return render_to_response('wss/insure/jdclbx_order_edit.html', data, context) 
#身份证号
#                       if certificate_number:
#                              jdclbx_order.certificate_number = certificate_number
#                       else:
#                            data['message'] = '投保人身份证不能为空！'
#                            return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
                      if applicant_phone:
                          jdclbx_order.applicant_phone = applicant_phone
                      else:
                           data['message'] = '投保人手机号不能为空！'
                           return render_to_response('wss/insure/jdclbx_order_edit.html', data, context) 
             elif user_classify == "单位":
                     jdclbx_order.user_classify = 'unit'
                     jdclbx_order.id_card_up = ""
                     jdclbx_order.id_card_down = ""
                     if applicant_company_name:
                         jdclbx_order.applicant_company_name = applicant_company_name
                     else:
                         data['message'] = '公司名称不能为空！'
                         return render_to_response('wss/insure/jdclbx_order_edit.html', data, context) 
#证件号
#                      if organ_number:
#                              jdclbx_order.organ = organ_number
#                      else:
#                            data['message'] = '单位证件号不能为空！'
#                            return render_to_response('wss/insure/jdclbx_baseinfo_edit.html', data, context) 
                     if applicant_phone:
                          jdclbx_order.applicant_phone = applicant_phone
                     else:
                           data['message'] = '投保人手机号不能为空！'
                           return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)   
                     if applicant_phone:
                          jdclbx_order.applicant_phone = applicant_phone
                     else:
                           data['message'] = '投保人手机号不能为空！'
                           return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)   
             if wx_mail_address:
                      jdclbx_order.mail_address = wx_mail_address
             else:
                    data['message'] = '邮寄地址不能为空！'
                    return render_to_response('wss/insure/jdclbx_order_edit.html', data, context) 
             if wx_policy_address:
                      jdclbx_order.policy_address = wx_policy_address
             else:
                    data['message'] = '详细地址不能为空！'
                    return render_to_response('wss/insure/jdclbx_order_edit.html', data, context) 
              
              #身份证正面更新
             if card_up:
                image_tool = ImageTools()
                try:
                    id_card_up_url = image_tool.save(request_file=card_up, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_card_up_url:
                        jdclbx_order.id_card_up=id_card_up_url
                        jdclbx_order.certificate_number = ""
     
                    else:
                         data['message'] = '身份证正面图片上传失败！'
                         return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)
                except:
                     data['message'] = '更新身份证正面失败！'
                     return render_to_response('wss/insure/jdclbx_order_edit.html', data, context) 
              #身份证背面更新
             if card_down:
                image_tool = ImageTools()
                try:
                    id_card_down_url = image_tool.save(request_file=card_down, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_card_down_url:
                        jdclbx_order.id_card_down=id_card_down_url
                        jdclbx_order.certificate_number = ""
                   
                    else:
                         data['message'] = '身份证背面图片上传失败！'
                         return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)
                except:
                     data['message'] = '更新身份证背面失败！'
                     return render_to_response('wss/insure/jdclbx_order_edit.html', data, context) 
              
              #营业执照更新
             if license_image:
                image_tool = ImageTools()
                try:
                    id_license_image_url = image_tool.save(request_file=license_image, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_license_image_url:
                        jdclbx_order.business_license_image=id_license_image_url
                        jdclbx_order.organ = ""
                    else:
                         data['message'] = '营业执照图片上传失败！'
                         return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)
                except:
                     data['message'] = '更新营业执照失败！'
                     return render_to_response('wss/insure/jdclbx_order_edit.html', data, context) 
              #行驶证正更新面
             if national_image:
                image_tool = ImageTools()
                try:
                    id_card_up_url = image_tool.save(request_file=national_image, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_card_up_url:
                        jdclbx_order.plate_image_left=id_card_up_url
                        jdclbx_order.holder = ""
                        jdclbx_order.use_property = ""
                        jdclbx_order.brand_digging = "" 
                        jdclbx_order.car_number = ""
                        jdclbx_order.engine_number = ""
                        jdclbx_order.issue_date = ""
                        jdclbx_order.people_number = ""
                        jdclbx_order.load_weight = ""
                    else:
                         data['message'] = '行驶证正面图片上传失败！'
                         return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)
                except:
                     data['message'] = '更新行驶证正面失败！'
                     return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)

             #行驶证背面更新
             if national_image_down:
                        image_tool = ImageTools()
                        try:
                            id_card_down_url = image_tool.save(request_file=national_image_down, file_folder=ImageFolderType.jdclbx, old_file='')
                            if id_card_down_url:
                                jdclbx_order.plate_image_right=id_card_down_url
                                jdclbx_order.holder = ""
                                jdclbx_order.use_property = ""
                                jdclbx_order.brand_digging = "" 
                                jdclbx_order.car_number = ""
                                jdclbx_order.engine_number = ""
                                jdclbx_order.issue_date = ""
                                jdclbx_order.people_number = ""
                                jdclbx_order.load_weight = ""
                            else:
                                data['message'] = '行驶证背面图片上传失败！'
                                return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)
                        except:
                             data['message'] = '更新行驶证背面失败！'
                             return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)            
            
             #保险类型
             if liability_state=="on":
                      jdclbx_order.liability_state = True
             else:
                      jdclbx_order.liability_state = False
              #车船税
             if vehicle_vessel_tax_state=="on":
                     jdclbx_order.vehicle_vessel_tax_state = True
             else:
                     jdclbx_order.vehicle_vessel_tax_state = False
  
             if third_insurance == "不投保":
                      jdclbx_order.third_insurance = 0
             else:
                      jdclbx_order.third_insurance  =int(third_insurance.rstrip("万"))*10000
              #车损险
             if damage_insurance=="on":
                     jdclbx_order.damage_insurance = True
             else:
                     jdclbx_order.damage_insurance = False
             #玻璃险
             if glass_insurance== "不投保":
                     jdclbx_order.glass_insurance = "no"    
             elif glass_insurance== "进口":
                   jdclbx_order.glass_insurance = "import"    
             elif  glass_insurance== "国产":
                   jdclbx_order.glass_insurance = "china"    
             #司机险
             if driver_insurance == "不投保":
                    jdclbx_order.driver_insurance= 0
             else:
                    jdclbx_order.driver_insurance= int(driver_insurance.rstrip("万"))*10000
             #盗抢险
             if theft_insurance=="on":
                   jdclbx_order.theft_insurance = True
             else:
                   jdclbx_order.theft_insurance = False
              #乘客险
             if passenger_insurance == "不投保":
                     jdclbx_order.passenger_insurance = 0
             else:
                     jdclbx_order.passenger_insurance =int(passenger_insurance.rstrip("万"))*10000
             #不计免赔险
             if iop_insurance=="on":
                    jdclbx_order.iop_insurance = True
             else:
                    jdclbx_order.iop_insurance = False
             #自燃损失
             if autoignition_insurance=="on":
                jdclbx_order.autoignition_insurance = True
             else:
                jdclbx_order.autoignition_insurance = False
             #涉水险
             if wading_insurance=="on":
                    jdclbx_order.wading_insurance = True
             else:
                jdclbx_order.wading_insurance = False
             #划痕险
             if scratch_insurance  == "不投保":
                  jdclbx_order.scratch_insurance = 0
             elif scratch_insurance  == "2千":
                  jdclbx_order.scratch_insurance = 2000
             elif scratch_insurance  == "5千":
                  jdclbx_order.scratch_insurance = 5000
             elif scratch_insurance  == "1万":
                  jdclbx_order.scratch_insurance = 10000
             elif scratch_insurance  == "2万":
                  jdclbx_order.scratch_insurance = 20000
             if liability_expectStartTime:
                jdclbx_order.liability_expectStartTime = liability_expectStartTime
             if commercial_expectStartTime:
                 jdclbx_order.commercial_expectStartTime = commercial_expectStartTime
             if not liability_state and not vehicle_vessel_tax_state and third_insurance == "不投保" and not damage_insurance and glass_insurance== "不投保" and driver_insurance == "不投保" and not theft_insurance and passenger_insurance == "不投保"  and not iop_insurance and not autoignition_insurance and not wading_insurance and  scratch_insurance  == "不投保":
                      data['message'] = '商业险和交强险请选择一种'
                      return render_to_response('wss/insure/jdclbx_order_edit.html', data, context)  
             #清除关联表
             intermediaryRate_set = IntermediaryRate.objects(jdclbx_order=jdclbx_order)
             if intermediaryRate_set:
                   for intermediaryRate in intermediaryRate_set:
                              intermediaryRate.delete()
             intermediaryPrice_set = IntermediaryPrice.objects(order=jdclbx_order)
             if intermediaryPrice_set:
                  for intermediaryPrice in intermediaryPrice_set:
                       intermediaryPrice.delete()
             jdclbx_order.state = "verify"
             jdclbx_order.intermediary_list=[]
             try:
                   jdclbx_order.save()  
             except Exception as e:
                   print(traceback.format_exc())
                   data['message'] = str(e) 
             id_card_list = []
             business_license_list=[]
             if  jdclbx_order.business_license_image: 
                    business_license_imaga = '/static/'+ jdclbx_order.business_license_image
                    business_license_list.append(business_license_imaga)
                    data['id_card_list'] = business_license_list  
                    data['shangye_pic_list'] = business_license_list   
                    data['jiaoqiang_pic_list'] = business_license_list   
             if  jdclbx_order.id_card_up and  jdclbx_order.id_card_down:
                       id_card_up= '/static/'+jdclbx_order.id_card_up
                       id_card_down =  '/static/'+jdclbx_order.id_card_down
                       id_card_list.append(id_card_up)
                       id_card_list.append(id_card_down)
                       data['id_card_list'] = id_card_list   
                       data['shangye_pic_list'] = id_card_list   
                       data['jiaoqiang_pic_list'] = id_card_list       
             data['order'] = jdclbx_order       
             data['date_state'] = "edit"  
             return render_to_response('wss/insure/car_insurance_detail.html', data, context)    
    else:
       data["message"] = "未获取到订单详情，请稍后重试"
       return render_to_response('wss/jdclbx_order_edit.html', data, context)





#暂时没用
def check_info(request):
 
 data = {}
 context = RequestContext(request)
 
#                   new_batch_insurance_price =int(batch_insurance_price.rstrip("万"))*10000
#                          order.insurance_price = int(new_batch_insurance_price*100)
 #return render_to_response('wss/insure/ai_car_info.html', data, context) #车辆信息
 #return render_to_response('wss/insure/ai_insurance_type.html', data, context) #选择险种界面
 #return render_to_response('wss/insure/ai_user.html', data, context) #用户信息
 #return render_to_response('wss/insure/auto_insurance.html', data, context) #机动车投保页面
 #return render_to_response('wss/insure/check_info.html', data, context) #核对车辆信息
 #return render_to_response('wss/insure/insurance_list.html', data, context) #询价后的保险列表
#return render_to_response('wss/insure/insurance_period.html', data, context) #保险起期页面 
 return render_to_response('wss/insure/ai_insurance_type.html', data, context) 
 
 
 
  #机动车辆保险页面
@OpenidViewRequired
@JSAPI_TICKET_Required
def jdclbx_order_create_new(request):
     data = {}
     context = RequestContext(request)
     request_tool = RequestTools(request)
     request_tool.check_message(data)
     wss_tools = DocumentWssTools(request)
     jdclbx_order = InquiryInfo()
     try:
         client = Client.objects(user=request.user).first()
         #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
         if client:
                jdclbx_order.client = client
         else:
                data['message'] = '用户不存在'
                return render_to_response('wss/insure/auto_insurance.html', data, context)
     except:
             data['message'] = '用户信息获取失败，请清理缓存后重试'   
             return render_to_response('wss/insure/auto_insurance.html', data, context)

     if request.method == 'POST':
         data1={}
         message=''
         #data['posted_data'] = request.POST
         order_car_type = request_tool.get_parameter('order_car_type', '').strip()
         plate_number = request_tool.get_parameter('plate_number', '').strip()
         city_code = request_tool.get_parameter('city_code', '').strip()
         data['city_code'] = city_code#传递所选城市
         data['plate_number'] = plate_number#传递车牌号
         data['order_car_type'] = order_car_type#传递所选城市
         if not order_car_type or not plate_number or not city_code:
             message = '网络延迟，未获取到车牌号、车辆所在城市或投保车辆类型，请刷新后重试'   
             #return render_to_response('wss/insure/auto_insurance.html', data, context)
             return  JsonResult(data=data1, code=CODE_ERROR, message=message).response()
         try:
             jdclbx_order_set = wss_tools.validation_jdclbx_order(jdclbx_order)
             jdclbx_order_set.save()
             data['message'] = "订单创建成功"
             data['order'] = jdclbx_order_set   
             #2017/08/28添加提醒出单员出单的功能
             try:
                site_settings = SiteSettings.get_settings()
                helper = m5c_sms_helper.SmsHelper(site_settings.meilian_username, site_settings.meilian_password, site_settings.meilian_api_key)
                dx_content ="订单号为："+str(jdclbx_order_set.paper_id)+ "，车牌号为："+str(jdclbx_order_set.plate_number)+"的订单已生成，请及时审单"
                helper.send_sms(phone_to='17745170813', content=dx_content)
             except Exception as e:
                 pass
             #添加结束
             data1['jdclbx_id'] =str(jdclbx_order_set.id)
             return JsonResult(data=data1, code=CODE_SUCCESS).response()
             #return HttpResponseRedirect(reverse('wss:jdclbx_detail', args=[jdclbx_order_set.id, ])) 
             #return render_to_response('wss/insure/ai_baseinfo.html', data, context)
         except Exception as e:
                message =  e.message
                return  JsonResult(data=data1, code=CODE_ERROR, message=message).response()
     else:
         city_code = request.session.get('city_code', '')#传递所选城市
         plate_number = request.session.get('plate_number', '')#传递车牌号
         order_car_type = request.session.get('order_car_type', '')#传递所选城市
         if not order_car_type or not plate_number or not city_code:
             data['message'] = '网络延迟，未获取到车牌号、车辆所在城市或投保车辆类型，请重新输入'   
             return render_to_response('wss/insure/auto_insurance.html', data, context)
         data['city_code'] = city_code#传递所选城市
         data['plate_number'] = plate_number#传递车牌号
         data['order_car_type'] = order_car_type#传递所选城市
         request.session['city_code'] = ''#传递所选城市
         request.session['plate_number'] = ''#传递车牌号
         request.session['order_car_type'] = ''#传递车辆类型
         return render_to_response('wss/insure/ai_baseinfo.html', data, context)
  #机动车辆保险页面
@OpenidViewRequired
@JSAPI_TICKET_Required
def jdclbx_order_create_new1(request):
     data = {}
     context = RequestContext(request)
     request_tool = RequestTools(request)
     request_tool.check_message(data)
     wss_tools = DocumentWssTools(request)
     jdclbx_order = InquiryInfo()
     try:
         client = Client.objects(user=request.user).first()
         #client = Client.objects(id='574e37d79a8f2b0e2a811ff2').first()
         if client:
                jdclbx_order.client = client
         else:
                data['message'] = '用户不存在'
                return render_to_response('wss/insure/auto_insurance.html', data, context)
     except:
             data['message'] = '用户信息获取失败，请清理缓存后重试'   
             return render_to_response('wss/insure/auto_insurance.html', data, context)

     if request.method == 'POST':
         data['posted_data'] = request.POST
         order_car_type = request_tool.get_parameter('order_car_type', '').strip()
         plate_number = request_tool.get_parameter('plate_number', '').strip()
         city_code = request_tool.get_parameter('city_code', '').strip()
         data['city_code'] = city_code#传递所选城市
         data['plate_number'] = plate_number#传递车牌号
         data['order_car_type'] = order_car_type#传递所选城市
         if not order_car_type or not plate_number or not city_code:
             data['message'] = '网络延迟，未获取到车牌号、车辆所在城市或投保车辆类型'   
             return render_to_response('wss/insure/auto_insurance.html', data, context)
         try:
             jdclbx_order_set = wss_tools.validation_jdclbx_order(jdclbx_order)
             jdclbx_order_set.save()
             data['message'] = "订单创建成功"
             data['order'] = jdclbx_order_set   
             #2017/08/28添加提醒出单员出单的功能
             try:
                site_settings = SiteSettings.get_settings()
                helper = m5c_sms_helper.SmsHelper(site_settings.meilian_username, site_settings.meilian_password, site_settings.meilian_api_key)
                dx_content = "{0}订单已生成，请及时出单".format(jdclbx_order_set.plate_number)
                helper.send_sms(phone_to='17745170813', content=dx_content)
             except Exception as e:
                 pass
             #添加结束
             return HttpResponseRedirect(reverse('wss:jdclbx_detail', args=[jdclbx_order_set.id, ])) 
             #return render_to_response('wss/insure/ai_baseinfo.html', data, context)
         except Exception as e:
                data['message'] = str(e)   
                return render_to_response('wss/insure/ai_baseinfo.html', data, context)
     else:
         city_code = request.session.get('city_code', '')#传递所选城市
         plate_number = request.session.get('plate_number', '')#传递车牌号
         order_car_type = request.session.get('order_car_type', '')#传递所选城市
         if not order_car_type or not plate_number or not city_code:
             data['message'] = '网络延迟，未获取到车牌号、车辆所在城市或投保车辆类型，请重新输入'   
             return render_to_response('wss/insure/auto_insurance.html', data, context)
         data['city_code'] = city_code#传递所选城市
         data['plate_number'] = plate_number#传递车牌号
         data['order_car_type'] = order_car_type#传递所选城市
         request.session['city_code'] = ''#传递所选城市
         request.session['plate_number'] = ''#传递车牌号
         request.session['order_car_type'] = ''#传递车辆类型
         return render_to_response('wss/insure/ai_baseinfo.html', data, context)
     
@OpenidViewRequired
@JSAPI_TICKET_Required
def jdclbx_order_edit_new(request , order_id ):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    wss_tools = DocumentWssTools(request)
    try:
        jdclbx_order = InquiryInfo.objects(id=order_id).first()
    except:
        data["message"] = "网络不稳定，或订单信息不存在"
        return render_to_response('wss/warn.html', data, context)
    if jdclbx_order:
        #分解城市
        city_detail = jdclbx_order.city#市
        pro_detail =  CargoArea.objects(code=jdclbx_order.city.parentcode).first()#省份
        data['city_code'] = city_detail.code
        data['city_name'] = pro_detail.name+ ' ' + city_detail.name
        #分解车牌号
        if jdclbx_order.plate_number:
            short =  jdclbx_order.plate_number[0:3]
            plate_number = jdclbx_order.plate_number[4:]
            data['short'] = short  
            data['plate_number'] = plate_number  
        #车辆类型
        if jdclbx_order.order_car_type == 'passenger_car':
            order_car_type='九座以下客车'
        elif jdclbx_order.order_car_type == 'truck':
            order_car_type='货车'
        else:
            data["message"] = "网络不稳定，未获取到订单车辆类型"
            return render_to_response('wss/warn.html', data, context)
        data['order_car_type'] = order_car_type  
        data['jdclbx_set'] = jdclbx_order  
    if request.method == 'POST':    
        try:
            jdclbx_order_set = wss_tools.validation_jdclbx_order(jdclbx_order)
            jdclbx_order_set.save()
            jdclbx_order_set.state='verify'
            jdclbx_order_set.save()
            jdclbx_order_set.fail_reason=''
            jdclbx_order_set.save()
            data['order'] = jdclbx_order_set   
           # return render_to_response('wss/insure/ai_baseinfo_edit.html', data, context) 
        except Exception as e:
                data['message'] = str(e)   
                return render_to_response('wss/insure/ai_baseinfo_edit.html', data, context)
        #删除中介报价内容
        try:
            intermediary_price_list=IntermediaryPrice.objects(order=jdclbx_order_set)
            if intermediary_price_list:
                for intermediary_price_detail in intermediary_price_list:
                    intermediary_price_detail.delete()
        except Exception as e:
            data['message'] = str(e)+"删除报价信息失败"
            return render_to_response('wss/insure/ai_baseinfo_edit.html', data, context)
        #删除添加中介手续费内容
        try:
            intermediary_rate_list=IntermediaryRate.objects(jdclbx_order=jdclbx_order_set)
            if intermediary_rate_list:
                for intermediary_rate_detail in intermediary_rate_list:
                    intermediary_rate_detail.delete()
        except Exception as e:
            data['message'] = str(e)+"删除手续费失败"
            return render_to_response('wss/insure/ai_baseinfo_edit.html', data, context)
        data['message'] = "订单编辑成功"
        return HttpResponseRedirect(reverse('wss:jdclbx_detail', args=[jdclbx_order_set.id, ]))
        #return render_to_response('wss/insure/car_insurance_detail.html', data, context)
        #return render_to_response('wss/insure/ai_baseinfo_edit.html', data, context) 
    else:
        data['message1'] = '进入编辑状态'
        return render_to_response('wss/insure/ai_baseinfo_edit.html', data, context)
 
#微信支付
@OpenidViewRequired
def wx_pay(request):
    context = RequestContext(request)
    request_tool = RequestTools(request)
    client = Client.objects(user=request.user).first()
    data = {}
    if request.method == 'POST':
        # 根据用户类型转向特定页面
        return HttpResponseRedirect(reverse('wss:my_order'))
    elif request.method == 'GET':
        order_id = request.GET.get("order_id","")
        if not order_id:
            data["message"] = "网络问题，未获取到订单参数"
            return render_to_response('wss/warn.html', data, context)
        try:
            order = Ordering.objects(id=order_id).first()
        except:
            data["message"] = "网络问题未获取到订单数据，请稍后再试"
            return render_to_response('wss/warn.html', data, context)
        if order.state == 'init':
            data['order'] = order
            return render_to_response('wss/insure/wx_pay.html', data, context)
        else:
            data["message"] = "订单状态不正确，请选择未支付订单"
            return render_to_response('wss/warn.html', data, context)
    
#申请分期 
@CODE_View_Required
@JSAPI_TICKET_Required
@OpenidViewRequired
def test_apply(request):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    url_test= str(settings.QUCHEXIAN_URL)
    try:

        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        client = Client.objects(user=request.user).first()
    except:
        data["message"] = "网络问题未获取到用户数据，请稍后再试"
        return render_to_response('wss/warn.html', data, context)
    try:
        #url ="http://www.tianshoufenqi.com/mobile/mobilereg?yzb=2&phone="+str(client.profile.phone)
        url =url_test+"/mobile/mobilereg?yzb=2&phone="+str(client.profile.phone)
        return HttpResponseRedirect(url)  
    except:
        data["message"] = "网络问题未获取到用户数据，请稍后再试。"
        return render_to_response('wss/warn.html', data, context)
    

#支付订单201710/26添加新的流程
@OpenidViewRequired
@JSAPI_TICKET_Required
def order_pay_update(request, order_id):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    wss_tools = DocumentWssTools(request)
    request_tool.check_message(data)
    client = Client.objects(user=request.user).first()
    data['client'] = client
    order = Ordering.objects(id=order_id).first()
    data['order'] = order
    gly_wx='oYXlSwfedYTw0OtzfRy2SYpPrNE8'
    if request.method == 'POST':
        try:
            if order.state != 'init':
                request_tool.set_message('支付订单状态错误')
                return HttpResponseRedirect(reverse('wss:order_pay_update', args=[order.id, ]))

            password = request_tool.get_parameter('password', '').strip()
            if password:
                password = hashlib.sha1(password.encode('utf-8')).hexdigest()
                if client.password == password:
                        message2=""
                        if order.client.balance >= order.price:
                            order.pay_money()
                            order.save()
                            #2017 添加支付统计
                            try:
                                if PaymentStatistical.objects(order=order).count()==0:
                                    payment_statistical = PaymentStatistical()
                                else:
                                    payment_statistical = PaymentStatistical.objects(order=order).first()
                                payment_statistical.client = order.client
                                payment_statistical.price = order.price
                                payment_statistical.order = order
                                payment_statistical.order_type = order.product_type
                                payment_statistical.state = 'wx_price'
                                payment_statistical.save()
                            except Exception as e :
                                message= '付款成功，网络延迟付款记录保存失败：'+str(e)
                                request_tool.set_message(message)
                            if int(order.client.balance/100)  >= 500:
                                    content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。"
                            else:
                                     content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。预存余额不足500，为了避免余额不足导致无法提交订单，请尽快补充预存！"   
                            try:
                                touser = order.client.wx_id
                                send_wx_message(touser,content)
                                request_tool.set_message("支付成功")
                            except:
                                request_tool.set_message("支付成功，因网络延迟发送微信消息失败")
                            #20171026添加判断是否传单部分
                            if order.state=='paid':
                                if order.insurance_product.create_way == 'hjb' and not order.third_paper_id:
                                    try:
                                        send_wx_message(gly_wx,'进入汇聚宝传值')
                                    except:
                                        pass
                                    try:
                                        order_pass_detail=order_pass_test(request, order.id)
                                        if order_pass_detail !='success':
                                            try:
                                                content1 = "用户订单:"+str(order.id)+"已经成功支付!提交汇聚宝过程出错注意查看。出错信息："+str(order_pass_detail)
                                                send_wx_message(gly_wx,content1)
                                            except:
                                                request_tool.set_message("支付成功，提交信息出错请联系管理员")
                                            
                                    except Exception as e :
                                        content1 = "用户订单:"+str(order.paper_id)+"已经成功支付!提交汇聚宝过程出错注意查看。出错信息："+str(e)
                                        try:
                                            send_wx_message(gly_wx,content1)
                                        except:
                                            pass
                            #判断是否传单部分结束
                        else:
                            request_tool.set_message('余额不足，预存余额为{0}元，您至少还须预存{1}元，预存成功后请到“我的”--“我的订单”中选择该订单进行支付'.format(order.client.balance/100, (order.price-order.client.balance)/100))
                            return HttpResponseRedirect(reverse('wss:warn'))
                else:
                    request_tool.set_message('密码错误，请重新输入')
                    return HttpResponseRedirect(reverse('wss:order_pay_update', args=[order.id, ]))
            else:
                request_tool.set_message('密码不能为空')
                return HttpResponseRedirect(reverse('wss:order_pay_update', args=[order.id, ]))

        except CustomError as e:
            data['message'] = e.message
            return render_to_response('wss/insure/order_pay_update.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('wss/insure/order_pay_update.html', data, context)
        return HttpResponseRedirect(reverse('wss:order_detail_update', args=[order.id, ]))
    elif request.method == 'GET':
        return render_to_response('wss/insure/order_pay_update.html', data, context)
    
    
    
#2017/11/28 完善众安订单信息
def add_za_order_detail(request):
    data = {}
    wss_tools = DocumentWssTools(request)
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
        return  JsonResult(data=data, code=CODE_ERROR, message='网络问题未找到订单信息.').response()
    if order_test.state !='wait':
            return  JsonResult(data=data, code=CODE_ERROR, message='订单状态不正确，请退出后重新进入订单列表').response()
    else:
        try:
            order = wss_tools.wss_validation_za_order(order_test)
            order.save()
        except ParameterError as e:
            message = e.message
            return  JsonResult(data=data, code= CODE_ERROR, message=message).response()
        except CustomError as e:
            message = e.message
            return  JsonResult(data=data, code= CODE_ERROR, message=message).response()
        except Exception as e:
            message = e.message
            return  JsonResult(data=data, code= CODE_ERROR, message=message).response()
        return JsonResult(data=data, code=CODE_SUCCESS).response()
    
    