#大东物流接口
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
import datetime 
from pss.tools import DocumentPssTools
import time
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pss.views_zhongan import ZhongAnApi
from django.conf import settings
from wss.views_sendmessage import  send_wx_message
#鉴权接口

@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
@csrf_exempt  
def authorize(request):
    message = {}
    if request.method == 'POST':
        app_id = request.POST.get('app_id', None)
        app_secret  = request.POST.get('app_secret', None)
    else:
        app_id = request.GET.get('app_id', None)
        app_secret = request.GET.get('app_secret', None)
    pss_tools = DocumentPssTools(request)
    
    logistics = Logistics.objects(platform_key=app_id,platform_secret=app_secret).first()
    message = pss_tools.validation_params(logistics,message)
    if message['state'] == '0': return Response(message)  
    d1 = datetime.datetime.now() 
    accessToken = AccessTokenApi.objects(logistics=logistics).first()
    if not accessToken:
        accessToken = AccessTokenApi()
        accessToken.logistics = logistics
    accessToken.expires_in= d1 + datetime.timedelta(hours=2)#token过期时间为2小时
    accessToken.token= generate_access_token(app_id,app_secret)
    accessToken.refresh_token= generate_refresh_token(app_secret)
    accessToken.refresh_token_expires= d1 + datetime.timedelta(days=60) #refresh token 过期时间为60天
    try:
        accessToken.save()
    except:
         return Response(pss_tools.get_message_dict("40006","sql save error","0"))    
    message['data'] = get_response_data(accessToken.token,accessToken.refresh_token)
    return Response(message)  
        
def get_response_data(access_token,refresh_token):
    data = {}
    data.setdefault("expires_in",7200)
    data.setdefault("access_token",access_token)
    data.setdefault("refresh_token",refresh_token) 
    return data
    
def generate_access_token(app_id,app_secret):
    time_stamp = str(int(time.time()))
    return hashlib.sha1((app_id+app_secret+time_stamp).encode('utf-8')).hexdigest().lower()

def generate_refresh_token(app_secret):
    time_stamp = str(int(time.time()))
    return hashlib.sha1((app_secret+time_stamp).encode('utf-8')).hexdigest().lower()

#刷新token
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def refresh_token(request):
    message = {}
    if request.method == 'POST':
        app_id = request.POST.get('app_id', 'None')
        app_secret  = request.POST.get('app_secret', None)
        refresh_token  = request.POST.get('refresh_token', None)
    else:
        app_id = request.GET.get('app_id', None)
        app_secret = request.GET.get('app_secret', None)
        refresh_token = request.GET.get('refresh_token', None)
        
    pss_tools = DocumentPssTools(request)
    logistics = Logistics.objects(platform_key=app_id,platform_secret=app_secret).first()
    message = pss_tools.validation_refresh_token_params(logistics,message)
    if message['state'] == '0': return Response(message)  
    d1 = datetime.datetime.now() 
    accessToken = AccessTokenApi.objects(logistics=logistics,refresh_token=refresh_token).first()
    if accessToken:
        if accessToken.is_resfresh_token_expired():  #判断resfresh_token是否过期
             return Response(pss_tools.get_message_dict("40007","refresh token expire","0"))   
    else:
            return Response(pss_tools.get_message_dict("40008","Invalid refresh token","0"))   
    accessToken.token= generate_access_token(app_id,app_secret)
    accessToken.expires_in= d1 + datetime.timedelta(hours=2)#token过期时间为2小时
    try:
        accessToken.save()
    except:
         return Response(pss_tools.get_message_dict("40006","sql save error","0"))   
    message['data'] = get_response_data(accessToken.token,accessToken.refresh_token)
    return Response(message)  

#检验授权凭证接口
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def check_token(request):
    message = {}
    if request.method == 'POST':
        access_token = request.POST.get('access_token', None)
    else:
        access_token = request.GET.get('access_token', None)
    pss_tools = DocumentPssTools(request)
    accessToken = AccessTokenApi.objects(token=access_token).first()
    if not accessToken:
            return Response(pss_tools.get_message_dict("40009","Invalid access token","0"))   
    if accessToken.is_expired():
            return Response(pss_tools.get_message_dict("40010","Access token expire","0"))   
    return Response(pss_tools.get_message_dict("0000","ok","1"))   

#获取各种文件接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def get_documents(request):
        if request.method == 'POST':
            access_token = request.POST.get('access_token', None)
            phone = request.POST.get('phone', None)      
        else:
            access_token = request.GET.get('access_token', None)
            phone = request.GET.get('phone', None)
        message = {'code':"0000","message":"ok","state":"1"}
        result = dict()
        resultlist = []
        pss_tools = DocumentPssTools(request)
        client = Client.objects(profile__phone=phone).first()
        if client:
                insure_type = client.product_ticket.product_type
                print(insure_type)
                if insure_type ==  'ticket':
                     documentlist = client.product_ticket.documents
                     if  documentlist:                            
                             for  document in documentlist:
                                 result['name'] = document.name
                                 host = request.get_host()
                                 result['url'] =  "http://"+host+"/wss/insure/document/detail/"+str(document.id)+"/"
                                 #result['url'] = " http://172.16.50.161:8080/wss/insure/document/detail/"+str(document.id)+"/"                        
                                 resultlist.append(result)
                     else:
                         return Response(pss_tools.get_message_dict("40029", "此产品没有相关文档","0"))
                else:
                     return Response(pss_tools.get_message_dict("40030", "产品类型错误","0"))                    
        else:
             return Response(pss_tools.get_message_dict("40031", "用户不存在","0"))                
        message['data'] = resultlist
        return Response(message)      


#创建订单接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def create_order(request):
        if request.method == 'POST':
              access_token = request.POST.get('access_token', None)
        else:
              access_token = request.GET.get('access_token', None)
        result = dict()
        message = {'code':"0000","message":"ok","state":"1"}   
        order = Ordering()
        pss_tools = DocumentPssTools(request)
        order = pss_tools.validation_dadong_order(order)
        try:
             if isinstance(order,dict):
                message = order
                return Response(message)  
             else:
                order.save()
        except Exception as e:
                print(e)

        if order.client.balance >= order.price:
            order.pay_money()
            order.state = "paid"
            try:
                  order.save()
            except Exception as e:
                  result['pay_result'] = "网络异常"
                  result['pay_state'] = "未支付"
            result['pay_result'] = "支付成功"
            result['pay_state'] = "已支付"
        else:
            result['pay_result'] = "余额不足"
            result['pay_state'] = "未支付"
        result['order_id'] = str(order.paper_id)
        result['balance'] = order.client.balance/100
        message['data'] = result
        return Response(message)  
        
    
#查看订单详情接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def get_order_detail(request):
    if request.method == 'POST':
        access_token = request.POST.get('access_token', None)
        paper_id = request.POST.get('paper_id', None)    
    else:
        access_token = request.GET.get('access_token', None)
        paper_id = request.GET.get('paper_id', None)
    images = dict()
    message = {'code':"0000","message":"ok","state":"1"}
    imagelist =  []
    result = dict()
    pss_tools = DocumentPssTools(request)
    order = Ordering.objects(paper_id=paper_id).first()
    if order:
        result['paper_id'] = order.paper_id
        if order.product_type =="ticket":
               result['product_type'] = "单票保险"
        elif order.product_type =="car":
               result['product_type'] = "运单保险"
        elif order.product_type =="batch":
               result['product_type'] = "车次保险"
            
        if order.state == "init":
               result['state'] = "未支付"
        elif order.state == "paid":
               result['state'] = "已支付"
        elif order.state == "done":
               result['state'] = "已完成"
               
        if order.insurance_type == "transport":
                result['insurance_type'] = "货物运输保险"
        elif order.insurance_type == "freight":
                 result['insurance_type'] = "物流责任保险"
        
        if order.transport_type == "road":
               result['transport_type'] = "陆运"
        elif order.transport_type == "air":
               result['transport_type'] = "空运"
        elif order.transport_type == "ocean":
                result['transport_type'] = "海运"
        elif order.transport_type == "railway":
                result['transport_type'] = "铁运"
        elif order.transport_type == "union":
                result['transport_type'] = "联运"
        
#         if order.good_type == "ordinary_good":
#                result['good_type'] = "普通货物"
#         elif order.good_type == "fragile_articles":
#                 result['good_type'] = "易碎品"
#         elif order.good_type == "equipment":
#                  result['good_type'] = "机器设备（含精密仪器）"
#         elif order.good_type == "fresh":
#                  result['good_type'] = "水果、蔬菜"
#         elif order.good_type == "second_hand":
#                  result['good_type'] = "二手货"
#         elif order.good_type == "drug":
#                  result['good_type'] = "药品（疫苗除外）"
#         elif order.good_type == "frozen_product":
#                  result['good_type'] = "冷冻品"
        result['good_type'] = order.cargo.cargo_name
        if order.is_compensate == "false":
                  result['is_compensate'] = "未受理"
        elif order.is_compensate == "true":
                 result['is_compensate'] = "已受理"
      
        result['company'] = order.company.name
        result['insurance_product_name'] = order.insurance_product.name
        result['insured'] = order.insured
        result['startSiteName'] = order.startSiteName
        result['insurance_price'] = order.insurance_price/1000
        result['insurance_rate'] = order.insurance_rate
        result['transport_id'] = order.transport_id
        result['commodityName'] = order.commodityName
        result['commodityCases'] = order.commodityCases
        result['expectStartTime'] = order.expectStartTime
        result['price'] = order.price/1000
        result['pay_price'] = order.pay_price/1000
        #result['old_price'] = order.old_price/1000     
        
        if order.state == "done":
            result['insurance_id'] =order.insurance_id
            for  image in order.insurance_image_list:
                images['url'] = "http://crteam.top/static/"+image
                imagelist.append(images)
            result['imagelist'] =imagelist           
        else:               
            result['imagelist'] ="处理中，请等待"   
    else:
            return Response(pss_tools.get_message_dict("40028", "查看的订单不存在","0"))
    message['data'] = result
    return Response(message)  
  
  
  #增加预存
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def add_deposit(request):
    if request.method == 'POST':
        access_token = request.POST.get('access_token', None)
        phone = request.POST.get('phone', None)
        money = request.POST.get('money', None)        
    else:
        access_token = request.GET.get('access_token', None)
        phone = request.GET.get('phone', None)
        money = request.GET.get('money', None)
    message = {'code':"0000","message":"ok","state":"1"}                      
    result = dict()
    pss_tools = DocumentPssTools(request)
    client = Client.objects(profile__phone=phone).first()
    if client:
            if money:
                    try:
                        money = round(float(money) * 100)
                        if isinstance(client.balance, int):
                            client.balance += money
                        else:
                            client.balance = money
                        client.save()
                        import datetime
                        import time
                        nowtime = datetime.datetime.now()
                        subtime = nowtime.strftime("%Y-%m-%d %H:%M:%S")
                        phone =  client .profile.phone
                        username = client.name
                        depositstatistical = DepositStatistical()
                        depositstatistical.name = username
                        depositstatistical.phone = phone
                        depositstatistical.company_name = client.company_name
                        depositstatistical.balance = money
                        depositstatistical.create_time = subtime
                        depositstatistical.save()
                        result['balance'] = client.balance/100
                        result['message'] = "预存成功！"
                    except Exception:
                        return Response(pss_tools.get_message_dict("40028", "存款金额类型异常","0"))                 
            else:
                  return Response(pss_tools.get_message_dict("40028", "预存金额不能为空","0"))         
    else:
            return Response(pss_tools.get_message_dict("40028", "用户不存在","0"))       
    message['data'] = result
    return Response(message)  



 #扣款预存
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def minus_deposit(request):
    if request.method == 'POST':
        access_token = request.POST.get('access_token', None)
        phone = request.POST.get('phone', None)
        order_id = request.POST.get('order_id', None)        
    else:
        access_token = request.GET.get('access_token', None)
        phone = request.GET.get('phone', None)
        order_id = request.GET.get('order_id', None)
    message = {'code':"0000","message":"ok","state":"1"}
    result = dict()
    pss_tools = DocumentPssTools(request)
    client = Client.objects(profile__phone=phone).first()
    if client:
         order = Ordering.objects(id=order_id).first()
         if order:
             if client.balance >= order.price:
                 client.balance -= order.price
                 order.state = "paid"
                 order.save()
                 client.order = order
                 client.save()
                 result[' order_state'] = "已支付"
                 result['balance'] = client.balance/100
                 result['message'] = "扣款成功！"
             else:
                return Response(pss_tools.get_message_dict("40028", "余额不足，扣款失败","0"))         
         else:
              return Response(pss_tools.get_message_dict("40028", "订单不存在","0"))         
    else:
          return Response(pss_tools.get_message_dict("40028", "用户不存在","0"))         
    message['data'] = result
    return Response(message) 
 
  #余额查询
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def get_balance(request):
    if request.method == 'POST':
        access_token = request.POST.get('access_token', None)
        phone = request.POST.get('phone', None)      
    else:
        access_token = request.GET.get('access_token', None)
        phone = request.GET.get('phone', None)
    result = dict()
    message = {'code':"0000","message":"ok","state":"1"}
    pss_tools = DocumentPssTools(request)
    client = Client.objects(profile__phone=phone).first()
    if client:
          result['balance'] = client.balance/100
    else:
          return Response(pss_tools.get_message_dict("40028", "用户不存在","0"))  
    message['data'] = result
    return Response(message)            

###############一嗨物流新版对接接口--start##################
#获取货物类型
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def get_cargo(request):
    if request.method == 'POST':
        access_token = request.POST.get('access_token', None)
        cargo = request.POST.get('cargo', None).strip()      
    else:
        access_token = request.GET.get('access_token', None)
        cargo = request.GET.get('cargo', None).strip()
    resultlist = []
    message = {'code':"0000","message":"ok","state":"1"}
    pss_tools = DocumentPssTools(request)
    if cargo:
             try:
                 cargo_type_set = CargoType.objects(ct_name=cargo,ct_state=True).first()
             except:
                 return Response(pss_tools.get_message_dict("40011", "可保货物大类不存在","0"))  
             if cargo_type_set:
                try:
                     cargo_set = Cargo.objects(cargo_type=cargo_type_set,state=True)
                except Exception as e:
                     a=str(e)
                     print(a)
             if cargo_set:
                         for cargoobj in cargo_set:
                             result = dict()
                             result['cargo_name'] = cargoobj.cargo_name
                             result['cargo_number'] = cargoobj.cargo_number
                             resultlist.append(result)
             else:
                 return Response(pss_tools.get_message_dict("40011", "此货物不在承保类型范围内","0"))  
    else:
#           cargo_set = CargoType.objects(ct_state=True)
#           for cargoobj in cargo_set:
#                  resultlist.append(cargoobj.ct_name)   
#           resultlist = set(resultlist)  
          cargo_set = Cargo.objects(state=True)
          for cargoobj in cargo_set:
                 result = dict()
                 result['cargo_name'] = cargoobj.cargo_name
                 result['cargo_number'] = cargoobj.cargo_number
                 resultlist.append(result)
    message['data'] = resultlist
    return Response(message)            


#获包装方式
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def get_pack(request):
    if request.method == 'POST':
        access_token = request.POST.get('access_token', None)
        pack = request.POST.get('pack', None).strip()      
    else:
        access_token = request.GET.get('access_token', None)
        pack = request.GET.get('pack', None).strip()      
    resultlist = []
    message = {'code':"0000","message":"ok","state":"1"}
    order = Ordering()
    pack_method_list=order.PACK_METHOD
    pss_tools = DocumentPssTools(request)
    if pack:
                for packobj in pack_method_list:
                       if packobj[0][0] == pack:             
                                 for packdetailobj in packobj[1]:
                                     result = dict()
                                     result['pack_code'] = packdetailobj[0]
                                     result['pack_name'] = packdetailobj[1]
                                     resultlist.append(result)
    else:
          for packobj in pack_method_list:
                 resultlist.append(packobj[0][0])   
          resultlist = set(resultlist)     
    message['data'] = resultlist
    return Response(message)    
        
#获取地址列表
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def get_area_list(request):
    if request.method == 'POST':
        access_token = request.POST.get('access_token', None)  
    else:
        access_token = request.GET.get('access_token', None)     
    
    resultlist = []
    message = {'code':"0000","message":"ok","state":"1"}
    pss_tools = DocumentPssTools(request)
    city_detail_list = CargoArea.objects()
    if  city_detail_list:
        for  cityobj in city_detail_list:
             result = dict()
             result['name'] = cityobj.name
             result['code'] = cityobj.code
             result['level'] = cityobj.level
             result['parentcode'] = cityobj.parentcode
             resultlist.append(result)
    else:
             return Response(pss_tools.get_message_dict("40012", "地址列表为空，无法获取","0"))  
    message['city_detail_list'] = resultlist
    return Response(message)            


 
 #立即投保接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def  immediate_insurance(request):
         if request.method == 'POST':
              access_token = request.POST.get('access_token', None)
         else:
              access_token = request.GET.get('access_token', None)
         result = dict()
         documentlist=[]
         document = dict()
         message = {'code':"0000","message":"ok","state":"1"}   
         order = Ordering()
         pss_tools = DocumentPssTools(request)
         order = pss_tools.yihai_validation_order(order)
         try:
             if isinstance(order,dict):
                message = order
                return Response(message)  
             else:
                order.save()
         except Exception as e:
                 print(e)
                 return Response(pss_tools.get_message_dict("40031", str(e),"0"))  
                
                
         if order.product_type =="ticket":
               result['product_type'] = "单票保险"
         elif order.product_type =="car":
               result['product_type'] = "运单保险"
         elif order.product_type =="batch":
               result['product_type'] = "车次保险"
            
         if order.state == "init":
               result['state'] = "未支付"
         elif order.state == "paid":
               result['state'] = "已支付"
         elif order.state == "done":
               result['state'] = "已完成"
               
         if order.insurance_type == "transport":
                result['insurance_type'] = "货物运输保险"
         elif order.insurance_type == "freight":
                 result['insurance_type'] = "物流责任保险"
        
         if order.is_compensate == "false":
                  result['is_compensate'] = "未受理"
         elif order.is_compensate == "true":
                 result['is_compensate'] = "已受理"
         if order.insurance_product.documents:
                for  documentobj in order.insurance_product.documents:
                                 document['name'] = documentobj.name
                                 document['url'] = "http://crteam.top/wss/insure/document/detail/"+str(documentobj.id)+"/"                  
                                 documentlist.append(document)
                result['documentlist'] = documentlist
         else:
            result['documentlist'] = "此产品没有相关的文档"
         result['company'] = order.company.name
         result['paper_id'] = str(order.paper_id)
         result['insurance_product_name'] = order.insurance_product.name
         result['insurance_rate'] = order.insurance_rate
         result['insured'] = order.insured
         result['insurance_price'] = order.insurance_price/100
         result['price'] = order.price/100
         result['expectStartTime'] = order.expectStartTime
         result['transport_id'] = order.transport_id
         result['plate_number'] = order.plate_number
         result['commodityName'] = order.commodityName
         result['commodityCases'] = order.commodityCases
         result['good_type'] = order.cargo.cargo_name
         result['pack_method'] = pss_tools.pack_method(order.pack_method)
         result['startSiteName'] =  pss_tools.address_name(order.startSiteName)
         result['targetSiteName'] = pss_tools.address_name(order.targetSiteName)
         result['transport_type'] = pss_tools.transport_type(order.transport_type)
         result['balance'] = order.client.balance/100
         message['data'] = result
         return Response(message)  
    
    
#确认投保接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def  confirm_insurance(request):
         if request.method == 'POST':
                access_token = request.POST.get('access_token', None)
                paper_id = request.POST.get('paper_id', None).strip()      
         else:
                access_token = request.GET.get('access_token', None)
                paper_id = request.GET.get('paper_id', None).strip()
         result = dict()
         images = dict()
         document =  dict()
         imagelist =  []
         documentlist =[]
         message = {'code':"0000","message":"ok","state":"1"}
         pss_tools = DocumentPssTools(request)
         order = Ordering.objects(paper_id=paper_id).first()
         if order:
                    if order.company.paper_id == settings.ZHONGAN_COMPANY_CODE:
                            if order.product_type == "ticket":
                                     if order.client.balance >=order.price:
                                         zhonganapi = ZhongAnApi(request)
                                         try:
                                                   response = zhonganapi.applyValidate(order.id)
                                         except Exception as e:
                                                    return Response(pss_tools.get_message_dict("40037", "网络异常，请联系运之宝客服","0"))  
                                        
                                         responseinfo = json.loads(response['bizContent'])
                                         if responseinfo['isSuccess'] == "Y":
                                             order.insurance_id = responseinfo['orderNo']
                                             temp =[]
                                             temp.append(responseinfo['epolicyDownloadlink'])
                                             order.insurance_image_list = temp
                                             order.pay_money()
                                             order.state = "done"
                                             try:
                                                 order.save()
                                             except Exception as e:
                                                       return Response(pss_tools.get_message_dict("40031", "数据库存储异常！","0"))  
                                         else:      
                                          return Response(pss_tools.get_message_dict("40032", responseinfo['failMsg'],"0"))  
                                     else:
                                        return Response(pss_tools.get_message_dict("40033", "用户的账户余额不足","0"))  
                            else:
                                  return Response(pss_tools.get_message_dict("40034", "保险公司只承保单票保险","0"))  
                    else:             
                            if order.client.balance >= order.price:
                                order.pay_money()
                                try:
                                    order.save()
                                except Exception as e:
                                         return Response(pss_tools.get_message_dict("40031", "数据库存储异常","0"))  
                                if int(order.client.balance/100)  >= 500:
                                        content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。"
                                else:
                                         content = "恭喜！您的订单"+str(order.paper_id)+"已经付款成功。如果您提交的订单信息在保险公司承保条件范围内，那么您的订单已经生效，否则保险公司不承担赔偿责任，我们将在3个工作日内将保单上传到平台以供查询，请耐心等待。预存余额不足500，为了避免余额不足导致无法提交订单，请尽快补充预存！"   
                                touser = order.client.wx_id
                                send_wx_message(touser,content)
                            else:
                                return Response(pss_tools.get_message_dict("40035", '余额不足，预存余额为{0}元，您至少还须预存{1}元，预存成功后请到“我的”--“我的订单”中选择该订单进行支付'.format(order.client.balance/100, (order.price-order.client.balance)/100),"0"))          
         else:
                    return Response(pss_tools.get_message_dict("40036", "要确认提单的订单不存在","0"))
         
         if order.product_type =="ticket":
               result['product_type'] = "单票保险"
         elif order.product_type =="car":
               result['product_type'] = "运单保险"
         elif order.product_type =="batch":
               result['product_type'] = "车次保险"
            
         if order.state == "init":
               result['state'] = "未支付"
         elif order.state == "paid":
               result['state'] = "已支付"
         elif order.state == "done":
               result['state'] = "已完成"
               
         if order.insurance_type == "transport":
                result['insurance_type'] = "货物运输保险"
         elif order.insurance_type == "freight":
                 result['insurance_type'] = "物流责任保险"
        
         if order.is_compensate == "false":
                  result['is_compensate'] = "未受理"
         elif order.is_compensate == "true":
                 result['is_compensate'] = "已受理"
       
        
         if order.state == "done":
             if  order.company.paper_id == settings.ZHONGAN_COMPANY_CODE:
                    result['insurance_id'] =order.insurance_id
                    for  image in order.insurance_image_list:
                        #images['url'] = "http://crteam.top/static/"+image
                        images['url'] = image
                        imagelist.append(images)
                    result['imagelist'] =imagelist  
                    result['insurance_id'] = str(order.insurance_id) 
             else:
                    result['insurance_id'] =order.insurance_id
                    for  image in order.insurance_image_list:
                                   images['url'] = "http://crteam.top/static/"+image
                                   imagelist.append(images)
                    result['imagelist'] =imagelist             
         else:
              result['imagelist'] ="保单处理中，请等待"      
              result['insurance_id'] =""
         if order.insurance_product.documents:
                for  documentobj in order.insurance_product.documents:
                                 document['name'] = documentobj.name
                                 document['url'] = "http://crteam.top/wss/insure/document/detail/"+str(documentobj.id)+"/"                  
                                 documentlist.append(document)
                result['documentlist'] = documentlist
         else:
            result['documentlist'] = "此产品没有相关的文档"
         result['company'] = order.company.name
         result['paper_id'] = str(order.paper_id)
         result['balance'] = order.client.balance/100
        
         #result['insurance_image_list'] = order.insurance_image_list
         result['insurance_product_name'] = order.insurance_product.name
         result['insurance_rate'] = order.insurance_rate
         result['insured'] = order.insured
         result['insurance_price'] = order.insurance_price/100
         result['price'] = order.price/100
         result['pay_time'] = order.pay_time
         result['transport_id'] = order.transport_id
         result['plate_number'] = order.plate_number
         result['commodityName'] = order.commodityName
         result['commodityCases'] = order.commodityCases
         result['good_type'] = order.cargo.cargo_name
         result['pack_method'] = pss_tools.pack_method(order.pack_method)
         result['startSiteName'] =  pss_tools.address_name(order.startSiteName)
         result['targetSiteName'] = pss_tools.address_name(order.targetSiteName)
         result['transport_type'] = pss_tools.transport_type(order.transport_type)
         
         
         message['data'] = result
         return Response(message)  
     
     
#获取订单详情
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def  get_insure_order_detail(request):
         if request.method == 'POST':
                access_token = request.POST.get('access_token', None)
                paper_id = request.POST.get('paper_id', None).strip()      
         else:
                access_token = request.GET.get('access_token', None)
                paper_id = request.GET.get('paper_id', None).strip()
         result = dict()
         images = dict()
         document =  dict()
         imagelist =  []
         documentlist =[]
         message = {'code':"0000","message":"ok","state":"1"}
         pss_tools = DocumentPssTools(request)
         order = Ordering.objects(paper_id=paper_id).first()
         if order:
                 if order.product_type =="ticket":
                       result['product_type'] = "单票保险"
                 elif order.product_type =="car":
                       result['product_type'] = "运单保险"
                 elif order.product_type =="batch":
                       result['product_type'] = "车次保险"
                    
                 if order.state == "init":
                       result['state'] = "未支付"
                 elif order.state == "paid":
                       result['state'] = "已支付"
                 elif order.state == "done":
                       result['state'] = "已完成"
                       
                 if order.insurance_type == "transport":
                        result['insurance_type'] = "货物运输保险"
                 elif order.insurance_type == "freight":
                         result['insurance_type'] = "物流责任保险"
                
                 if order.is_compensate == "false":
                          result['is_compensate'] = "未受理"
                 elif order.is_compensate == "true":
                         result['is_compensate'] = "已受理"
               
                
                 if order.state == "done":
                     if  order.company.paper_id == settings.ZHONGAN_COMPANY_CODE:
                                result['insurance_id'] =order.insurance_id
                                for  image in order.insurance_image_list:
                                    #images['url'] = "http://crteam.top/static/"+image
                                       images['url'] = image
                                       imagelist.append(images)
                                result['imagelist'] =imagelist  
                                result['insurance_id'] = str(order.insurance_id) 
                     else:
                                result['insurance_id'] =order.insurance_id
                                for  image in order.insurance_image_list:
                                        images['url'] = "http://crteam.top/static/"+image
                                        imagelist.append(images)
                                result['imagelist'] =imagelist             
                 else:
                      result['imagelist'] ="保单处理中，请等待"      
                      result['insurance_id'] =""
                 if order.insurance_product.documents:
                        for  documentobj in order.insurance_product.documents:
                                         document['name'] = documentobj.name
                                         document['url'] = "http://crteam.top/wss/insure/document/detail/"+str(documentobj.id)+"/"                  
                                         documentlist.append(document)
                        result['documentlist'] = documentlist
                 else:
                    result['documentlist'] = "此产品没有相关的文档"
                 result['company'] = order.company.name
                 result['paper_id'] = str(order.paper_id)
                 result['balance'] = order.client.balance/100
               
                 #result['insurance_image_list'] = order.insurance_image_list
                 result['insurance_product_name'] = order.insurance_product.name
                 result['insurance_rate'] = order.insurance_rate
                 result['insured'] = order.insured
                 result['insurance_price'] = order.insurance_price/100
                 result['price'] = order.price/100
                 result['pay_time'] = order.pay_time
                 result['transport_id'] = order.transport_id
                 result['plate_number'] = order.plate_number
                 result['commodityName'] = order.commodityName
                 result['commodityCases'] = order.commodityCases
                 result['good_type'] = order.cargo.cargo_name
                 result['pack_method'] = pss_tools.pack_method(order.pack_method)
                 result['startSiteName'] =  pss_tools.address_name(order.startSiteName)
                 result['targetSiteName'] = pss_tools.address_name(order.targetSiteName)
                 result['transport_type'] = pss_tools.transport_type(order.transport_type)
         else:
                return Response(pss_tools.get_message_dict("40036", "查看订单不存在","0"))
         
         
         message['data'] = result
         return Response(message)       
     
     
#  #测试接口
# @csrf_exempt  
# @api_view(http_method_names=['POST','GET'])  
# @permission_classes((permissions.AllowAny,))  
# def  confirm_ceshi(request):
#          if request.method == 'POST':
#                 access_token = request.POST.get('access_token', None)
#                # order_id = request.POST.get('order_id', None).strip()      
#          else:
#                 access_token = request.GET.get('access_token', None)
#                 #order_id = request.GET.get('order_id', None).strip()
#          result = dict()
#          images = dict()
#          document =  dict()
#          imagelist =  []
#          documentlist =[]
#          message = {'code':"0000","message":"ok","state":"1"}
#          pss_tools = DocumentPssTools(request)
# #          import locale
# #          locale.setlocale('LC_COLLATE', 'zh_CN.UTF8')
#          a = ['中国人', '美国人', '韩国人', '台湾人']
#          for b in a:
#              print(b)
#                #imagelist = multi_get_letter(b)
# #          b = sorted(a, cmp = locale.strcoll)
#          #client = Client.objects(profile__phone=phone).first()
#         # order = Ordering.objects(id=order_id).first()
#         # print("order.pack_method-----"+order.pack_method)
#          #result['pack_method'] = pss_tools.pack_method(order.pack_method)
#          
#                 #  print("random_num-----"+random_num)
# #          result['startSiteName'] =  pss_tools.address_name(order.startSiteName)
# #          result['targetSiteName'] = pss_tools.address_name(order.targetSiteName)
# #          result['transport_type'] = pss_tools.transport_type(order.transport_type)
#          
#          #随机车牌号
# #          randomlist = []
# #          for i in range(5):
# #               random_num = random.randint(0, 9) 
# #               randomlist.append(str(random_num))
# #          random_5 = ''.join(randomlist)
# #          chepaihao ="黑A"+random_5
#          
#          
#          #投保人和被保人
#          
# #          order = Ordering.objects(id=order_id).first()
# #          if order.insured:
# #                  if order.insured == order.client.company_name:
# #                          insureName = order.insured
# #                          insureLinkName = order.insured
# #                  else:
# #                          if order.client.user_type == "transport":
# #                                   insureName = order.client.company_name+"/"+order.insured                     
# #                                   insureLinkName = order.client.company_name+"/"+order.insured
# #                          elif  order.client.user_type == "boss":
# #                              if order.client.user_classify == "units":
# #                                              insureName = order.client.company_name+"/"+order.insured         
# #                                              insureLinkName = order.client.company_name+"/"+order.insured
# #                              else:
# #                                     insureName = order.insured
# #                                     insureLinkName = order.insured
# #                          else:
# #                                     insureName = order.insured
# #                                     insureLinkName = order.insured
# #          else:
# #              if  order.client.user_type == "transport":
# #                       insureName = order.client.company_name
# #                       insureLinkName = order.client.company_name
# #                       
# #              elif order.client.user_type == "driver":
# #                       insureName = order.client.name
# #                       insureLinkName = order.client.name
# #              elif  order.client.user_type == "boss":
# #                         if order.client.user_classify == "units":
# #                              insureName = order.client.company_name
# #                              insureLinkName = order.client.company_name
# #                         elif order.client.user_classify == "individuals":
# #                              insureName = order.client.name
# #                              insureLinkName = order.client.name
# #              
# #              
# #              
# # #          if order.insured:
# # #                if  order.client.user_type == "transport":
# # #                      insureName = order.client.company_name+"/"+order.insured
# # #                      insureLinkName = order.client.company_name+"/"+order.insured
# # #                      
# # #                elif order.client.user_type == "driver":
# # #                      insureName = order.client.name
# # #                      insureLinkName = order.client.name
# # #                elif  order.client.user_type == "boss":
# # #                        if order.client.user_classify == "units":
# # #                             insureName = order.client.company_name+"/"+order.insured
# # #                             insureLinkName = order.client.company_name+"/"+order.insured
# # #                        elif order.client.user_classify == "individuals":
# # #                             insureName = order.client.name
# # #                             insureLinkName = order.client.name
# # #          else:
# # #                if  order.client.user_type == "transport":
# # #                      insureName = order.client.company_name
# # #                      insureLinkName = order.client.company_name
# # #                      
# # #                elif order.client.user_type == "driver":
# # #                      insureName = order.client.name
# # #                      insureLinkName = order.client.name
# # #                elif  order.client.user_type == "boss":
# # #                        if order.client.user_classify == "units":
# # #                             insureName = order.client.company_name
# # #                             insureLinkName = order.client.company_name
# # #                        elif order.client.user_classify == "individuals":
# # #                             insureName = order.client.name
# # #                             insureLinkName = order.client.name
# #          result["insureName"]      = insureName
# #          result["insureLinkName"]    =   insureLinkName
#   
#          
# #          if order.insure:
# #                  insureName = order.insure
# #                  insureLinkName = order.insure
# #                  if  order.client.user_type == "transport":
# #                         holderName =  order.client.company_name+"/"+order.client.name
# #                         holderLinkName =  order.client.company_name+"/"+order.client.name
# #                         holderType = "201"
# #                         holderCertType = "YY"
# #                         holderCertNo = order.client.business_license_id
# #                         
# #                         insureType = "201"
# #                         insureCertType = "YY"
# #                         insureCertNo  =  order.client.business_license_id  
# #                  elif order.client.user_type == "driver":
# #                         holderName =  order.client.name
# #                         holderLinkName =  order.client.name
# #                         holderType = "100"
# #                         holderCertType = "I"
# #                         holderCertNo = order.client.national_id
# #                         
# #                         insureType = "100"
# #                         insureCertType = "I"
# #                         insureCertNo  =  order.client.national_id
# #                  elif  order.client.user_type == "boss":
# #                        if order.client.user_classify == "units":
# #                                 holderName =  order.client.company_name+"/"+order.client.name
# #                                 holderLinkName =  order.client.company_name+"/"+order.client.name
# #                                 holderType = "201"
# #                                 holderCertType = "YY"
# #                                 holderCertNo = order.client.business_license_id
# #                                 
# #                                 insureType = "201"
# #                                 insureCertType = "YY"
# #                                 insureCertNo  =  order.client.business_license_id  
# #                                 
# #                        elif order.client.user_classify == "individuals":
# #                                 holderName =  order.client.name
# #                                 holderLinkName =  order.client.name
# #                                 holderType = "100"
# #                                 holderCertType = "I"
# #                                 holderCertNo = order.client.national_id
# #                                 
# #                                 insureType = "100"
# #                                 insureCertType = "I"
# #                                 insureCertNo  =  order.client.national_id
# #          else:
#              
#              
#            
# 
#          
#        
#          message['data'] =imagelist
#          return Response(message)  
#      
#      
# def multi_get_letter(str_input):
#   if isinstance(str_input, unicode):
#     unicode_str = str_input
#   else:
#     try:
#       unicode_str = str_input.decode('utf8')
#     except:
#       try:
#         unicode_str = str_input.decode('gbk')
#       except:
#         print 'unknown coding'
#         return
#   return_list = []
#   for one_unicode in unicode_str:
#     return_list.append(single_get_first(one_unicode))
#   return return_list
# def single_get_first(unicode1):
#   str1 = unicode1.encode('gbk')
#   try:
#     ord(str1)
#     return str1
#   except:
#     asc = ord(str1[0]) * 256 + ord(str1[1]) - 65536
#     if asc >= -20319 and asc <= -20284:
#       return 'a'
#     if asc >= -20283 and asc <= -19776:
#       return 'b'
#     if asc >= -19775 and asc <= -19219:
#       return 'c'
#     if asc >= -19218 and asc <= -18711:
#       return 'd'
#     if asc >= -18710 and asc <= -18527:
#       return 'e'
#     if asc >= -18526 and asc <= -18240:
#       return 'f'
#     if asc >= -18239 and asc <= -17923:
#       return 'g'
#     if asc >= -17922 and asc <= -17418:
#       return 'h'
#     if asc >= -17417 and asc <= -16475:
#       return 'j'
#     if asc >= -16474 and asc <= -16213:
#       return 'k'
#     if asc >= -16212 and asc <= -15641:
#       return 'l'
#     if asc >= -15640 and asc <= -15166:
#       return 'm'
#     if asc >= -15165 and asc <= -14923:
#       return 'n'
#     if asc >= -14922 and asc <= -14915:
#       return 'o'
#     if asc >= -14914 and asc <= -14631:
#       return 'p'
#     if asc >= -14630 and asc <= -14150:
#       return 'q'
#     if asc >= -14149 and asc <= -14091:
#       return 'r'
#     if asc >= -14090 and asc <= -13119:
#       return 's'
#     if asc >= -13118 and asc <= -12839:
#       return 't'
#     if asc >= -12838 and asc <= -12557:
#       return 'w'
#     if asc >= -12556 and asc <= -11848:
#       return 'x'
#     if asc >= -11847 and asc <= -11056:
#       return 'y'
#     if asc >= -11055 and asc <= -10247:
#       return 'z'
#     else:
#       return ''
#     return ''