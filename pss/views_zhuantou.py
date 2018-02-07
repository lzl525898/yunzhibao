#物流接口
from builtins import isinstance
from _struct import pack

__author__ = 'mlzx'
from django.shortcuts import render,render_to_response  
from django.template import RequestContext  
from rest_framework import request  
from rest_framework import permissions  
from rest_framework.response import Response  
from rest_framework.decorators import api_view, permission_classes  
import json
import os 
import hashlib
from common.models import *
from pss.tools import DocumentPssTools
import time
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pss.views_zhongan import ZhongAnApi
from django.conf import settings
from datetime import timedelta
#test
from django.views.decorators.csrf import csrf_exempt
from wss.views_sendmessage import  send_wx_message
#20171025添加发送短信通知
import common.tools_m5c_sms as m5c_sms_helper
from common.tools import RequestTools
#分页
from common.tools import DocumentTools, PageTools






#立即投保接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def  zhuantou_immediate_insurance(request):
         pss_tools = DocumentPssTools(request)
         result = dict()
         document=dict()
         documentlist=[]
         message = {'code':"0000","message":"ok","state":"1"}   
         order = Ordering()
         if request.method == 'POST':
              access_token = request.POST.get('access_token', None)
         else:
              access_token = request.GET.get('access_token', None)
         if access_token == None:
             return Response(pss_tools.get_message_dict("400096", "未找到access_token参数","0"))  
         try:
             accessToken = AccessTokenApi.objects(token=access_token).first()
             if not accessToken:
                return Response(pss_tools.get_message_dict("400097","Invalid access token","0"))   
             if accessToken.is_expired():
                return Response(pss_tools.get_message_dict("400098","Access token expire","0"))
         except:
            return Response(pss_tools.get_message_dict("400099","Access token fail","0"))

         try:
             order = pss_tools.zhuantou_validation_order(order)
             if isinstance(order,dict):
                message = order
                return Response(message)
             else:
                
                order.save()
                if order.client.balance >=order.price:
                   order.client.balance -= order.price
                   order.client.save()
                   order.pay_money()
                   #order.state = "done"
                   order.save()
                
                
         except Exception as e:
                 print(e)
                 return Response(pss_tools.get_message_dict("400100", "数据库存储异常","0"))  
         if order.state == "init":
               result['state'] = "未支付"
               try:
                   touser = 'oYXlSwfedYTw0OtzfRy2SYpPrNE8'
                   content='订单号：'+order.paper_id+'的订单未付款，请联系平台对接管理员及时充值'
                   send_wx_message(touser,content)
               except:
                    pass
         elif order.state == "paid":
               result['state'] = "已支付"
         elif order.state == "done":
               result['state'] = "已完成"

         result['paper_id'] = str(order.paper_id)#运之宝订单号
         result['price'] = order.price#订单金额
         result['transport_id'] = order.transport_id#第三方运单号
         result['balance'] = order.client.balance#账户余额
         message['data'] = result
         return Response(message)  
     
     
#查看保单接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def  zhuantou_search_insurance(request):
         result = dict()
         document=dict()
         documentlist=[]
         images = dict()
         imagelist =  []
         message = {'code':"0000","message":"ok","state":"1"}   
         pss_tools = DocumentPssTools(request)

    #验证token
         if request.method == 'POST':
             paper_id = request.POST.get('paper_id', None)
             transport_id = request.POST.get('transport_id', None)
             access_token = request.POST.get('access_token', None)
         else:
             paper_id = request.GET.get('paper_id', None)
             transport_id = request.GET.get('transport_id', None)
             access_token = request.GET.get('access_token', None)
         if access_token == None:
             return Response(pss_tools.get_message_dict("400096", "未找到access_token参数","0"))  
         try:
             accessToken = AccessTokenApi.objects(token=access_token).first()
             if not accessToken:
                return Response(pss_tools.get_message_dict("400097","Invalid access token","0"))   
             if accessToken.is_expired():
                return Response(pss_tools.get_message_dict("400098","Access token expire","0"))
         except:
            return Response(pss_tools.get_message_dict("400099","Access token fail","0"))
        #验证token结束
         if paper_id == None:
             return Response(pss_tools.get_message_dict("400095", "未找到paper_id参数","0"))  
         if transport_id == None:
             return Response(pss_tools.get_message_dict("400094", "未找到transport_id参数","0"))  

         try:
             order = Ordering.objects(paper_id=paper_id,transport_id=transport_id).first()   
         except Exception as e:
                 print(e)
                 return Response(pss_tools.get_message_dict("400093", "查找失败请检查运单号和订单号","0"))  
         if not order:
            return Response(pss_tools.get_message_dict("400092", "未查找到对应订单","0")) 
         if order.product_type != 'car':
             return Response(pss_tools.get_message_dict("400091", "查找订单类型错误，只能查看运单保险","0")) 
         
         if order.state == "done":
            result['insurance_id'] =order.insurance_id
            for  image in order.insurance_image_list:
                images['url'] = "http://123.57.35.153/static/"+image
                imagelist.append(images)
            result['imagelist'] =imagelist           
         else:               
            result['imagelist'] ="处理中，请等待" 
            
         if order.state == "init":
               result['state'] = "未支付"
         elif order.state == "paid":
               result['state'] = "已支付"
         elif order.state == "done":
             result['state'] = "已完成"

         result['paper_id'] = str(order.paper_id)#运之宝订单号
         result['price'] = order.price#订单金额
         result['transport_id'] = order.transport_id#第三方运单号
         message['data'] = result
         return Response(message)  

#最近版本接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,)) 
def zhuantou_insurance_create(request):
    result = dict()
    message = {'code':"0000","message":"ok","state":"1"}   
    pss_tools = DocumentPssTools(request)
    request_tool = RequestTools(request)
    #添加测试代码
    #保存记录
    client_test=""
    try:
        client_test = Client.objects(profile__phone='18812345678').first()
    except:
        pass
    try:
        log_content = "post:{0};\nget:{1};".format(json.dumps(request.POST), json.dumps(request.GET))
        log_path = request.META['PATH_INFO']
        log_type = 'create'
        ip = request_tool.get_ip()[:15]
        if client_test:
            Log(content=log_content[:2000], ip=ip, type=log_type, path=log_path[:200],user=client_test.user).save()
        else:
            Log(content=log_content[:2000], ip=ip, type=log_type, path=log_path[:200]).save()
    except  Exception as e:
            message1=str(e)
    #添加测试代码结束
    #保存操作用户
    phone =   request_tool.get_parameter("phone")
    if not phone:
        return Response(pss_tools.get_message_dict("400102", "请检查填写的手机号","0")) 
    try:
        client = Client.objects(profile__phone=phone).first()
        if  not client:
            return Response(pss_tools.get_message_dict("400103", "用户不存在","0")) 
    except:
        return Response(pss_tools.get_message_dict("400102", "用户不存在，请检查填写的手机号","0")) 
    #保存记录
    try:
        log_content = "post:{0};\nget:{1};".format(json.dumps(request.POST), json.dumps(request.GET))
        log_path = request.META['PATH_INFO']
        log_type = 'create'
        ip = request_tool.get_ip()[:15]
        Log(content=log_content[:2000], ip=ip, type=log_type, path=log_path[:200],user=client.user).save()
    except  Exception as e:
            message1=str(e)
    if request.method == "POST":
        try:
            order = Ordering()
            order.submit_style = 'platform'
            order = pss_tools.zhuantou_validation_order(order)
            if isinstance(order,dict):
                message = order
                return Response(message)
            else:
                 order.save()
                 #return Response(message)  
        except Exception as e:
            message1=str(e)
            return Response(pss_tools.get_message_dict("400200", "订单存储失败","0")) 
        #付款部分
        if order.client.balance >= order.price:
            try:
                    order.pay_money()
                    order.save()
            except Exception as e:
                message1=str(e)
        else:
            #余额不足发送微信
            try:
                content="账户余额不足，订单号："+str(order.paper_id)+'的订单未支付，为防止影响您保险权益，请您及时付款'
                touser = order.client.wx_id
                send_wx_message(touser,content)     
            except Exception as e:
                pass
            #余额不足发送短信
            try:
                site_settings = SiteSettings.get_settings()
                helper = m5c_sms_helper.SmsHelper(site_settings.meilian_username, site_settings.meilian_password, site_settings.meilian_api_key)
                dx_content ="订单号为："+str(order.paper_id)+ "，车牌号为："+str(order.plate_number)+"的订单已生成，请及时付款"
                helper.send_sms(phone_to='17745170813', content=dx_content)
            except Exception as e:
                 pass
        if order:
            #订单状态
            if order.state == "init":
                   result['order_state'] = "未支付"
                   result['remark'] = "订单未支付，为防止影响您保险权益，请您及时付款"
            elif order.state == "paid":
                   result['order_state'] = "已支付"
            elif order.state == "done":
                 result['order_state'] = "已完成"
            result['paper_id'] = str(order.paper_id)#订单号
            result['transport_id'] = str(order.transport_id)#运单号
            message['data'] = result
        return Response(message) 
    else:
        raise InvalidAccessError()
     
#查看保单接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def  zhuantou_insurance_detail(request):
         result = dict()
         document=dict()
         documentlist=[]
         imagelist =  []
         message = {'code':"0000","message":"ok","state":"1"}   
         pss_tools = DocumentPssTools(request)
         request_tool = RequestTools(request)
         #保存操作用户
         phone =   request_tool.get_parameter("phone")
         try:
            client = Client.objects(profile__phone=phone).first()
            if  not client:
                return Response(pss_tools.get_message_dict("400103", "用户不存在","0")) 
         except:
            return Response(pss_tools.get_message_dict("400102", "用户不存在，请检查填写的手机号","0")) 
        #保存记录
         try:
            log_content = "post:{0};\nget:{1};".format(json.dumps(request.POST), json.dumps(request.GET))
            log_path = request.META['PATH_INFO']
            log_type = 'search'
            ip = request_tool.get_ip()[:15]
            Log(content=log_content[:2000], ip=ip, type=log_type, path=log_path[:200],user=client.user).save()
         except  Exception as e:
                message1=str(e)
                
         if request.method == 'POST':
             paper_id = request.POST.get('paper_id', None)
         else:
             paper_id = request.GET.get('paper_id', None)

         if paper_id == None:
             return Response(pss_tools.get_message_dict("400095", "未找到paper_id参数","0"))  

         try:
             order = Ordering.objects(paper_id=paper_id,client=client,is_hidden=False).first()   
         except Exception as e:
                 print(e)
                 return Response(pss_tools.get_message_dict("400093", "查找失败请检查所传参数正确性","0"))  
         if not order:
            return Response(pss_tools.get_message_dict("400092", "未查找到对应订单","0")) 
         if order.product_type != 'car':
             return Response(pss_tools.get_message_dict("400091", "查找订单类型错误，只能查看运单保险","0")) 
         
         if order.state == "done":
            host = request.get_host()
            #result['url'] =  "http://"+host+"/wss/insure/document/detail/"+str(document.id)+"/"
            for  image in order.insurance_image_list:
                images=''
                if order.insurance_up_state in [ 'pdf','picture']:
                    images =  "http://"+host+"/static/"+image
                else :
                    images= image
                imagelist.append(str(images))
            result['imagelist'] =imagelist           
         else:               
            result['imagelist'] ="处理中，请等待" 
            
         if order.state == "init":
               result['order_state'] = "未支付"
         elif order.state == "paid":
               result['order_state'] = "已支付"
         elif order.state == "done":
             result['order_state'] = "已完成"
             result['insurance_id'] = str(order.insurance_id)#保单号

         result['paper_id'] = str(order.paper_id)#运之宝订单号
         result['price'] = order.price/100#订单金额
         message['data'] = result
         return Response(message)  
     
def  create_data_detail(request,result, order_list):
    number=1
    for order_set in order_list:
        order_detail ={}
        #创建订单部分信息
        order_detail['phone'] =order_set.client.profile.phone
        order_detail['insured'] =order_set.insured
        order_detail['startSiteName'] =order_set.car_startSiteName
        order_detail['targetSiteName'] =order_set.car_targetSiteName
        order_detail['insurance_price'] =order_set.insurance_price/100
        order_detail['transport_id'] =order_set.transport_id
        order_detail['commodityName'] =order_set.commodityName
        order_detail['commodityCases'] =order_set.commodityCases
        #订单状态
        if order_set.state == "init":
               order_detail['order_state'] = "未支付"
        elif order_set.state == "paid":
               order_detail['order_state'] = "已支付"
        elif order_set.state == "done":
               order_detail['order_state'] = "已完成"
        
        order_detail['paper_id'] = order_set.paper_id       #订单号
        order_detail['price'] = str(order_set.price/100)   #应付保费
        order_detail['pay_price'] = str(order_set.pay_price/100)    #实付保费
        order_detail['insurance_id'] = str(order_set.insurance_id)#保单号
        order_detail['create_time'] = order_set.create_time.strftime("%Y-%m-%d ")#创建时间
        #保单地址
        imagelist =  []
        if order_set.state == "done":
            host = request.get_host()
            for  image in order_set.insurance_image_list:
                images=''
                if order_set.insurance_up_state in [ 'pdf','picture']:
                    images =  "http://"+host+"/static/"+image
                else :
                    images= image
                imagelist.append(str(images))
            order_detail['imagelist'] =imagelist           
        else:               
            order_detail['imagelist'] ="处理中，请等待" 
        result[number] = order_detail
        number = number +1
    return     result
     
#查看保单列表
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def  zhuantou_insurance_list(request):
         result = dict()
         document=dict()
         documentlist=[]
         imagelist =  []
         message = {'code':"0000","message":"ok","state":"1"}   
         pss_tools = DocumentPssTools(request)
         request_tool = RequestTools(request)
         #保存操作用户
         phone =   request_tool.get_parameter("phone")
         try:
            client = Client.objects(profile__phone=phone).first()
            if  not client:
                return Response(pss_tools.get_message_dict("400103", "用户不存在","0")) 
         except:
            return Response(pss_tools.get_message_dict("400102", "用户不存在，请检查填写的手机号","0")) 
        #保存记录
         try:
            log_content = "post:{0};\nget:{1};".format(json.dumps(request.POST), json.dumps(request.GET))
            log_path = request.META['PATH_INFO']
            log_type = 'search'
            ip = request_tool.get_ip()[:15]
            Log(content=log_content[:2000], ip=ip, type=log_type, path=log_path[:200],user=client.user).save()
         except  Exception as e:
                message1=str(e)
         #保存记录结束      
         #获取分页信息 
         if request.method == 'POST':
             page_index = request.POST.get('page_index', '1')
         else:
             page_index = request.GET.get('page_index', '1')
        #分页信息结束
         try:
             order_list = Ordering.objects(client=client,is_hidden=False,product_type='car')  #筛选出运单列表
         except Exception as e:
                 print(e)
                 return Response(pss_tools.get_message_dict("400093", "查找失败请检查所传参数正确性","0"))  
         if not order_list:
            return Response(pss_tools.get_message_dict("400092", "未查找到对应订单","0")) 
         
         count = order_list.count()
         page = PageTools()
         page_index=int(page_index)
         paging = page.get_paging(5, page_index, count)
         order_set = order_list[paging['start_item']:paging['end_item']]
         if len(order_set)>0:
             result = create_data_detail(request,result,order_set)
         total_pages_count=paging['total_pages_count']
         if page_index>total_pages_count:
             text="您查询的页数大于订单总页数，订单总页数为"+str(total_pages_count)
             return Response(pss_tools.get_message_dict("400106", text,"0")) 
         result['page_index'] = str(page_index)#当前页
         result['total_pages_count'] = str(total_pages_count)#总页数
         message['data'] = result
         return Response(message)  
     
     
     
     
     
     
     
     
     
     
     