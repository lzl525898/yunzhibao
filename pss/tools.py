from setuptools.command.build_ext import if_dl
__author__ = 'mlzx'

from common.tools_legoo import DocumentTools, DocumentFolderType, ImageTools, ImageFolderType
from common.tools import RequestTools
from common.tools import ConvertTools
from common.models import *
from django.contrib.auth import authenticate
from datetime import timedelta
from datetime import datetime
from common.interface_helper import *
from uuid import uuid1
from mongoengine.django.auth import User
import re
import hashlib
import json
import os
#from rest_framework.response import Response  
import operator
from django.conf import settings
import jieba

class DocumentPssTools(RequestTools):

    #   验证平台自动提交订单
    def validation_logistics_order(self, order):
        phone = self.get_parameter('phone', '')
        platform_id = self.get_parameter('platform_id', '')
        time_stamp = self.get_parameter('time_stamp', '')
        token = self.get_parameter('token').lower()
        if not phone:
            raise ParameterError('未找到phone参数')
        if not platform_id:
            raise ParameterError('未找到platform_id参数')
        if not time_stamp:
            raise ParameterError('未找到time_stamp参数')
        if not token:
            raise ParameterError('未找到token参数')
        logistics = Logistics.objects(id=platform_id).first()
        if not logistics:
            raise ParameterError('访问的权限不足')
        if not logistics.platform_key:
            raise ParameterError('联系运之宝人员设置key')
        client = Client.objects(profile__phone=phone).first()
        if client:
            token_user = hashlib.sha1((phone+logistics.platform_key+time_stamp).encode('utf-8')).hexdigest().lower()
            print('token-----------------'+token_user)
            print(token)
            if token_user != token:
                raise ParameterError('访问的token不正确')
            order.client = client
            order.organ = client.organ
            order.start_date = datetime.now()
            #   被保险人姓名
            insured = self.get_parameter("insured")
            if insured:
                order.insured = insured
            else:
                if client.company_name:
                    order.insured = client.company_name
                else:
                    order.insured = client.name
                    
            #test 
            insurance_price = self.get_parameter('insurance_price').strip()

            #   起运地
            startSiteName = self.get_parameter("startSiteName")
            if startSiteName:
                order.startSiteName = startSiteName
            else:
                raise ParameterError('起运地不能为空')

            #   目的地
            targetSiteName = self.get_parameter("targetSiteName")
            if targetSiteName:
                order.targetSiteName = targetSiteName
            else:
                raise ParameterError('目的地不能为空')

            # #保险起期
            # expectStartTime = self.get_parameter('expectStartTime').strip()
            # if expectStartTime:
            #     try:
            #         order.expectStartTime = expectStartTime
            #     except Exception:
            #         raise ParameterError("日期格式错误，请填写正确的日期格式")
            # else:
            #     raise ParameterError('承保日期不能为空')


            order.expectStartTime = datetime.now()

            product_type = self.get_parameter('product_type')
            if product_type == 'car':
                order.product_type = product_type
                #   运单号
                transport_id = self.get_parameter("transport_id")
                if transport_id:
                    order.transport_id = transport_id
                else:
                    raise ParameterError('请输入运单号')

                #   货物名称
                commodityName = self.get_parameter("commodityName")
                if commodityName:
                    order.commodityName = commodityName
                else:
                    raise ParameterError('缺失货物名称参数')

                #   货物数量
                commodityCases = self.get_parameter("commodityCases")
                if commodityCases:
                    try:
                        commodityCases=int(commodityCases)
                    except:
                        try:
                            commodityCases=float(commodityCases)
                        except:
                            raise ParameterError('输入的货物数量不为数字')
                    if commodityCases>0:
                        order.commodityCases = str(commodityCases)
                    elif  commodityCases==0:
                        raise ParameterError('货物数量不能为零')
                    else:
                        raise ParameterError('货物数量不能为负数')

                else:
                    raise ParameterError('缺失货物数量参数')

                if client.product_car:
                    order.insurance_product = client.product_car
                    order.company = client.product_car.company
                    order.insurance_type = client.product_car.insurance_type
                    order.insurance_rate = client.product_car.rate
                    order.product_type = client.product_car.product_type
                else:
                    raise ParameterError('用户没有设置关联产品，请联系运之宝负责人')

            elif product_type == 'batch':
                order.product_type = product_type
                #   车牌号
                self.request.POST.getlist('')
                plate_number = self.get_parameter("plate_number")
                # plate_number = re.match(r'^[\u4e00-\u9fa5]{1}[A-Z]{1}[A-Z_0-9]{5}$', plate_number)
                if plate_number:
                    order.plate_number = plate_number
                else:
                    raise ParameterError('车牌号错误')

                plate_number_plus = self.get_parameter('plate_number_plus')
                if plate_number_plus:
                    order.plate_number_plus = plate_number_plus

                batch_json_list = self.get_parameter('batch_list')
                batch_list = json.loads(batch_json_list)
                for batch in batch_list:
                    transport_id = batch.get('transport_id', '')
                    if not transport_id:
                        raise ParameterError("运单号不能为空")
                    startSiteName = batch.get('startSiteName', '')
                    if not startSiteName:
                        raise ParameterError("起运地不能为空")
                    targetSiteName = batch.get('targetSiteName', '')
                    if not targetSiteName:
                        raise ParameterError("目的地不能为空")
                    commodityName = batch.get('commodityName', '')
                    if not commodityName:
                        raise ParameterError("货物名称不能为空")
                    commodityCases = batch.get('commodityCases', '')
                    if not commodityCases:
                        raise ParameterError("货物数量不能为空")
                    batches = BatchList()

                    batches.transport_id = transport_id
                    batches.startSiteName = startSiteName
                    batches.targetSiteName = targetSiteName
                    batches.commodityName = commodityName
                    try:
                        commodityCases = int(commodityCases)
                        
                    except:
                        try:
                            commodityCases=float(commodityCases)
                        except ValueError:
                            raise ParameterError('货物数量必须是数字')
                    if commodityCases>0:
                        batches.commodityCases = str(commodityCases)
                    elif commodityCases==0:
                        raise ParameterError('货物数量不能为零')
                    else:
                        raise ParameterError('货物数量必须是正数')
                    order.batch_list.append(batches)
                # if 1 == 1:
                #     raise ParameterError("暂时性错误")

                if client.product_batch:
                    order.insurance_product = client.product_batch
                    order.company = client.product_batch.company
                    order.insurance_type = client.product_batch.insurance_type
                    order.insurance_rate = client.product_batch.rate
                    order.product_type = client.product_batch.product_type
                else:
                    raise ParameterError('用户没有设置关联产品，请联系运之宝负责人')

            elif product_type == 'ticket':
                order.product_type = product_type
                #   车牌号
                plate_number = self.get_parameter("plate_number")
                # plate_number = re.match(r'^[\u4e00-\u9fa5]{1}[A-Z]{1}[A-Z_0-9]{5}$', plate_number)
                if plate_number:
                    order.plate_number = plate_number

                plate_number_plus = self.get_parameter('plate_number_plus')
                if plate_number_plus:
                    order.plate_number_plus = plate_number_plus

                #   运单号
                transport_id = self.get_parameter("transport_id")
                if transport_id:
                    order.transport_id = transport_id

                if not transport_id and not plate_number:
                    raise ParameterError('车牌号和运单号至少填写一个')

                #   货物名称
                commodityName = self.get_parameter("commodityName")
                if commodityName:
                    order.commodityName = commodityName
                else:
                    raise ParameterError('缺失货物名称参数')

                #   货物数量
                commodityCases = self.get_parameter("commodityCases")
                if commodityCases:
                    try:
                        commodityCases=int(commodityCases)
                    except:
                        try:
                            commodityCases=float(commodityCases)
                        except:
                            raise ParameterError('货物数量不是数字类型数据')
                    if commodityCases<0:
                        raise ParameterError('货物数量不能为负数')
                    elif commodityCases==0:
                        raise ParameterError('货物数量不能为零')
                    else:
                        order.commodityCases = str(commodityCases)
                 
                    
                else:
                    raise ParameterError('缺失货物数量参数')

                if client.product_ticket:
                    order.insurance_product = client.product_ticket
                    order.company = client.product_ticket.company
                    order.insurance_type = client.product_ticket.insurance_type
                    order.insurance_rate = client.product_ticket.rate
                    order.product_type = client.product_ticket.product_type
                else:
                    raise ParameterError('用户没有设置关联产品，请联系运之宝负责人')
            else:
                raise ParameterError('投保的产品不存在')

            #保额
            insurance_price = self.get_parameter('insurance_price').strip()
            if insurance_price:
                if insurance_price:
                    try:
                        insurance_price = int(insurance_price)
                    except ValueError:
                        raise ParameterError("数据类型错误，请填写整数,单位为分")
                    if order.product_type == 'car':
                        if insurance_price > 2000000:
                            raise ParameterError('运单保险的货物价值上限20000元，请投单票保险')
                    elif order.product_type == 'batch':
                        pass
                    elif order.product_type == 'ticket':
                        if insurance_price < 2000000 or insurance_price > 200000000:
                            raise ParameterError('单票保险的货物价值在20000-2000000元之间')
                    else:
                        raise ParameterError("投保的产品不存在")
                    order.insurance_price = insurance_price
            else:
                raise ParameterError('保额不能为空')
        else:
            raise ParameterError('投保的用户不存在')
        return order

    def  validation_params(self,logistics,message):
         app_id = self.get_parameter('app_id').strip()
         if not app_id:
                message['code'] = "40001"
                message['message'] = "Invlid app_id"
                message['state'] = "0"
                return message
         app_secret = self.get_parameter('app_secret').strip()    
         if not app_secret:
                message['code'] = "40002"
                message['message'] = "Invlid app_secret"
                message['state'] = "0"
                return message
            
         if not logistics or logistics is None:
                message['code'] = "40003"
                message['message'] = "app_id、app_secret is not exists"
                message['state'] = "0"
                return message
         code = self.get_parameter('code').strip()     
         if not code or code != "yzbcode":
                message['code'] = "40004"
                message['message'] = "Invalid code"
                message['state'] = "0"
                return message
         grant_type = self.get_parameter('grant_type').strip()     
         if not grant_type or grant_type != "authorization_code":
                message['code'] = "40005"
                message['message'] = "grant_type error"
                message['state'] = "0"
                return message
         message = {'code':"0000","message":"ok","state":"1"}
         return message
     
    def validation_refresh_token_params(self,logistics,message):
         app_id = self.get_parameter('app_id').strip()
         if not app_id:
                return self.get_message_dict("40001","Invlid app_id","0")
            
         app_secret = self.get_parameter('app_secret').strip()    
         if not app_secret:
                return self.get_message_dict("40002","Invlid app_secret","0")
            
         if not logistics or logistics is None:
                return self.get_message_dict("40003","app_id、app_secret is not exists","0")
            
         grant_type = self.get_parameter('grant_type').strip()     
         if not grant_type or grant_type != "refresh_token":
                return self.get_message_dict("40005","grant_type error","0")
            
         message = {'code':"0000","message":"ok","state":"1"}
         return message
     
    def get_message_dict(self,code,message,state):
        data = {}
        data.setdefault("code",code)
        data.setdefault("message",message)
        data.setdefault("state",state) 
        return data
#     def check_Id_and_secret(app_id,app_secret):  
#          logistics = Logistics.objects(platform_key=app_id,platform_secret=app_secret).first()
#          if not logistics:
#              return True
#          else:
#              return False
        # #   提单号
        # blNo = self.get_parameter("blNo")
        # if blNo:
        #     order.blNo = blNo
        # else:
        #     raise ParameterError('请输入提单号')
        #
        # #   发货单号
        # freightNo = self.get_parameter("freightNo")
        # if freightNo:
        #     order.freightNo = freightNo
        #
        # #   发车批次
        # departGroup = self.get_parameter("departGroup")
        # if departGroup:
        #     order.departGroup = departGroup
        #
        # #   标的物代码
        # itemdetailcode = self.get_parameter("itemdetailcode")
        # if itemdetailcode:
        #     order.itemdetailcode = itemdetailcode
        # else:
        #     raise ParameterError('缺失标的物代码参数')
        # #   险别代码
        # kindCode = self.get_parameter("kindCode")
        # if kindCode:
        #     order.kindCode = kindCode
        # else:
        #     raise ParameterError('缺失险别代码参数')
        #
        # #   货物价值
        # goodsValue = self.get_parameter("goodsValue")
        # if goodsValue:
        #     order.goodsValue = goodsValue
        #
        # #   包装
        # packing = self.get_parameter("packing")
        # if packing:
        #     order.packing = packing
        #
        # #   件数
        # quantity = self.get_parameter("quantity")
        # if quantity:
        #     order.quantity = quantity
        #
        # #   预计营业收入
        # saleCount = self.get_parameter("saleCount")
        # if saleCount:
        #     order.saleCount = saleCount
        #
        # #   运输方式
        # transportType = self.get_parameter("transportType")
        # if transportType:
        #     order.transportType = transportType
        #
        # #   装载方式
        # loadType = self.get_parameter("loadType")
        # if loadType:
        #     order.loadType = loadType
        #
        # #       代收货款
        # deliveryPayment = self.get_parameter("deliveryPayment")
        # if deliveryPayment:
        #     order.deliveryPayment = deliveryPayment
        # else:
        #     raise ParameterError('缺失代收货款参数')
        #
        # #       实际运费
        # actualCost = self.get_parameter("actualCost")
        # if actualCost:
        #     order.actualCost = actualCost
        # else:
        #     raise ParameterError('缺失实际运费参数')
        #
        # #   收货人
        # consignee = self.get_parameter("consignee")
        # if consignee:
        #     order.consignee = consignee
        #
        # #   收货人电话
        # consigneeTel = self.get_parameter("consigneeTel")
        # if consigneeTel:
        #     order.consigneeTel = consigneeTel
        #
        # #   托运人
        # consignor = self.get_parameter("consignor")
        # if consignor:
        #     order.consignor = consignor
        #
        # #   托运人电话
        # consignorTel = self.get_parameter("consignorTel")
        # if consignorTel:
        #     order.consignorTel = consignorTel
        #
        # #   司机姓名
        # driverName = self.get_parameter("driverName")
        # if driverName:
        #     order.driverName = driverName
        #
        # #   司机电话
        # driverTel = self.get_parameter("driverTel")
        # if driverTel:
        #     order.driverTel = driverTel
        #
        # #   备注
        # remark = self.get_parameter("remark")
        # if remark:
        #     order.remark = remark
        #
        # #   重量
        # weight = self.get_parameter("weight")
        # if weight:
        #     order.trackingNo = weight
        #
        #
        #
        #
        # #   司机运费
        # driverFreight = self.get_parameter("driverFreight")
        # #   发站
        # departStation = self.get_parameter("departStation")
        # #   到站
        # departStation = self.get_parameter("departStation")
        # #   联系人
        # linkman = self.get_parameter("linkman")
        # #   联系电话
        # linkTel = self.get_parameter("linkTel")
        # #   通信地址
        # communicationAdd = self.get_parameter("communicationAdd")
        # #   到付
        # freightPayment = self.get_parameter("freightPayment")
        # #   现返
        # backCashMoment = self.get_parameter("backCashMoment")
        # #   欠返
        # backCashDebt = self.get_parameter("backCashDebt")
        # #   欠/月/回付
        # dmbPayment = self.get_parameter("dmbPayment")
        # #   到付
        # freightCollect = self.get_parameter("freightCollect")
        # #   货到打卡
        # goodStoClock = self.get_parameter("goodStoClock")
        # #   回单
        # receipt = self.get_parameter("receipt")
        # #   体积
        # volume = self.get_parameter("volume")
        # #   现付
        # payMoment = self.get_parameter("payMoment")
        
         
        
  #验证大东订单接口      
    def validation_dadong_order(self, order):
        phone = self.get_parameter('phone', '')
        if not phone:
            return self.get_message_dict("40012","未找到phone参数","0")
        client = Client.objects(profile__phone=phone).first()
        if client:        
            order.client = client
           # order.organ = client.organ
            order.start_date = datetime.now()
            order.expectStartTime = datetime.now()
            #   被保险人姓名
            insured = self.get_parameter("insured")
            if insured:         
                order.insured = client.company_name+"/"+insured
            else:
                order.insured = client.company_name

            #   起运地
            startSiteName = self.get_parameter("startSiteName")
            if startSiteName:
                order.startSiteName = startSiteName
            else:
                return self.get_message_dict("40013","起运地不能为空","0")

            #   目的地
            targetSiteName = self.get_parameter("targetSiteName")
            if targetSiteName:
                order.targetSiteName = targetSiteName
            else:
                return self.get_message_dict("40014","目的地不能为空","0")
            
            #运输方式
            transport_type = self.get_parameter("transport_type")
            if transport_type:
                order.transport_type = transport_type
            else:
                return self.get_message_dict("40015","运输方式不能为空","0")

            product_type = self.get_parameter('product_type')       
            if product_type == 'ticket':
                order.product_type = product_type
                
                 #   运单号
                transport_id = self.get_parameter("transport_id")
                if transport_id:
                    order.transport_id = transport_id
                else:
                    return self.get_message_dict("40016","运单号不能为空","0")
                    
                #   货物名称
                commodityName = self.get_parameter("commodityName")
                if commodityName:
                    order.commodityName = commodityName
                else:
                    return self.get_message_dict("40017","货物名称不能为空","0")

                #   货物数量
                commodityCases = self.get_parameter("commodityCases")
                if commodityCases:
                    try:
                        commodityCases=int(commodityCases)
                    except:
                        try:
                            commodityCases=float(commodityCases)
                        except:
                            return self.get_message_dict("40018","货物数量不是数字类型数据","0")
                    if commodityCases<0:
                        return self.get_message_dict("40019","货物数量不能为负数","0")
                    elif commodityCases==0:
                        return self.get_message_dict("40020","货物数量不能为零","0")
                    else:
                        order.commodityCases = str(commodityCases)                
                else:
                    return self.get_message_dict("40021","货物数量不能为空","0")
                #产品货物类型
                good_type = self.get_parameter("good_type")
                if good_type:
                             cargo_set = Cargo.objects(cargo_number=good_type).first()
                             if cargo_set:
                                         product =  client.product_ticket
                                         productCargo = ProductCargo.objects(cargo=cargo_set,product = product ).first()
                                         if productCargo:
                                               order.good_type = productCargo.state
                                               order.cargo = cargo_set
                                         else:
                                            return self.get_message_dict("40033","货物类型不在承保范围内","0")
                                               
                             else:
                                     return self.get_message_dict("40032","货物编码错误","0")
#                          a=InsuranceProducts()
#                          good_type_list=a.GOOD_TYPE
#                          for  good_type1 in good_type_list:
#                              if good_type == good_type1[1]:
#                                  good_type_test=good_type1[1]
#                                  break
#                          else:
#                              if good_type in order.COMMON_GOOD:
#                                 good_type_test = "普通货物"
#                              else:
#                                  return self.get_message_dict("40032","货物类型不在承保范围内","0")
#                          for pro in client.product_ticket.product_rate_list:
#                                     if  good_type_test == pro.good_type:
#                                         if good_type_test =="普通货物":
#                                             order.good_type = good_type_test
#                                             order.common_good_detail =  good_type  
#                                         else:
#                                             order.good_type = good_type_test
#                                         break
#   
# #                                         if  good_type_test = "普通货物":
# #                                                order.good_type = good_type_test
# #                                                order.common_good_detail =  good_type  
# #                                         else:    
# #                                                 order.good_type = good_type_test
# #                                             break
#                          if  not order.good_type:
#                               return self.get_message_dict("40033","产品无此货物类型","0")
                else:
                          return self.get_message_dict("40022","产品货物类型不能为空","0")
                
                if client.product_ticket:
                    order.insurance_product = client.product_ticket
                    order.company = client.product_ticket.company
                    order.insurance_type = client.product_ticket.insurance_type
                    order.product_type = client.product_ticket.product_type
                else:
                     return self.get_message_dict("40023","用户没有设置关联产品，请联系运之宝负责人","0")

            #保额
            insurance_price = self.get_parameter('insurance_price').strip()
            if insurance_price:
                    try:
                           insurance_price = float(insurance_price)*100  
                           insurance_price_int = int(insurance_price) 
                           if insurance_price>    insurance_price_int:
                                return self.get_message_dict("40034","保额数据错误，最多填写两位小数","0")
                           if insurance_price < 100000 or insurance_price > 200000000:
                                    return self.get_message_dict("40025","单票保险的保额在1000-2000000元之间","0")
                           else:
                                    order.insurance_price = insurance_price
                    except ValueError:
                             return self.get_message_dict("40024","保额数据类型错误，请填写数字 ","0")        
            else:
                return self.get_message_dict("40026","保额不能为空","0")
        else:
            return self.get_message_dict("40027","投保的用户不存在","0")
        return order
    
    
    # 一嗨 验证订单接口
    def yihai_validation_order(self, order):
        #产品类型
        product_type = self.get_parameter("product_type", "")
       #订单是创建还是编辑
        order_type = self.get_parameter("order_type", "")
        phone = self.get_parameter('phone', '')
        if not phone:
            return self.get_message_dict("40013","未找到phone参数","0")
        client = Client.objects(profile__phone=phone).first()
        if client:
            if ConvertTools.validate_choices(product_type, InsuranceProducts.PRODUCT_TYPE):
                order.product_type = product_type
                order.client = client

                #被保人姓名
                insured = self.get_parameter('insured').strip()
                if insured:
                    order.insured = insured
                else:
                    if client.company_name:
                        order.insured = client.company_name
                    else:
                        order.insured = client.name
                #起运地
                startSiteName_prov = self.get_parameter('startSiteName_prov').strip()
                startSiteName_city = self.get_parameter('startSiteName_city').strip()
                startSiteName_dist = self.get_parameter('startSiteName_dist').strip()
                if startSiteName_prov and startSiteName_city:
                    order.startSiteName = startSiteName_prov + ' '+startSiteName_city+' '+startSiteName_dist
                else:
                    return self.get_message_dict("40014","起运地不能为空","0")
 
                #目的地
                targetSiteName_prov = self.get_parameter('targetSiteName_prov').strip()
                targetSiteName_city = self.get_parameter('targetSiteName_city').strip()
                targetSiteName_dist = self.get_parameter('targetSiteName_dist').strip()
                if targetSiteName_prov and targetSiteName_city:
                    order.targetSiteName = targetSiteName_prov + " " + targetSiteName_city+" "+targetSiteName_dist
                else:
                    return self.get_message_dict("40015","目的地不能为空","0")
                
                #提单时间
                order.expectStartTime = datetime.now()

                #不同产品类型处理
                if product_type == 'car':
                    car_transport_id = self.get_parameter('car_transport_id').strip()
                    if car_transport_id:
                        order.transport_id = car_transport_id
                    else:
                        raise ParameterError('运单号不能为空')

                    car_commodityName = self.get_parameter('car_commodityName').strip()
                    if car_commodityName:
                        order.commodityName = car_commodityName
                    else:
                        raise ParameterError('货物名称不能为空')

                    car_commodityCases = self.get_parameter('car_commodityCases').strip()
                    if car_commodityCases:
                        order.commodityCases = car_commodityCases
                    else:
                        raise ParameterError('货物数量不能为空')
                elif product_type == 'batch':                   
                    #货物价值
                    batch_insurance_price =  self.get_parameter('batch_insurance_price').strip()
                    if batch_insurance_price:
                         order.insurance_price = int(float(batch_insurance_price)*100)
                    else:
                         raise ParameterError('货物价值不能为空')
                     
                    insuranceProducts = InsuranceProducts.objects(product_type=product_type,is_hidden=False)
                    productbatchsite = []
                    resultbatch = []
                    if insuranceProducts:
                           for insuranceProductsobj in insuranceProducts:
                                         if startSiteName_prov in insuranceProductsobj.no_insurable_route or targetSiteName_prov  in insuranceProductsobj.no_insurable_route:
                                                             continue
                                         else:
                                                             productbatchsite.append(insuranceProductsobj)
                           if  productbatchsite:
                                      for productbatchsiteobj in productbatchsite:
                                               if float(batch_insurance_price)>productbatchsiteobj.insurance_price_max/100 or float (batch_insurance_price)<productbatchsiteobj.insurance_price_min/100:
                                                                    continue
                                               else:
                                                                resultbatch.append(productbatchsiteobj)
                           else:
                                  raise ParameterError('此路线没有对应的产品')
                            
                           if resultbatch:
                                  resultbatch.sort(key = operator.attrgetter("priority"))  
                                  order.insurance_product = resultbatch[0]
                                  order.company = resultbatch[0].company
                                  order.product_type = resultbatch[0].product_type
                                  order.insurance_type = resultbatch[0].insurance_type
                                  order.insurance_rate = resultbatch[0].rate
                           else:
                                 raise ParameterError('货物价值没有对应的承保产品')
                                  
                                            
                    else:
                            raise ParameterError('无此产品类型的产品')
                     
                    #车牌号
                    batch_plate_number = self.get_parameter('batch_plate_number').strip()
                    if order_type == "edit":
                            if batch_plate_number :
                                if len(batch_plate_number) <= 10:
                                    order.plate_number = batch_plate_number
                                else:
                                    raise ParameterError('您输入的车牌号不正确')
                    else:
                            if batch_plate_number:
                                if len(batch_plate_number) <= 10:
                                    order.plate_number = batch_plate_number
                                else:
                                    raise ParameterError('您输入的车牌号不正确')
                            else:
                                raise ParameterError('车牌号不能为空')
                    
                    #挂车牌号
                    batch_plate_number_plus = self.get_parameter('batch_plate_number_plus').strip()
                    if batch_plate_number_plus:
                        order.plate_number_plus = batch_plate_number_plus

                    # 车次清单文档
                    batch_file = self.request.FILES.get('batch_file')
                    if batch_file:
                        document_tools = DocumentTools()
                        order.batch_url = document_tools.save(request_file=batch_file, file_folder=DocumentFolderType.batch, old_file='')

                    #车次清单图片
                    batch_image_list = self.request.FILES.getlist('batch_image_list', '')
                    print(batch_image_list)
                    if order_type == "edit":
                                order.batch_image_list = []
                    if batch_image_list:       
                        image_tool = ImageTools()
                        for batch_image in batch_image_list:
                            batch_image_url = image_tool.save(request_file=batch_image, file_folder=ImageFolderType.batch, old_file='')
                            if batch_image_url:
                                order.batch_image_list.append(batch_image_url)
                            else:
                                raise ParameterError('保存清单图片失败')
                

                    #车次清单list
                 
                    position_list = self.request.POST.getlist('position')
                    if order_type == "edit":
                                    order.batch_list = []
                    if len(position_list) > 0:
                      
                        for position in position_list:
                            try:
                                yd = self.request.POST.get("yd_" + position)
                                qyd = self.request.POST.get("qyd_" + position)
                                mdd = self.request.POST.get("mdd_" + position)
                                hwmc = self.request.POST.get("hwmc_" + position)
                                hwsl = self.request.POST.get("hwsl_" + position)
                                batches = BatchList()
                                if yd:
                                    batches.transport_id = yd
                                else:
                                    raise ParameterError('运单不能为空')
                                if qyd:
                                    batches.startSiteName = qyd
                                else:
                                    raise ParameterError('起运地不能为空')
                                if mdd:
                                    batches.targetSiteName = mdd
                                else:
                                    raise ParameterError('目的地不能为空')
                                if hwmc:
                                    batches.commodityName = hwmc
                                else:
                                    raise ParameterError('货物名称不能为空')
                                if hwsl:
                                    try:
                                        hwsl = int(hwsl)
                                    except:
                                        try:
                                            hwsl = float(hwsl)
                                        except:
                                            raise ParameterError('货物数量请输入数字')
                                    if hwsl>0:
                                        batches.commodityCases = hwsl
                                    else:
                                        raise ParameterError('货物数量请输入大于零的正数')
                                else:
                                    raise ParameterError('货物数量不能为空')
                                order.batch_list.append(batches)
                            except ParameterError as e:
                                raise e
                            except Exception as e:
                                pass
                    if order_type == "edit":
                               if not order.batch_list and not order.batch_image_list and not order.batch_url:
                                    raise ParameterError("保险清单内容，三选一")
                    else:       
                                if not position_list and not batch_image_list and not batch_file:
                                    raise ParameterError("保险清单内容，三选一")
                elif product_type == 'ticket':
                      #包装方式
                     wx_pack_detail_id = self.get_parameter('wx_pack_detail_id').strip()
                     if wx_pack_detail_id:
                          order.pack_method = wx_pack_detail_id
                     else:
                           return self.get_message_dict("40016","包装方式不能为空","0")
                       
                     #货物类型
                     wx_cargo_detail = self.get_parameter('wx_cargo_detail').strip()
                     if wx_cargo_detail:
                         try:
                             cargo_detail= Cargo.objects(cargo_number=wx_cargo_detail).first()
                         except:
                             return self.get_message_dict("40017","货物类型不能为空。","0")
                         order.cargo = cargo_detail
                     else:
                           return self.get_message_dict("40017","货物类型不能为空","0")
                       
                     #货物价值
                     insurance_price = self.get_parameter('insurance_price').strip()
                     if insurance_price:
                         order.insurance_price = int(float(insurance_price)*100)
                     else:
                         return self.get_message_dict("40018","货物价值不能为空","0")
                     
                     #过滤
                     resultlist5 = []
                     productCargosite = []
                     productCargo= []
                     cargo =Cargo.objects(cargo_number=wx_cargo_detail).first()
                     if  cargo:          
                                     order.cargo = cargo                                              
                                     productCargoall= ProductCargo.objects(cargo=cargo)  
                                     if productCargoall:
                                        for productCargoallobj in productCargoall:
                                                     if startSiteName_prov in productCargoallobj.product.no_insurable_route or targetSiteName_prov  in productCargoallobj.product.no_insurable_route:
                                                            continue
                                                     else:
                                                            productCargosite.append(productCargoallobj)  
                                     if productCargosite:
                                                     for productCargositeobj in productCargosite:
                                                           if float(insurance_price)>productCargositeobj.product.insurance_price_max/100 or float (insurance_price)<productCargositeobj.product.insurance_price_min/100:
                                                                    continue
                                                           else:
                                                               if  productCargositeobj.product.is_hidden == False:
                                                                        productCargo.append(productCargositeobj)
                                     else:
                                          return self.get_message_dict("40019","此路线没有可保产品","0")
                                                                                                                  
                                     if productCargo:             
                                             if    len(productCargo)==1:
                                                  for  rate  in   productCargo[0].product.product_rate_list:
                                                               if productCargo[0].product.company.paper_id == settings.ZHONGAN_COMPANY_CODE:             
                                                                                                if rate.good_type == productCargo[0].state:
                                                                                                         if  rate.insurance_rate* 10000000 / 10000000 *float(insurance_price)  <5:
                                                                                                                     order.insurance_company_rate = rate.insurance_rate
                                                                                                                     order.insurance_company_price =500
                                                                                                                     order.old_price =1000
                                                                                                                     order.insurance_product =  productCargo[0].product
                                                                                                                     order.insurance_rate = rate.products_rate
                                                                                                                     order.commission_ratio =rate.commission_ratio
                                                                                                                     order.good_type = rate.good_type
                                                                                                                     order.company =  productCargo[0].product.company
                                                                                                                     order.insurance_type = productCargo[0].product.insurance_type
                                                                                                         else:
                                                                                                                      order.insurance_company_rate = rate.insurance_rate
                                                                                                                      order.insurance_company_price =  int(rate.insurance_rate* 10000000 / 10000000 *float(insurance_price)*100)
                                                                                                                      order.old_price = int(rate.products_rate* 10000000 / 10000000 *float(insurance_price)*100)
                                                                                                                      order.insurance_product =  productCargo[0].product
                                                                                                                      order.insurance_rate = rate.products_rate
                                                                                                                      order.commission_ratio =rate.commission_ratio
                                                                                                                      order.good_type = rate.good_type
                                                                                                                      order.company =  productCargo[0].product.company
                                                                                                                      order.insurance_type = productCargo[0].product.insurance_type
                                                               else:
                                                                     if rate.good_type == productCargo[0].state:
                                                                                 order.insurance_company_rate = rate.insurance_rate
                                                                                 order.insurance_company_price = int(rate.insurance_rate* 10000000 / 10000000 *float(insurance_price)*100)
                                                                                 order.old_price =int(rate.products_rate* 10000000 / 10000000 *float(insurance_price)*100)
                                                                                 order.insurance_product =  productCargo[0].product
                                                                                 order.insurance_rate = rate.products_rate
                                                                                 order.commission_ratio =rate.commission_ratio
                                                                                 order.good_type = rate.good_type
                                                                                 order.company =  productCargo[0].product.company
                                                                                 order.insurance_type = productCargo[0].product.insurance_type
                                                                    
                                             elif  len(productCargo)>1:
                                                          for productcargo in productCargo:
                                                                     for  rate  in   productcargo.product.product_rate_list:
                                                                               if rate.good_type == productcargo.state:
                                                                                                         a = rate.insurance_rate* 10000000 / 10000000 *float(insurance_price)
                                                                                                         if  a <5:               
                                                                                                                          if productcargo.product.company.paper_id ==settings.ZHONGAN_COMPANY_CODE:
                                                                                                                                        break
                                                                                                                          else:
                                                                                                                               resultlist5.append( productcargo)
                                                                                                         else:
                                                                                                                              resultlist5.append( productcargo) 
                                                          resultlist5.sort(key = operator.attrgetter("product.priority"))                   
                                                          if resultlist5:
                                                                 for  rate  in   resultlist5[0].product.product_rate_list:
                                                                     if rate.good_type == resultlist5[0].state:
                                                                             order.insurance_company_rate = rate.insurance_rate
                                                                             order.insurance_company_price = int(rate.insurance_rate* 10000000 / 10000000 *float(insurance_price)*100)
                                                                             order.old_price = int(rate.products_rate* 10000000 / 10000000 *float(insurance_price)*100)
                                                                             order.insurance_product =   resultlist5[0].product
                                                                             order.insurance_rate = rate.products_rate
                                                                             order.commission_ratio =rate.commission_ratio
                                                                             order.good_type = rate.good_type
                                                                             order.company =  resultlist5[0].product.company
                                                                             order.insurance_type = resultlist5[0].product.insurance_type
                                                        
                                                          else:
                                                            return self.get_message_dict("40020","没有符合条件的产品","0")
                                             else:
                                                 return self.get_message_dict("40020","没有符合条件的产品","0")                                   
                                     else:
                                         return self.get_message_dict("40021","此货物价值没有可保产品","0")
                     else:
                         return self.get_message_dict("40022","此货物类型没有可保产品","0")
        
                    
                   #运单号
                     ticket_transport_id = self.get_parameter('ticket_transport_id').strip()
                     if ticket_transport_id:
                        order.transport_id = ticket_transport_id
                     #货物名称
                     ticket_commodityName = self.get_parameter('ticket_commodityName').strip()
                     if ticket_commodityName:
                        order.commodityName = ticket_commodityName
                     else:
                         return self.get_message_dict("40023","货物名称不能为空","0")
                     #货物数量
                     ticket_commodityCases = self.get_parameter('ticket_commodityCases').strip()
                     if ticket_commodityCases:
                        try:
                            ticket_commodityCases=int(ticket_commodityCases)
                        except:
                            try:
                                ticket_commodityCases=float(ticket_commodityCases)
                            except:
                                 return self.get_message_dict("40024","货物数量请输入数字","0")
                        if ticket_commodityCases>0:
                            order.commodityCases = str(ticket_commodityCases)
                        else:
                             return self.get_message_dict("40025","货物数量请输入大于零的数字","0")
                     else:
                        return self.get_message_dict("40026","货物数量不能为空","0")
                     #车牌号
                     batch_plate_number = self.get_parameter('batch_plate_number').strip()
        
                     if batch_plate_number:
                                            if len(batch_plate_number) <= 10:
                                                order.plate_number =  batch_plate_number
                                            else:
                                                return self.get_message_dict("40027","您输入的车牌号不正确","0")

                     if not ticket_transport_id and not ticket_plate_number:
                          return self.get_message_dict("40028","车牌号和运单号至少填写一个","0")
                else:
                    return self.get_message_dict("40029","非法的产品类型","0")
            else:
                return self.get_message_dict("40030","用户不存在","0")

        return order
     
     #货物类型翻译
    def cargo_name(self, value):
            cargo_set =Cargo.objects(cargo_number=value).first()
            if cargo_set:
                name=cargo_set.cargo_name
                return name
            else:
                message=cargo_number+"未找到对应货物"
                return message
            
     #包装方式类型翻译        
    def pack_method(self, value):
            num_pack=value
            print(num_pack)
            order = Ordering()
            pack_method_list=order.PACK_METHOD
            try:
                name = num_pack
                test =0
                for pack_method in pack_method_list:
                    for pack_detail in pack_method[1]:
                        if pack_detail[0]==num_pack:
                            name=pack_detail[1]
                            test=1
                            break
                    if test==1:
                        break
                if name==num_pack:
                      name=name+"未找到订单货物的包装方式"
                return name
            except:
                return "未找到订单对应的包装方式"
            
    #运输方式翻译        
    def transport_type(self, value):
            transport_number=value
            print("transport_number=="+transport_number)
            order = Ordering()
            transport_type_list=order.TRANSPORT_TYPE
            try:
                name = ""
                test =0
                for transport_type in transport_type_list:
                    if transport_type[0]==transport_number:
                        name=transport_type[1]
                        test=1
                        break
                if test ==1:
                    return name
                else:
                    message = transport_number +"未找到对应运输方式"
                    return message
            except:
                return "未找到订单对应的运输方式"
    #翻译地址编码        
    def address_name(self, value):
        address_number = value
        try:
            print(address_number)
            name_detail = address_number.split(" ")
            count = len(name_detail)
            address_detail=""
            for i in range(count):
                prov_code = name_detail[i]
                prov_name = CargoArea.objects(code=prov_code).first().name
                address_detail = address_detail + prov_name+" "
            return address_detail
        except:
            message = address_number+"未找到订单对应编码的地址名称"
            return message
        
        
        
           # 乐卡 验证订单接口
    def leka_validation_order(self, order):
        #产品类型
        product_type = self.get_parameter("product_type", "")
        phone = self.get_parameter('phone', '').strip() 
        if not phone:
            return self.get_message_dict("40013","未找到phone参数","0")
        client = Client.objects(profile__phone=phone).first()
        if client:
            if ConvertTools.validate_choices(product_type, InsuranceProducts.PRODUCT_TYPE):
                order.product_type = product_type
                order.client = client
                       
                #被保人姓名
                insured = self.get_parameter('insured')#个人是姓名，公司是公司名称
                if insured:
                    order.insured = insured
                else:
                    if client.company_name:
                        order.insured = client.company_name
                    else:
                        order.insured = client.name
                insured_certificate = self.get_parameter('insured_certificate')#个人是身份证，公司是营业执照
                if insured_certificate:
                    order.log_certificate_number = insured_certificate
                    
                    
                #起运地
                startSiteName = self.get_parameter('startSiteName').strip()        
#                 seg_list = jieba.cut(startSiteName)
#                 keyword = ' '.join(seg_list)
#                 keyword = keyword .split(" ")  #中间存在空格，变成数组
#                 if len(keyword) ==1:
#                         cargoshen = CargoArea.objects(Q(name__contains=keyword[0]),level="1").first()
#                         if  cargoshen:
#                               startSiteName_prov = cargoshen.code
#                 elif len(keyword) == 2:   
#                         cargoshen = CargoArea.objects(Q(name__contains=keyword[0]),level="1").first()
#                         if  cargoshen:
#                               startSiteName_prov = cargoshen.code   
#                         cargoshi = CargoArea.objects(name__contains=keyword[1],parentcode=cargoshen.code).first()
#                         if cargoshi:
#                               startSiteName_city= cargoshi.code   
#                 else:
#                         return self.get_message_dict("40014","起运地参数错误","0")  
#                 startSiteName_code = startSiteName_prov+ " " + startSiteName_city
                if startSiteName:
                     cargoshi = CargoArea.objects(Q(name__contains=startSiteName),level="2").first()
                     if cargoshi:
                          startSiteName_city = cargoshi.code
                          order.startSiteName = startSiteName_city
                     else:
                            return self.get_message_dict("40014","起运地不在可保范围","0")
                else:
                     return self.get_message_dict("40015","起运地不能为空","0")   
                  

                
                
                #目的地
                targetSiteName = self.get_parameter('targetSiteName').strip()        
#                 seg_list = jieba.cut( targetSiteName)
#                 keyword = ' '.join(seg_list)
#                 keyword = keyword .split(" ")  #中间存在空格，变成数组
#                 if len(keyword) ==1:
#                         cargoshen = CargoArea.objects(Q(name__contains=keyword[0]),level="1").first()
#                         if  cargoshen:
#                                targetSiteName_prov = cargoshen.code
#                 elif len(keyword) == 2:   
#                         cargoshen = CargoArea.objects(Q(name__contains=keyword[0]),level="1").first()
#                         if  cargoshen:
#                                targetSiteName_prov = cargoshen.code   
#                         cargoshi = CargoArea.objects(name__contains=keyword[1],parentcode=cargoshen.code).first() 
#                         if cargoshi:
#                                targetSiteName_city= cargoshi.code   
#                 else:
#                         return self.get_message_dict("40016","目的地参数错误","0")  
#                 targetSiteName_code =  targetSiteName_prov+ " " +  targetSiteName_city
                if   targetSiteName:
                     cargoshi = CargoArea.objects(Q(name__contains=targetSiteName),level="2").first()
                     if cargoshi:
                           targetSiteName_city = cargoshi.code
                           order.targetSiteName =   targetSiteName_city
                     else:
                            return self.get_message_dict("40016","目的地不在可保范围","0")
                else:
                     return self.get_message_dict("40017","目的地不能为空","0")  
                  
#                 if   targetSiteName_code:
#                      order. targetSiteName =  targetSiteName_code
#                 else:
#                     return self.get_message_dict("40017","目的地不能为空","0")
                
                #提单时间
                order.expectStartTime = datetime.now()

                #不同产品类型处理
                if product_type == 'car':
                              print("车次")
                elif product_type == 'batch':                   
                              print("运单")
                elif product_type == 'ticket':
                      #包装方式           
                     order.pack_method = "leka"                 

                     #货物价值
                     insurance_price = self.get_parameter('insurance_price').strip()
                     insurance_price = int(float(insurance_price))
                     if insurance_price:
                          if insurance_price > 5000000:
                                return self.get_message_dict("40032","货物价值范围是0到500万","0")
                          else:        
                                order.insurance_price = int(float(insurance_price)* 100)
                     else:
                         return self.get_message_dict("40018","货物价值不能为空","0")

                    
                   #运单号
                     ticket_transport_id = self.get_parameter('ticket_transport_id').strip()
                     if ticket_transport_id:
                        order.transport_id = ticket_transport_id
                     #货物名称
                     ticket_commodityName = self.get_parameter('ticket_commodityName').strip()
                     if ticket_commodityName:
                        order.commodityName = ticket_commodityName
                     else:
                         return self.get_message_dict("40019","货物名称不能为空","0")
                     #货物数量
                     ticket_commodityCases = self.get_parameter('ticket_commodityCases').strip()
                     if ticket_commodityCases:
                        try:
                            ticket_commodityCases=int(ticket_commodityCases)
                        except:
                            try:
                                ticket_commodityCases=float(ticket_commodityCases)
                            except:
                                 return self.get_message_dict("40020","货物数量请输入数字","0")
                        if ticket_commodityCases>0:
                            order.commodityCases = str(ticket_commodityCases)
                        else:
                             return self.get_message_dict("40021","货物数量请输入大于零的数字","0")
                     else:
                        return self.get_message_dict("40022","货物数量不能为空","0")
                     #车牌号
                     batch_plate_number = self.get_parameter('batch_plate_number').strip()
        
                     if batch_plate_number:
                                            if len(batch_plate_number) <= 10:
                                                order.plate_number =  batch_plate_number
                                            else:
                                                return self.get_message_dict("40023","您输入的车牌号不正确","0")

                     if not ticket_transport_id and not ticket_plate_number:
                          return self.get_message_dict("40024","车牌号和运单号至少填写一个","0")
                      
                      
                      #货物类型   
                     cargo =Cargo.objects(cargo_number="无").first()
                     if  cargo:          
                            order.cargo = cargo 
                     productresultlist = []        
                     productslist =  InsuranceProducts.objects(product_type="ticket")
                     if productslist:
                         for productobj in productslist:
                               if productobj.company.paper_id == settings.ZHONGAN_COMPANY_CODE:
                                         continue
                               else:
                                         productresultlist.append(productobj)
                     else:
                            return self.get_message_dict("40025","没有可保的产品","0")
                     productresultlist.sort(key = operator.attrgetter("priority"))       
                     if productresultlist:          
                             print(productresultlist[0])            
                             productCargo= ProductCargo.objects(product=productresultlist[0],cargo=cargo).first()
                             for rate in productresultlist[0].product_rate_list:
                                   if rate.good_type == productCargo.state:
                                         order.insurance_company_rate = rate.insurance_rate
                                         order.insurance_company_price = int(rate.insurance_rate* 10000000 / 10000000 *float(insurance_price)*100)
                                         order.insurance_product =   productresultlist[0]
                                         order.insurance_rate = rate.products_rate
                                         order.commission_ratio =rate.commission_ratio
                                         order.good_type = rate.good_type
                                         order.company =  productresultlist[0].company
                                         order.insurance_type = productresultlist[0].insurance_type                    
                     else:
                            return self.get_message_dict("40025","没有可保的产品","0")
        else:
                return self.get_message_dict("40026","用户不存在","0")

        return order


           # 砖头验证订单接口===20171023修正后
    def zhuantou_validation_order(self, order):
        #产品类型
        phone = self.get_parameter('phone', '').strip() 
        if not phone:
            return self.get_message_dict("400101","未找到phone参数","0")

        try:
            client = Client.objects(profile__phone=phone).first()
        except:
            return self.get_message_dict("400102","用户不存在，请检查填写的手机号","0")
        
        if  not client:
            return self.get_message_dict("400103","用户不存在","0")
        else:
            order.state = "init"
            order.product_type = 'car'
            order.client = client
        #筛选产品
        try:
            site_settings = SiteSettings.get_settings()
            paper_id=site_settings.product_code
            insurance_product_set = InsuranceProducts.objects()
            insurance_product_set = insurance_product_set.filter(paper_id=paper_id).first()
        except:
            return self.get_message_dict("400104","产品不存在，请联系管理员","0")
        if  not insurance_product_set:
            return self.get_message_dict("400105","未筛选出合适产品","0")
        else:
            order.insurance_product = insurance_product_set
            order.company = insurance_product_set.company
            order.product_type = insurance_product_set.product_type
            order.insurance_type = insurance_product_set.insurance_type
        #投保人
        if client:
            if client.company_name:
                order.client_name = client.company_name
            elif client.name:
                order.client_name = client.name
            else:
                order.client_name = phone
        #被保人姓名
        insured = self.get_parameter('insured')#个人是姓名，公司是公司名称
        if insured:
            if len(insured)>100:
                raise self.get_message_dict("400106","输入被保险人姓名过长，名称不可超过100位","0")
            order.insured = insured
        else:
            return self.get_message_dict("400107","未找到insured参数","0")
        #运输方式
        order.transport_type = '1'
        
        #起运地
        startSiteName = self.get_parameter('startSiteName').strip()        
        if startSiteName:
            order.car_startSiteName = startSiteName
        else:
            return self.get_message_dict("400108","未找到起运地参数","0")
        #目的地
        targetSiteName = self.get_parameter('targetSiteName').strip()        
        if targetSiteName:
            order.car_targetSiteName = targetSiteName
        else:
            return self.get_message_dict("400109","未找到目的地参数","0")
        #提单时间
        order.expectStartTime = datetime.now()
        
        #货物价值
        insurance_price = self.get_parameter('insurance_price').strip()        
        if insurance_price:
            try:
                insurance_price1=float(insurance_price)
                insurance_price2=insurance_price1*100
                insurance_price3=int(insurance_price2)
                if insurance_price2>insurance_price3:
                    return self.get_message_dict("400110","货物价值最多有两位小数","0")
            except:
                return self.get_message_dict("400111","货物价值应为数字","0")
            if insurance_price2<0:
                return self.get_message_dict("400112","货物价值不能为负数","0")
            order.insurance_price = insurance_price3
        else:
            return self.get_message_dict("400113","未找到货物价值参数","0")
 
        #运单号
        transport_id = self.get_parameter('transport_id').strip()
        if transport_id:
            if len(transport_id)>50:
                return self.get_message_dict("400115","输入运单号过长，不可超过50位","0")
            order.transport_id = transport_id
        else:
            return self.get_message_dict("400116","运单号不能为空","0")
        #货物名称
        commodityName = self.get_parameter('commodityName').strip()
        if commodityName:
            if len(commodityName)>200:
                return self.get_message_dict("400117","输入货物名称过长，不可超过200位","0")
            order.commodityName = commodityName
        else:
            return self.get_message_dict("400118","货物名称不能为空","0")
        #货物数量
        commodityCases = self.get_parameter('commodityCases').strip()
        if commodityCases:
            if len(commodityCases)>10:
                return self.get_message_dict("400119","输入货物数量过长，不可超过10位","0")
            try:
                commodityCases=int(commodityCases)
            except:
                try:
                    commodityCases=float(commodityCases)
                except:
                    return self.get_message_dict("400120","输入的货物数量应为大于零的数字","0")
            if commodityCases>0:
                order.commodityCases = str(commodityCases)
            else:
                return self.get_message_dict("400121","货物数量未大于零","0")
        else:
            return self.get_message_dict("400122","货物数量不能为空","0")

        return order