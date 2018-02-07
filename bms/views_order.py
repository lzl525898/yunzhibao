__author__ = 'mlzx'
import hashlib
from django.views.decorators.csrf import csrf_exempt
###################################test
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render,render_to_response  
from django.template import RequestContext 
from rest_framework import request  
from rest_framework import permissions  
from rest_framework.response import Response  
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes  
import urllib
#################################testend
from django.contrib.auth.decorators import login_required
from common.decorators import AdminRequired
from common.decorators import SuperAdminRequired
from django.shortcuts import HttpResponseRedirect
from mongoengine.django.auth import User, make_password
# from common.tools_legoo import *
from common.tools import *
from bms.tools import DocumentBmsTools,validation_create_order_list
from django.shortcuts import HttpResponse
import traceback
import math
from common.tools_legoo import DocumentTools, DocumentFolderType, ImageTools, ImageFolderType
from common.tools import RequestTools
from common.tools_excel_export import ExcelExportTools
# from openpyxl.reader.excel import load_workbook
# import openpyxl
from django.contrib.staticfiles.templatetags.staticfiles import static
from wss.views_sendmessage import  send_wx_message
import datetime
import time
from pss.views_zhongan import ZhongAnApi
from django.conf import settings
############################测试未提交订单
from wss.tools import DocumentWssTools
#批量上传订单
import os, base64
#发送微信
from common import tools_string
#发送短信
import common.tools_m5c_sms as m5c_sms_helper
from common.models import SiteSettings
#－－－－－－－－－－－－－－－－－－－－－－－－－－     订单列表      －－－－－－－－－－－－－－－－－－－－－－－－－－


@login_required
@AdminRequired
def order_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_order'] = search_keyword
        start_time = request.POST.get('start_time', '')
        request.session['start_time'] = start_time
        end_time = request.POST.get('end_time', '')
        request.session['end_time'] = end_time
        request.session['page_index_order'] = 1
        state = request_tool.get_parameter("state")
        pay_state = request_tool.get_parameter("pay_state")
        user_type = request_tool.get_parameter("user_type")
        id_client = request_tool.get_parameter("client_sign")
        get_parameter = "?state={0}&pay_state={1}&user_type={2}&id_client={3}".format(state, pay_state, user_type, id_client)
        return HttpResponseRedirect(reverse('bms:order_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_order', '')
        order_set = Ordering.objects()
        order_set = request_tool.order_filter(order_set=order_set, keyword=search_keyword)
        count = order_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_order'] = paging['page_index']
        order_set = order_set[paging['start_item']:paging['end_item']]

        user_type = request_tool.get_parameter("user_type", '')
        if user_type:
            client_set = Client.objects().filter(user_type=user_type)
        else:
            client_set = Client.objects()
        #2017修改用户流程
        user_set = User.objects(is_active=True)
        client_set = client_set.filter(user__in=user_set)
        count1=client_set.count()
#             client_set = Client.objects().filter(user_type__ne='registered')
        data['clients'] = client_set
        data['orders'] = order_set
        data['search_keyword'] = search_keyword
        data['start_time'] = request.session.get('start_time', '')
        data['end_time'] = request.session.get('end_time', '')
        request.session['start_time'] = ''
        request.session['end_time'] = ''
        data['paging'] = paging
        return render_to_response('bms/order/order_list.html', data, context)


@login_required
@AdminRequired
def order_detail(request, order_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    order = Ordering.objects(id=order_id).first()
    print(type(order.expectStartTime))
    # order.pay_time = '2015-02-05 15:45:36'
    # order.save()
    # order.reload()
    if order:
        data['order'] = order
        i=0
        temp=[]
        temp2=[]
        for insurance_image in order.insurance_image_list:
            i=i+1
            temp.append(insurance_image)
            if i%4 == 0:
                temp2.append(temp)
                print(temp2)
                temp=[]
        temp2.append(temp)
        data["insurance_image_list"]=temp2
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:order_list', args=[page_index, ]))
    if order.state == 'wait':
        #实时筛选订单可保护信息
        wss_tools = DocumentWssTools(request)
        insurable_products_list=[]
        message=''
        try:
            insurable_products_list=wss_tools.wss_validation_insurable_products(order)
        except ParameterError as e:
            message= e.message
        except CustomError as e:
            message = e.message
        except Exception as e:
            message = str(e)
        data['message']=message
        if len(insurable_products_list)==0:
            data['product_detail']='实时询价结果未筛出合适产品，原因：'+str(message)
        else:
            data['product_detail']='实时询价共筛出'+str(len(insurable_products_list))+'款产品可保'
            data['insurable_products_list']=insurable_products_list
        
    return render_to_response('bms/order/order_detail.html', data, context)


@login_required
@AdminRequired
def order_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    company_set = InsuranceCompany.objects(is_hidden=False)
    #2017修改用户流程
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    count1=client_set.count()
    
#     client_set = Client.objects().filter(user_type__ne='registered')
    product_set = InsuranceProducts.objects()
    product_type = InsuranceProducts.PRODUCT_TYPE
    order = Ordering()
    bms_tools.check_message(data)
    cargo_area_list = CargoArea.objects()
    data['cargo_area_list'] = cargo_area_list
    data['companys'] = company_set
    data['clients'] = client_set
    data['product_types'] = product_type
    data['insurance_products'] = product_set
    data['transport_list']=order.TRANSPORT_TYPE
    data['common_good_list']=order.COMMON_GOOD
    data['pack_method_list']=order.PACK_METHOD
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新","港","澳","台"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    batch_price_list=[]
    for num in range(1,51):
        a=num*100000
        b=str(num*10)+'万'
        batch_detail=(str(a), str(b))
        batch_price_list.append(batch_detail)
    data["batch_price_list"] = batch_price_list
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            order = Ordering()
            order = bms_tools.validation_order(order)
            if request.POST.get('active', '') == 'show':
                order.is_hidden = False
            else:
                order.is_hidden = True
            order.submit_style = 'input'
            order.save()
            ##########提交订单
            if order.product_type == "car":
#                 order.pay_money()
#                 order.save()
                    #自动扣款通知
                if order.state ==  'paid':
                            if int(order.client.balance/100)  >= 500:
                                 content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。"
                            else:
                                   content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。预存余额不足500，为了避免余额不足导致无法提交订单，请尽快补充预存！"   
                            touser = order.client.wx_id
                            #touser = "oYXlSwfedYTw0OtzfRy2SYpPrNE8"
                            #send_wx_message(touser,content)
                request.session['message'] = '创建成功'
                return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
            else:
                content = "恭喜！您的订单"+str(order.paper_id)+"已经创建成功，为了保障您的权益，请您及时付款。"
                touser = order.client.wx_id
                #send_wx_message(touser,content)
                request.session['message'] = '创建成功'
                return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))

        except CustomError as e:
            # request.session['message'] = e.message
            data['message'] =  e.message
            return render_to_response('bms/order/order_create.html', data, context)
        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('bms/order/order_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            # request.session['message'] = str(e)
            return render_to_response('bms/order/order_create.html', data, context)
#         else:
#             return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
        # return HttpResponseRedirect(reverse('bms:order_create'))

    elif request.method == 'GET':
        return render_to_response('bms/order/order_create.html', data, context)


@login_required
@AdminRequired
def order_edit(request, order_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    #需要改动
    order = Ordering.objects(id=order_id).first()
    #修改
    company_set = InsuranceCompany.objects(is_hidden=False)
    #2017修改用户流程
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    count1=client_set.count()
#     client_set = Client.objects().filter(user_type__ne='registered')
    product_set = InsuranceProducts.objects()
    product_type = InsuranceProducts.PRODUCT_TYPE
    bms_tools.check_message(data)
    cargo_area_list = CargoArea.objects()
    data['cargo_area_list'] = cargo_area_list
    data['companys'] = company_set
    data['clients'] = client_set
    data['product_types'] = product_type
    data['insurance_products'] = product_set
    data['transport_list']=order.TRANSPORT_TYPE
    data['common_good_list']=order.COMMON_GOOD
    data['pack_method_list']=order.PACK_METHOD
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新","港","澳","台"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    batch_price_list=[]
    for num in range(1,51):
        a=num*100000
        b=str(num*10)+'万'
        batch_detail=(str(a), str(b))
        batch_price_list.append(batch_detail)
    data["batch_price_list"] = batch_price_list
    
    if order:
        data['order'] = order
        data['batch_insurance_price'] =int(order.insurance_price/100)
        order_id1=order.id
        #分解车牌号
        data["short"]=""
        data["mid"]=""
        data["end"]=""
        if order.plate_number:
            try:
                a=order.plate_number
                short = order.plate_number[0]
                mid = order.plate_number[2]
                end = order.plate_number[3:]
                data["short_number"]=short
                data["mid_number"]=mid
                data["end_number"]=end
            except:
                pass
        #翻译起运地
        startSiteName_detail = order.startSiteName.split(" ")
        print(startSiteName_detail)
        count = len(startSiteName_detail)
        data["start_prov"] = ""#省
        data["start_city"] = ""#市
        data["start_dis"] = ""#县
        for i in range(count):
            name_code = startSiteName_detail[i]
            print( i )
            print( name_code )
            if i == 0:
                data["start_prov"] = name_code
            if i == 1 :
                data["start_city"] = name_code
            if i == 2 :
                data["start_dis"] = name_code
                #翻译目的地
        targetSiteName_detail = order.targetSiteName.split(" ")
        print(targetSiteName_detail)
        count1 = len(targetSiteName_detail)
        data["target_prov"] = ""#省
        data["target_city"] = ""#市
        data["target_dis"] = ""#县
        for i in range(count1):
            name_code1 = targetSiteName_detail[i]
            print( i )
            print( name_code1 )
            if i == 0:
                data["target_prov"] = name_code1
            if i == 1 :
                data["target_city"] = name_code1
            if i == 2 :
                data["target_dis"] = name_code1
                      
        #包装方式回显
        if order.product_type == "ticket":
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
                request.session['message'] =  order.pack_method+"未找到订单对应的包装方式"
                return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
            #货物类型回显
            product_cargo_list = ProductCargo.objects(product = order.insurance_product , state = order.good_type)
            if product_cargo_list:
                data["product_cargo_list"] = product_cargo_list
            else:
                request.session['message'] =  order.pack_method+"未找到订单对应的货物小类"
                return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    else:
        request.session['message'] = '未找到对应的保单信息'
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
   
    if request.method == 'POST':
        try:
            order = bms_tools.validation_order(order)
            if request.POST.get('active', '') == 'show':
                order.is_hidden = False
            else:
                order.is_hidden = True
            order.save()
            request.session['message'] = '编辑成功'
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/order/order_edit.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/order/order_edit.html', data, context)
    
    
#向汇聚宝传单
def order_pass(request, order_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    order = Ordering.objects(id=order_id).first()
    try:
        order_pass_detail=order_pass_test(request, order.id)
        if order_pass_detail !='success':
            bms_tools.set_message(order_pass_detail)
    except Exception as e :
        message= str(e)
        bms_tools.set_message(message)
    except ParameterError as e:
        message= str(e)
        bms_tools.set_message(message)
    return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))

#向汇聚宝传单过程测试
def order_pass_test(request, order_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    order = Ordering.objects(id=order_id).first()
    gly_wx='oqgGUvz6B64uBI5oa8Z23yV8M_xM'
    try:
        send_wx_message(gly_wx,'进入支付状态测试步骤100')
    except:
        pass
    if order.state !='paid':
        raise ParameterError('订单未支付不能传值')
    if order.state=='paid':
    #*******************************test***************************************************
            #2017/5/23向汇聚宝传单
        a=order.insurance_product.create_way
        if order.insurance_product.create_way == 'hjb':
            if order.third_paper_id:
                raise ParameterError('订单已经提交不能二次上传')
            post_url_list={}
            #单票车次公共部分
            try:
                extraInfo_detail={}
                extraInfo_detail["holderName"]=str(order.client_name)#.投保人姓名
                extraInfo_detail["holderPhone"]=str(order.client.profile.phone)#投保人手机号
                extraInfo_detail["insureName"]=str(order.insured )#.被保人姓名
                extraInfo_detail["channelOrderNo"]=str(order.paper_id)#渠道订单号
                order_price = float(order.insurance_price)/100
                if order_price<1000.0:
                    order_price=1000.0
                extraInfo_detail["coverage"]=str(order_price)#.保险金额
                extraInfo_detail["loadType"]="非集装箱"#.encode("utf8")说定写死的字段
            except Exception as e:
                message=str(e)+'\n'
                raise ParameterError(str(e))
            #起运地
            try:
                address_number = order.startSiteName
                name_detail = address_number.split(" ")
                prov_name = ''
                city_name = ''
                dist_name = ''
                number1=len(name_detail)
                prov_name = CargoArea.objects(code=name_detail[0]).first().name
                city_name = CargoArea.objects(code=name_detail[1]).first().name
                #2017-09-19添加众安传值code
                startSite_code = CargoArea.objects(code=name_detail[1]).first().code
                if number1>2:
                    dist_name = CargoArea.objects(code=name_detail[2]).first().name
            except Exception as e:
                message=str(e)
                raise ParameterError(message)
            #目的地
            try:
#                 address_number2 = order.targetSiteName
#                 name_detail2 = address_number2.split(" ")[0]
#                 prov_name2 = CargoArea.objects(code=name_detail2).first().name
#                 extraInfo_detail["destination"]= str(prov_name2)#.encode("utf8")
                
                address_number2 = order.targetSiteName
                name_detail2 = address_number2.split(" ")
                prov_name2 = ''
                city_name2 = ''
                dist_name2 = ''
                number2=len(name_detail2)
                prov_name2 = CargoArea.objects(code=name_detail2[0]).first().name
                city_name2 = CargoArea.objects(code=name_detail2[1]).first().name
                #2017-09-19添加众安传值code
                targetSite_code = CargoArea.objects(code=name_detail2[1]).first().code
                if number2>2:
                    dist_name2 = CargoArea.objects(code=name_detail2[2]).first().name
                
                
            except Exception as e:
                message=str(e)
                raise ParameterError(message)
            #判断目的地和起运地是否一致
            test_city=0
            if prov_name2 !=prov_name:
                departure= str(prov_name)
                destination= str(prov_name2)
            else:
                if city_name2 !=city_name:
                    departure=  str(city_name)
                    destination= str(city_name2)
                else:
                    test_city=3
                    departure=  str(city_name) + str(dist_name)
                    destination= str(city_name2) + str(dist_name2)
            if len(departure)>10:
                if test_city==3:
                    departure=dist_name[0:9]
                else:
                    departure =departure[0:9]
            if len(destination)>10:
                if test_city==3:
                    destination=dist_name2[0:9]
                else:
                    destination =destination[0:9]
                    
            extraInfo_detail["departure"]=departure
            extraInfo_detail["destination"]=destination
            #2017-09-19添加众安传值code
            extraInfo_detail["departureCode"]=str(startSite_code)
            extraInfo_detail["destinationCode"]=str(targetSite_code)
            
            
            
            try:
#                     extraInfo_detail["expectStartTime"]= str(20170623150623)
#                     expectStartTime = order.pay_time.strftime('%Y%m%d%H%M%S');
                expectStartTime = (datetime.datetime.now()-datetime.timedelta(minutes=-2))
                expectStartTime   =expectStartTime.strftime('%Y%m%d%H%M%S');  
                extraInfo_detail["expectStartTime"]=expectStartTime
            except:
                message=str(e)
                raise ParameterError(message)
            #单票车次区分值
            if order.insurance_product.product_type == 'batch' :
                extraInfo_detail["transportType"]='汽运'#运输方式
                extraInfo_detail["packType"]='裸装'#包装方式
                extraInfo_detail["goodsType"]='轻工品类'#.货物大类
                extraInfo_detail["goodsName"]='百货（普通货物）'#.货物名称
                extraInfo_detail["goodsAmount"]= '整车'#.货物数量
                extraInfo_detail["carNo"]= str(order.plate_number).replace(' ','')#车牌号
                #2017/12/01添加众安传值
                if "众安" in  order.insurance_product.company.parent.description:
                    extraInfo_detail["freightNo"]= "待定"#运单号
                    if order.tb_client_type=="company":
                        extraInfo_detail["holderType"]='201'#投保人类型
                    elif order.tb_client_type=="person":
                        extraInfo_detail["holderType"]='100'#投保人类型
                    else:
                        message='众安保险传值所需投保人类型不正确，请查看信息'+str(order.tb_client_type)
                        raise ParameterError(message)
                    extraInfo_detail["taxpayerRegNum"]=str(order.taxpayerRegNum)#投保人纳税人识别号
                    extraInfo_detail["holderCertType"]=str(order.tb_holderCertType)#投保人证件类型
                    extraInfo_detail["holderCertNo"]=str(order.holderCertNo)#投保人证件号
                    extraInfo_detail["insureCertType"]=str(order.bb_insureCertType)#被保人证件类型
                    extraInfo_detail["insureCertNo"]=str(order.bb_insureCertNo)#被保人证件号
                    extraInfo_detail["trailerNo"]=str(order.plate_number_plus)#挂车牌号
                
            elif order.insurance_product.product_type == 'ticket' :
                #2017/12/01添加众安传值
                if "众安" in  order.insurance_product.company.parent.description:
                    if order.tb_client_type=="company":
                        extraInfo_detail["holderType"]='201'#投保人类型
                    elif order.tb_client_type=="person":
                        extraInfo_detail["holderType"]='100'#投保人类型
                    else:
                        message='众安保险传值所需投保人类型不正确，请查看信息'+str(order.tb_client_type)
                        raise ParameterError(message)
                extraInfo_detail["taxpayerRegNum"]=str(order.taxpayerRegNum)#投保人纳税人识别号
                extraInfo_detail["holderCertNo"]=str(order.holderCertNo)#投保人证件号
                if order.transport_id:
                    extraInfo_detail["freightNo"]= str(order.transport_id)#运单号
                else:
                    extraInfo_detail["freightNo"]= "待定"#运单号
                if order.plate_number:
                    extraInfo_detail["carNo"]= str(order.plate_number).replace(' ','')#车牌号
                else:
                    extraInfo_detail["carNo"]= "待定"#车牌号
                #运输方式翻译
                try:
                    transport_type1=order.transport_type
                    transport_type_list1=order.TRANSPORT_TYPE
                    name = ""
                    test =0
                    for transport_type in transport_type_list1:
                        if transport_type[0]==order.transport_type:
                            name=transport_type[1]
                            test=1
                            break
                    if test ==1:
                        extraInfo_detail["transportType"]=str(name)
                    else:
                        message='传值过程中运输方式翻译失败，请查看运输编号'+str(order.transport_type)
                        raise ParameterError(message)
#                         extraInfo_detail["transportType"]="汽运"#.encode("utf8")
                except:
                    message='传值过程中运输方式翻译失败，请查看运输编号'+str(order.transport_type)
                    raise ParameterError(message)
                
                #包装方式
                try:
                    pack_method_list=order.PACK_METHOD
                    test =0
                    pack_method_detail = ''
                    for pack_method in pack_method_list:
                        for pack_detail in pack_method[1]:
                            if pack_detail[0]==order.pack_method:
                                test=1
                                break
                        if test==1:
                            pack_method_detail=pack_method[0][0]
                            break
                    if pack_method_detail:
                         extraInfo_detail["packType"]=str(pack_method_detail)
                    else:
                        raise ParameterError('未翻译出包装方式大类，小类码是：'+str(order.pack_method))
                except Exception as e:
                    message=str(e)+'\n'
                    raise ParameterError(message)
                try:
                    #20170714添加货物大类分类
                    cargo_name_detail = str(order.cargo.cargo_name)
                    qgpl=["家具（非红木家具）","药品（疫苗，须冷藏冷冻除外）","易碎品货物","二手货","其他普通货物"]
                    jxsbl = ["二手车","商品车"]
                    if "水果"  in cargo_name_detail:
                        cargo_name_detail = '农产品土畜产类'
                    elif cargo_name_detail in qgpl:
                        cargo_name_detail = '轻工品类'
                    elif cargo_name_detail in jxsbl:
                        cargo_name_detail = '机械设备类'
                    extraInfo_detail["goodsType"]=cargo_name_detail#.货物大类
                    extraInfo_detail["goodsName"]=str(order.commodityName)#.货物名称
                    extraInfo_detail["goodsAmount"]= str(order.commodityCases)#.货物数量
                except Exception as e:
                    message=str(e)
                    raise ParameterError(message)
            else:
                 raise ParameterError('需要传值的订单类型不正确') 
            try:
                post_url_list["productCode"] = str(order.insurance_product.third_product_number)
                post_url_list["channelId"] = str(order.insurance_product.merchant_number)
                post_url_list["channelOrderNo" ] = str(order.paper_id)
                host = request.get_host()#2017-08-21添加自动获取域名部分
                post_url_list["notifyUrl"]="http://"+host+"/bms/order/change_order_state/"
                post_url_list["extraInfo"] = str(extraInfo_detail)
                data_test = urllib.parse.urlencode(post_url_list)
                data_test = data_test.encode('utf-8')
                headers = { 
                "contentType" : "application/x-www-form-urlencoded;charset=utf-8"
                 }
                #params=urllib.parse.urlencode(post_url_list).encode(encoding='UTF8')
                url_post= str(order.insurance_product.third_party_url)
                req = urllib.request.Request(url_post, data_test,headers)
                r = urllib.request.urlopen(req)
                res=r.read().decode('utf8')  
                data['message']=str(res)
                jsonO = json.loads(res)
                a=jsonO['isSuccess']
                if jsonO['isSuccess']=='Y':
                    order.note_detail='投保成功'
                    order.third_paper_id= str(jsonO['sysOrderNo'])
                    order.save()
                else:
                    order.note_detail='投保失败，错误代码：'+str(jsonO['errCode'])+str(jsonO['errMsg'])+str(jsonO['channelOrderNo'])
                    order.save()
                    try:
                        send_wx_message(gly_wx,str(post_url_list))
                    except:
                        pass
                        
                    return order.note_detail
            except Exception as e:
                data['message']=str(e)+'\n' +str(post_url_list)
                order.note_detail=str(e)+'\n' +'url_post------'+str(url_post)+'------detail----'+str(post_url_list)
                order.save()
            return 'success'

#*******************************testend***************************************************
    
#付款
@login_required
@AdminRequired
def order_pay(request, order_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    order = Ordering.objects(id=order_id).first()
    if order:
        data['order'] = order
    else:
        request.session['message'] = '未找到对应的保单'
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    if order.state=='paid':
        request.session['message'] = '用户支付成功请勿二次支付'
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    if request.method == 'POST':
        try:
            #touser = order.client.wx_id
            #send_wx_message(touser,"进入付款部分")
            pay_order = bms_tools.get_parameter('order_confirm_id')
            if pay_order:
                pay_order = int(pay_order)
                if order.client.balance >= order.price:
                    order.pay_money()
                    order.save()
                    #确定支付成功通知 
                    if int(order.client.balance/100)  >= 500:
                         content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。"
                    else:
                           content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。预存余额不足500，为了避免余额不足导致无法提交订单，请尽快补充预存！"   
                    try:
                        touser = order.client.wx_id
                        send_wx_message(touser,content)
                        bms_tools.set_message('付款成功')
                    except:
                        bms_tools.set_message('付款成功,网络问题或该用户未关注公众号，微信通知发送失败')
                else:
                    bms_tools.set_message('您操作的用户余额不足，请通知用户缴纳保费')
            else:
                bms_tools.set_message('货物价值不能为空')
        except CustomError as e:
            data['message'] = e.message
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
        except ValueError as e:
            bms_tools.set_message('货物价值只能为正整数')
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
        except Exception as e:
            bms_tools.set_message(str(e))
            message=str(e)
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
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
            payment_statistical.state = 'ht_price'
            payment_statistical.save()
        except Exception as e :
            message= str(e)
            bms_tools.set_message(message)
        if order.state=='paid':
            if order.insurance_product.create_way == 'hjb':
                try:
                    order_pass_detail=order_pass_test(request, order.id)
                    if order_pass_detail !='success':
                        bms_tools.set_message(order_pass_detail)
                except Exception as e :
                    message= str(e)
                    bms_tools.set_message(message)
                except ParameterError as e:
                    message= str(e)
                    bms_tools.set_message(message)
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    elif request.method == 'GET':
        return render_to_response('bms/order/order_detail.html', data, context)


# 修改投保人
@login_required
@AdminRequired
def edit_insured(request, order_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    order = Ordering.objects(id=order_id).first()
    if order:
        data['order'] = order
    else:
        request.session['message'] = '未找到对应的保险公司'
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    if request.method == 'POST':
        try:
            insured = bms_tools.get_parameter('edit_insured')
            if insured:
                order.insured = insured
                order.save()
                bms_tools.set_message('被投保人的姓名修改成功')
            else:
                bms_tools.set_message('被投保人不能为空')
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            bms_tools.set_message(str(e))
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    elif request.method == 'GET':
        return render_to_response('bms/order/order_detail.html', data, context)


@login_required
@AdminRequired
def import_insurance(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    search_keyword = request_tool.get_parameter('search_keyword', '')
    start_time = request.POST.get('start_time', '')
    request.session['start_time'] = start_time
    end_time = request.POST.get('end_time', '')
    request.session['end_time'] = end_time
    state = request_tool.get_parameter("state")
    pay_state = request_tool.get_parameter("pay_state")
    user_type = request_tool.get_parameter("user_type")
    id_client = request_tool.get_parameter("client_sign")
    request.session['search_keyword_order'] = search_keyword
    request.session['page_index_order'] = 1
    get_parameter = "?state={0}&pay_state={1}&user_type={2}&id_client={3}".format(state, pay_state, user_type, id_client)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            image_tool = ImageTools()
            order_set = Ordering.objects()
            order_set = request_tool.order_filter(order_set=order_set, keyword=search_keyword)
            for order in order_set:
                if order.state == 'paid':
                    insurance_image_list = request.FILES.getlist('insurance_image_list', '')
                    insurance_id = request_tool.get_parameter('insurance_id', '')
                    temp = []
                    if insurance_image_list:
                        for insurance_image in insurance_image_list:
                            order_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
                            if not order_image_url:
                                request_tool.set_message(order.paper_id+'生成图片地址失败')
                                return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]) + get_parameter)
                            else:
                                temp.append(order_image_url)
                    else:
                        request_tool.set_message('导入失败，请填入保单图片')
                        return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]) + get_parameter)

                    order.insurance_id = insurance_id
                    order.insurance_image_list = temp
                    order.state = 'done'
                    order.save()
                else:
                    request_tool.set_message(order.paper_id+'订单的状态不正确')
                    return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]) + get_parameter)
            request_tool.set_message('导入成功')
            return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]))
        except CustomError as e:
            request_tool.set_message(e.message)
        except Exception as e:
            print(traceback.format_exc())
            request_tool.set_message(str(e))
        return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]) + get_parameter)


# 添加保单号
@login_required
@AdminRequired
def add_insurance_pic(request, order_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    bms_tools = DocumentBmsTools(request)
    order = Ordering.objects(id=order_id).first()
    if not order:
        request_tools.set_message("未找到对应订单")
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    if order.state == 'init':
        request_tools.set_message("要增加的订单状态不正确")
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    if request.method == 'POST':
        try:
            image_tool = ImageTools()
            insurance_image_list = request.FILES.getlist('add_insurance_image_pic', '')
            insurance_id = request_tools.get_parameter('insurance_id', '')
            if insurance_image_list:
                for insurance_image in insurance_image_list:
                    order_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
                    if not order_image_url:
                        request_tools.set_message(order.paper_id+'生成图片地址失败')
                        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
                    else:
                        order.insurance_image_list.append(order_image_url)
            else:
                request_tools.set_message('导入失败，请填入保单图片')
                return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
            order.insurance_id = insurance_id
            order.picture_upload_path = 'yzb'
            order.state = 'done'
            order.save()
            #订单生成通知用户信息
            crteamtop = request.get_host()
            order_url = "http://"+crteamtop+reverse('wss:order_detail', args=[order_id, ])
            orderinsurance_id = order.insurance_id
            orderpaper_id = order.paper_id
            request_tools.set_message("操作成功")
            content ="您的订单"+str(orderpaper_id)+"的保单已经上传，保单号为：<a href = '"+order_url+"'>"+str(orderinsurance_id)+"</a>,在我的订单中查看订单状态，如有疑问请联系运之宝客服，电话：15910731868"
            touser = order.client.wx_id
            send_wx_message(touser,content)
            
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
        except ParameterError as e:
            # 初始化错误信息
            request_tools.set_message(e.message)
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
    elif request.method == 'GET':
        request_tools.check_message(data)
        data['order'] = order
        data['order_id'] = order_id
        return render_to_response('bms/order/order_detail.html', data, context)




# 修改保单图片
@login_required
@AdminRequired
def edit_insurance_pic(request, order_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    bms_tools = DocumentBmsTools(request)
    order = Ordering.objects(id=order_id).first()
    if order:
        try:
            order = bms_tools.validation_edit_pic(order=order)
            order.save()
            # 创建成功
            request.session['message'] = '编辑成功'
        except ParameterError as e:
            request.session['message'] = '编辑图片失败:{0}'.format(e.message)
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
    else:
        request.session['message'] = '未找到对应订单'
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
    
    
    #删除保单图片
def delete_insurance_pic(request, order_id):
    context = RequestContext(request)
    image_url = request.POST.get('image_detail_url_delete', '')
    if image_url:
        try:
            image_tools = ImageTools()
            image_tools.delete(image_url)
            order = Ordering.objects(id=order_id).first()
            order.insurance_image_list.remove(image_url)
            order.save()
        except Exception as e:
            request.session['message'] = '删除失败：{0}'.format(e)
    else:
        request.session['message'] = '未找到对应图片'
    return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))





# 修改车次图片
@login_required
@AdminRequired
def edit_batch_pic(request, order_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    bms_tools = DocumentBmsTools(request)
    order = Ordering.objects(id=order_id).first()
    if order:
        try:
            order = bms_tools.validation_edit_batch_pic(order=order)
            order.save()
            # 创建成功
            request.session['message'] = '编辑成功'
        except ParameterError as e:
            request.session['message'] = '编辑图片失败:{0}'.format(e.message)
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
    else:
        request.session['message'] = '未找到对应订单'
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))


    #删除车次图片
def delete_batch_pic(request, order_id):
    context = RequestContext(request)
    image_url = request.POST.get('image_batch_url_delete', '')
    if image_url:
        try:
            image_tools = ImageTools()
            image_tools.delete(image_url)
            order = Ordering.objects(id=order_id).first()
            order.batch_image_list.remove(image_url)
            order.save()
        except Exception as e:
            request.session['message'] = '删除失败：{0}'.format(e)
    else:
        request.session['message'] = '未找到对应图片'
    return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))



# 添加车次清单列表
@login_required
@AdminRequired
def add_batch_list(request, order_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    bms_tools = DocumentBmsTools(request)
    order = Ordering.objects(id=order_id).first()
    if not order:
        request_tools.set_message("未找到对应订单")
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    if request.method == 'POST':
        try:
            order = bms_tools.validation_batch_list(order=order, request=request)
            order.save()
            request_tools.set_message("添加车次清单成功")
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
        except ParameterError as e:
            # 初始化错误信息
            request_tools.set_message(e.message)
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
    elif request.method == 'GET':
        request_tools.check_message(data)
    data['order'] = order
    data['order_id'] = order_id
    return render_to_response('bms/order/order_detail.html', data, context)

# 编辑车次清单
@login_required
@AdminRequired
def edit_batch_list(request, order_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    bms_tools = DocumentBmsTools(request)
    order = Ordering.objects(id=order_id).first()
    if not order:
        request_tools.set_message("未找到对应商品")
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    if request.method == 'POST':
        try:
            order = bms_tools.validation_batch_edit(order=order, request=request)
            order.save()
            request.session['message'] = '编辑车次清单成功'
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
        except ParameterError as e:
            # 初始化错误信息
            request.session['message'] = e.message
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
    elif request.method == 'GET':
        request_tools.check_message(data)
    data['order'] = order
    data['order_id'] = order.id
    return render_to_response('bms/order/order_detail.html', data, context)


#删除车次清单
@login_required
@AdminRequired
def delete_batch_list(request, order_id):
    context = RequestContext(request)
    order = Ordering.objects(id=order_id).first()
    temp = None
    if order:
        yd = request.POST.get('batch_list_name', '')
        for batch in order.batch_list:
            if batch.transport_id == yd:
                temp = batch
        if temp:
            order.batch_list.remove(temp)
            order.save()
        else:
            raise ParameterError('找不到要删除的货物清单')
    else:
        request.session['message'] = '没有找到对应的订单'
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))


# 屏蔽保单
@login_required
@AdminRequired
def order_hidden(request, order_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    order = Ordering.objects(id=order_id).first()
    if order:
        if order.is_hidden:
            order.is_hidden = False
        else:
            order.is_hidden = True
        order.save()
    else:
        request.session['message_order'] = '未找到对应的保单'
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))



@login_required
@AdminRequired
def order_export(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    search_keyword = request_tool.get_parameter('search_keyword', '')
    state = request_tool.get_parameter("state")
    pay_state = request_tool.get_parameter("pay_state")
    user_type = request_tool.get_parameter("user_type")
    id_client = request_tool.get_parameter("client_sign")
    request.session['search_keyword_order'] = search_keyword
    request.session['page_index_order'] = 1
    get_parameter = "?state={0}&pay_state={1}&user_type={2}&id_client={3}".format(state, pay_state, user_type, id_client)
    try:
        start_time = request.POST.get('start_time', '')
        request.session['start_time'] = start_time
        end_time = request.POST.get('end_time', '')
        request.session['end_time'] = end_time

        order_set = Ordering.objects()
        order_set = request_tool.order_filter(order_set=order_set, keyword=search_keyword)
        if order_set:
            export_tools = ExcelExportTools()
            file_url = export_tools.export(order_set, Ordering.INSURANCE_FIELD_TUPLE)
            print(file_url)
            url = static('/static/'+file_url)
            # request_tool.set_message('导出成功')
            return HttpResponseRedirect(url)
        else:
            request_tool.set_message('没有找到要导入的订单')
            return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]) + get_parameter)
    except CustomError as e:
        request_tool.set_message(e.message)
    except Exception as e:
        print(traceback.format_exc())
        request_tool.set_message(str(e))
    return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]) + get_parameter)

@csrf_exempt 
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def change_order_state(request):
    context = RequestContext(request)
    data={}
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    touser = 'oqgGUvz6B64uBI5oa8Z23yV8M_xM'
    if request.method == 'POST':
        SYS_ORDER_NO=""
        CHANNEL_ORDER_NO = ''#渠道商户订单号
        POLICY_NO =''#保单号
        DOC_URL = ''#电子保单下载地址
        try:
            SYS_ORDER_NO = request.POST.get('SYS_ORDER_NO', '')#系统内部订单号（汇聚宝）
            CHANNEL_ORDER_NO = request.POST.get('CHANNEL_ORDER_NO', '')#渠道商户订单号（运至宝）
            POLICY_NO = request.POST.get('POLICY_NO', '')#保单号
            DOC_URL = request.POST.get('DOC_URL', '')#电子保单下载地址
        except Exception as e:
            message="40091"+str(e)+'--------'
            send_wx_message(touser,message)
    else:
        SYS_ORDER_NO = request.GET.get('SYS_ORDER_NO', '')
        CHANNEL_ORDER_NO = request.GET.get('CHANNEL_ORDER_NO', '')
        POLICY_NO = request.GET.get('POLICY_NO', '')
        DOC_URL = request.GET.get('DOC_URL', '')
    try:
        message="400191"+'--------'+SYS_ORDER_NO+'----------'+CHANNEL_ORDER_NO+'----------'+POLICY_NO+'----------'+DOC_URL
        send_wx_message(touser,message)
        order = Ordering.objects(third_paper_id=SYS_ORDER_NO,paper_id=CHANNEL_ORDER_NO).first()
        count= Ordering.objects(third_paper_id=SYS_ORDER_NO,paper_id=CHANNEL_ORDER_NO).count()
        if count ==0:
                message="错误码：40092，"
                send_wx_message(touser,message)
        if not order:
            message="40093"
            send_wx_message(touser,message)  
        order.insurance_id=POLICY_NO
        order.insurance_image_list=[str(DOC_URL)]
        order.picture_upload_path='hjb'
        order.state='done'
        order.note_detail='投保完成'
        order.save()
        return Response("success")  
    except Exception as e:
        print(traceback.format_exc())
        send_wx_message(touser,message)  
        
        
        
# 2017/10/29添加保单号的3种方式
@login_required
@AdminRequired
def add_insurance_pic_new(request, order_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    bms_tools = DocumentBmsTools(request)
    order = Ordering.objects(id=order_id).first()
    if not order:
        request_tools.set_message("未找到对应订单")
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    if order.state not in ['paid','done']:
        request_tools.set_message("要编辑的订单状态不正确")
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
    if request.method == 'POST':
        if order.state == 'done':
            #编辑状态清空原始信息
            order.insurance_image_list=[]
            order.insurance_id = ''#保存订单号
            order.insurance_up_state = ''#保存上传保单类别
        #提取信息
        try:
            insurance_id = request_tools.get_parameter('insurance_id', '')#订单号
            if not insurance_id:
                request_tools.set_message("请填写保单号码")
                return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
            insurance_type = request_tools.get_parameter('insurance_type', '')#保单状态
            if insurance_type == 'web_url':
                insurance_image_list = request.POST.get('insurance_image', '')
            else:
                insurance_image_list = request.FILES.getlist('insurance_image', '')
        except Exception as e:
            request_tools.set_message("提取保单信息出错："+str(e))
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
         #保单图片
        if insurance_type == 'picture':
            try:
                image_tool = ImageTools()
                if insurance_image_list:
                    for insurance_image in insurance_image_list:
                        order_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
                        if not order_image_url:
                            request_tools.set_message(order.paper_id+'生成图片地址失败')
                            return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
                        else:
                            order.insurance_image_list.append(order_image_url)
                else:
                    request_tools.set_message('导入失败，请填入保单图片')
                    return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
            except ParameterError as e:
                # 初始化错误信息
                request_tools.set_message(e.message)
                return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
        #pdf文件保存
        elif insurance_type == 'pdf':
                if insurance_image_list:
                    #交强险文档
                    liability_document_url=[]
                    for insurance_image in insurance_image_list:
                        document_tools = DocumentTools()
                        try:
                            file_url = document_tools.save(request_file=insurance_image, file_folder=DocumentFolderType.order, old_file='')
                        except Exception as e:
                            request_tools.set_message(str(e)+'保单文件上传失败')
                            return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
                        liability_document_url.append(file_url)
                    if not liability_document_url:
                        request_tools.set_message('生成保单文件地址失败')
                        return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
                    else:
                        order.insurance_image_list=liability_document_url
                else:
                    request_tools.set_message('请上传保单文件')
                    return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
        elif insurance_type == 'web_url':
                if insurance_image_list:
                    insurance_web_url = []
                    insurance_image_list = str(insurance_image_list)
                    insurance_web_url.append(insurance_image_list)
                    order.insurance_image_list = insurance_web_url
                else:
                    request.session['message'] = '请填写保单下载链接'
                    return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
        try:
            order.insurance_id = insurance_id#保存订单号
            order.insurance_up_state = insurance_type#保存上传保单类别
            order.picture_upload_path = 'yzb'
            order.state = 'done'
            order.save()
        except:
            request.session['message'] = '订单保存失败'
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
        try:
            #订单生成通知用户信息
            crteamtop = request.get_host()
            order_url = "http://"+crteamtop+reverse('wss:order_detail', args=[order_id, ])
            orderinsurance_id = order.insurance_id
            orderpaper_id = order.paper_id
            request_tools.set_message("操作成功")
            content ="您的订单"+str(orderpaper_id)+"的保单已经上传，保单号为：<a href = '"+order_url+"'>"+str(orderinsurance_id)+"</a>,在我的订单中查看订单状态，如有疑问请联系运之宝客服，电话：15910731868"
            touser = order.client.wx_id
            send_wx_message(touser,content)
        except:
            request.session['message'] = '未找到用户微信id'
            return HttpResponseRedirect(reverse('bms:order_detail', args=[order_id, ]))
        return HttpResponseRedirect(reverse('bms:order_detail', args=[order.id, ]))
        
    elif request.method == 'GET':
        request_tools.check_message(data)
        data['order'] = order
        data['order_id'] = order_id
        return render_to_response('bms/order/order_detail.html', data, context)
    
    
    
#批量创建订单
@login_required
@AdminRequired
def input_order_list(request):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    if request.method == 'POST':
        #上传文档
        order_create_file = request.FILES.get('order_create_file')
        old_file=''
        if order_create_file:
            try:
                document_tools = DocumentTools()
                order_create_file_url = document_tools.save(request_file=order_create_file, file_folder=DocumentFolderType.order, old_file=old_file )
                if not order_create_file_url:
                    request.session['message'] = '文件上传失败' 
                    return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]))
            except Exception as e:
                request.session['message'] = '文件上传失败，错误原因：' + str(e)
                return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]))
        else:
            request.session['message'] = '未找到需要创建的订单文件'
            return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]))
        
        #文件上传成功开始生成保单
        try:
            BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
            #host = request.get_host()
            file_url1=BASE_ROOT+'/static/'+order_create_file_url
            Result = validation_create_order_list(request,file_url1)
            a=Result['state'] 
            
            if Result['state'] == "success":
                request.session['message'] = Result['order_total'] + '，订单全部上传成功'
            else:
                if Result['fail_reason']:
                    request.session['message'] =Result['fail_reason']
                else:
                    request.session['message'] = Result['order_total'] + '，其中：'+Result['wrong_order_id'] +"\n"+Result['wrong_pay_state'] +"\n"+Result['wrong_order_detail']
                
        except CustomError as e:
            # request.session['message'] = e.message
            request.session['message'] =  str(e)
            return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]))
        except ParameterError as e:
            request.session['message'] =  str(e)
            return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]))
        except Exception as e:
            print(traceback.format_exc())
            request.session['message'] =  str(e)
            return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]))
        if Result['wrong_pay_state']:
            try:
                if Result['client_wx_id']:
                    touser = str(Result['client_wx_id'])
                    content= "您"+Result['wrong_pay_state']+"请及时支付。"
                    send_wx_message(touser,content)
                ad_content=str(Result['wrong_pay_state'])
                string_tools = tools_string.StringTools()
                ad_touser = string_tools.get_string("administrator_wx_id")
                send_wx_message(ad_touser,ad_content)
            except Exception as e:
                pass
            #发送短信
            try:
                if Result['client_phone']:
                    site_settings = SiteSettings.get_settings()
                    helper = m5c_sms_helper.SmsHelper(site_settings.meilian_username, site_settings.meilian_password, site_settings.meilian_api_key)
                    dx_content ="您"+Result['wrong_pay_state']+"请登陆公众号，及时支付。"
                    phone_number= str(Result['client_phone'])
                    helper.send_sms(phone_to=phone_number, content=dx_content)
            except Exception as e:
                 pass

    return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]))
    
    
