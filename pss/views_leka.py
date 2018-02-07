#乐卡物流接口
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






#立即投保接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def  leka_immediate_insurance(request):
         if request.method == 'POST':
              access_token = request.POST.get('access_token', None)
         else:
              access_token = request.GET.get('access_token', None)
         result = dict()
         document=dict()
         documentlist=[]
         message = {'code':"0000","message":"ok","state":"1"}   
         order = Ordering()
         pss_tools = DocumentPssTools(request)
         order = pss_tools.leka_validation_order(order)
         try:
             order.save()
             if isinstance(order,dict):
                message = order
                return Response(message)  
             else:
                   if order.client.balance >=order.price:
                       order.pay_money()
                       #order.state = "done"
                       order.save()
         except Exception as e:
                 print(e)
                 return Response(pss_tools.get_message_dict("40026", "数据库存储异常","0"))  
                 
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
#          if order.insurance_product.documents:
#                 for  documentobj in order.insurance_product.documents:
#                                  document['name'] = documentobj.name
#                                  document['url'] = "http://crteam.top/wss/insure/document/detail/"+str(documentobj.id)+"/"                  
#                                  documentlist.append(document)
#                 result['documentlist'] = documentlist
#          else:
#             result['documentlist'] = "此产品没有相关的文档"
         result['company'] = order.company.name
         result['paper_id'] = str(order.paper_id)
         result['insurance_product_name'] = order.insurance_product.name
         result['insurance_rate'] = order.insurance_rate
         result['insured'] = order.insured
         result['insurance_price'] = order.insurance_price/100
         print(order.insurance_price)
         result['price'] = order.price/100
         result['expectStartTime'] = order.expectStartTime
         result['transport_id'] = order.transport_id
         result['plate_number'] = order.plate_number
         result['commodityName'] = order.commodityName
         result['commodityCases'] = order.commodityCases
         result['startSiteName'] =  pss_tools.address_name(order.startSiteName)
         result['targetSiteName'] = pss_tools.address_name(order.targetSiteName)
         result['balance'] = order.client.balance/100
         message['data'] = result
         return Response(message)  
     
     
     
     #获取订单详情接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def leka_get_order_detail(request):
    if request.method == 'POST':
        access_token = request.POST.get('access_token', None)
        paper_id = request.POST.get('paper_id', None).strip()           
    else:
        access_token = request.GET.get('access_token', None)
        paper_id = request.GET.get('paper_id', None).strip()       
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
        

        if order.is_compensate == "false":
                  result['is_compensate'] = "未受理"
        elif order.is_compensate == "true":
                 result['is_compensate'] = "已受理"
      
        result['company'] = order.company.name
        result['insurance_product_name'] = order.insurance_product.name
        result['insured'] = order.insured
        result['startSiteName'] = leka_address_name(order.startSiteName)
        result['targetSiteName'] = leka_address_name(order.targetSiteName)
        result['insurance_price'] = order.insurance_price/1000
        result['insurance_rate'] = order.insurance_rate
        result['transport_id'] = order.transport_id
        result['commodityName'] = order.commodityName
        result['commodityCases'] = order.commodityCases
        result['expectStartTime'] = order.expectStartTime
        result['price'] = order.price/1000
        result['pay_price'] = order.pay_price/1000   
        
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

#获取保险产品文档接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def leka_get_documents(request):
        if request.method == 'POST':
            access_token = request.POST.get('access_token', None)    
        else:
            access_token = request.GET.get('access_token', None)
        message = {'code':"0000","message":"ok","state":"1"}
        result = dict()
        document=dict()
        resultlist = []
        productresultlist=[]
        documentlist=[]
        pss_tools = DocumentPssTools(request)
        productslist =  InsuranceProducts.objects(product_type="ticket")
        if productslist:
                for productobj in productslist:
                        if productobj.company.paper_id == settings.ZHONGAN_COMPANY_CODE:
                                         continue
                        else:
                                         productresultlist.append(productobj)
        else:
                return Response(pss_tools.get_message_dict("40025", "没有可保的产品","0"))
            
        
        if  productresultlist:
               for productdocobj in productresultlist:
                           for  documentobj in productdocobj.documents:
                                  document['name'] = documentobj.name
                                  document['url'] = "http://crteam.top/wss/insure/document/detail/"+str(documentobj.id)+"/"                  
                                  documentlist.append(document)
               if documentlist:
                       result['documentlist'] = documentlist
               else:
                      return Response(pss_tools.get_message_dict("40029", "保险产品没有相应的文档","0"))
        else:
                return Response(pss_tools.get_message_dict("40025", "没有可保的产品","0"))
               
       
        message['data'] = result
        return Response(message)      


#获取用户订单列表接口
@csrf_exempt  
@api_view(http_method_names=['POST','GET'])  
@permission_classes((permissions.AllowAny,))  
def leka_get_order_list(request):
        if request.method == 'POST':
            access_token = request.POST.get('access_token', None) 
            phone = request.POST.get('phone', None).strip()    
            start_time = request.POST.get('start_time', None)
            end_time= request.POST.get('end_time', None)
            insured= request.POST.get('insured', None)   
            insurance_str= request.POST.get('insurance_str', None)  
            #insurance_list= request.POST.getlist('insurance_list', None)    
        else:
            access_token = request.GET.get('access_token', None)
            phone = request.GET.get('phone', None).strip()    
            start_time= request.GET.get('start_time', None)   
            end_time = request.GET.get('end_time', None) 
            insured = request.GET.get('insured', None) 
            insurance_str = request.GET.get('insurance_str', None)       
        message = {'code':"0000","message":"ok","state":"1"}
        result = dict()
        orderlist = []  
        imagelist=[] 
        insurance_list = insurance_str.split(" ,")
        pss_tools = DocumentPssTools(request)
        if not phone:
            return Response(pss_tools.get_message_dict("40013", "未找到phone参数","0"))
        client = Client.objects(profile__phone=phone).first()
        if client:
                  order_set = Ordering.objects(client=client)
                  order_set = leka_order_filter(order_set=order_set, start_time=start_time, end_time=end_time,insurance_list=insurance_list,insured=insured)
                  if  order_set:
                          for  orderobj in order_set:
                                   order=dict()
                                   order['paper_id'] = orderobj.paper_id
                                   order['insurance_product_name'] = orderobj.insurance_product.name 
                                   order['insured'] = orderobj.insured
                                   order['transport_id'] = orderobj.transport_id
                                   order['expectStartTime'] = orderobj.expectStartTime
                                   order['company'] = orderobj.company.name
                                   if orderobj.state == "init":
                                           order['state'] = "未支付"
                                   elif orderobj.state == "paid":
                                           order['state'] = "已支付"
                                   elif orderobj.state == "done":
                                           order['state'] = "已完成"
                                           order['insurance_id'] =orderobj.insurance_id
                                           for  image in orderobj.insurance_image_list:
                                                 images = dict()
                                                 images['url'] = "http://crteam.top/static/"+image
                                                 imagelist.append(images)
                                           order['imagelist'] =imagelist           
                                   orderlist.append(order)
                          result['orderlist']=orderlist
                  else:
                       return Response(pss_tools.get_message_dict("40030", "此用户没有订单","0"))
                       #return self.get_message_dict("40030","此用户没有订单","0")  
        else:
                  return Response(pss_tools.get_message_dict("40031", "用户不存在","0"))
        message['data'] = result
        return Response(message)     

def leka_address_name(value):
    address_number = value
    try:
        print(address_number)
        name_detail = address_number.split(" ")
        count = len(name_detail)
        address_detail=""
        for i in range(count):
            prov_code = name_detail[i]
            if prov_code:
                prov_name = CargoArea.objects(code=prov_code).first().name
                address_detail = address_detail + prov_name+" "
            else:
                continue
        return address_detail.strip()
    except:
        message = address_number+"未找到订单对应编码的地址名称"
        return message
    
def leka_order_filter(order_set,start_time, end_time,insurance_list,insured):
        if not isinstance(order_set, QuerySet):
            raise ParameterError('非法的参数：order_set')
        if insured:
            order_set = order_set.filter(Q(insured__contains=insured))
        if insurance_list:
            order_set = order_set.filter(insurance_id__in=insurance_list)  
            #order_set = order_set.filter(Q(insurance_id__contains=keyword) | Q(paper_id__contains=keyword) | Q(insured__contains=keyword)| Q(transport_id__contains=keyword)|Q(insurance_product__in=product_set))#| Q(insurance_product__name__contains=keyword))
        if start_time and end_time:     
                   end_time2 = datetime.strptime(end_time,"%Y-%m-%d")
                   end_time1 = (end_time2+timedelta(days= 1)).strftime('%Y-%m-%d') 
                   order_set = order_set.filter(expectStartTime__gt=start_time, expectStartTime__lt=end_time1)
               
        return order_set