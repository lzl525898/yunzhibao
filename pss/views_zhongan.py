# -*- coding: utf-8 -*-
"""
众安保险公司调用测试

 作者: yzb
 创建时间: 2016-07-26 
 版本: 1.0

"""
__author__ = 'mlzx'
from pss.ZhongAnApiClient import ZhongAnApiClient
import collections
from django.template import RequestContext
from django.shortcuts import render_to_response
import json


from common.tools import *
import os
import time
import datetime
import jpype
from InsuranceSite.settings import BASE_DIR
import rsa 
import random
import string

#测试jpype
def runDemojava(request):
        context = RequestContext(request)
        if not jpype.isJVMStarted():
             jpype.startJVM(jpype.getDefaultJVMPath())     
             
        #测试码

        jpype.attachThreadToJVM()    
        jpype.java.lang.System.out.println( " hello world! ") 
        
#众安保险对接接口类        
class ZhongAnApi(RequestTools):
         #众安保险验证和出单接口
        def applyValidate(self, order_id):
            #TODO 指定环境 iTest:测试环境; uat:预发环境; prd:生产环境
          
            order = Ordering.objects(id=order_id).first()
            insurancePlatform = InsurancePlatform.objects(company = order.company).first()
                
            #env = "iTest"
            #env="prd"
            # TODO 开发者的appKey，由众安提供
           # appKey = "3890efac7ece7a646b18095aa424a9f9"
            for configobj in insurancePlatform.i_config:
               if configobj.c_key == "appKey":
                          appKey = configobj.c_value.strip()
               elif configobj.c_key == "channelId":
                          channelId = configobj.c_value.strip()
               elif configobj.c_key == "productNo":
                           productNo =  configobj.c_value.strip()
               elif configobj.c_key == "env":
                          env = configobj.c_value.strip()
               elif configobj.c_key == "privatekey":
                          privateKey = configobj.c_value.strip()
               elif configobj.c_key == "version":
                          version = configobj.c_value.strip()
            if order. plate_number:              
                    transNo = order. plate_number
            else:
                    randomlist = []
                    for i in range(5):
                          random_num = random.randint(0, 9) 
                          randomlist.append(str(random_num))
                    random_5 = ''.join(randomlist)
                    transNo ="黑A"+random_5
                   
            #TODO 开发者的私钥，由开发者通过openssl工具生成，不需要PKCS8转码
            #privateKey = '/pss/zhonganUtil/rsa_private_key.pem'
            
            serviceName = "zhongan.cargo.common.applyValidate"  
            expectStartTimes = (datetime.datetime.now()+datetime.timedelta(minutes= 5)).strftime('%Y-%m-%d  %H:%M:%S')
            #单票参数
            businessField = {}
            businessField['freightNo'] = order.transport_id     #运单号Y
            businessField['goodsWeight'] = ""                              #货物重量N
            businessField['goodsValue'] = order.insurance_price/100  #货物价值Y
            businessField['goodsName'] =  order.commodityName#货物名称
            businessField['packType'] = order.pack_method#包装类型 Y   编码格式
            businessField['amount'] = order.commodityCases  #货物数量Y
            businessField['goodsClass'] = order.cargo.cargo_number  #货物类型Y 编码格式
            businessField['transportType'] = order.transport_type   #运输方式Y 编码格式
            businessField['transNo'] = transNo      #order. plate_number       #车牌号Y
            businessField['expectStartTime'] = expectStartTimes#"2016-8-31  22:22:22"#expectStartTimes#起运日期Y和保险起期是一个格式为：YYYY-MM-DDHH：MM：SS
            businessField['departurePlace'] = self. getcargoAreacode(order.startSiteName) #起运地Y 编码格式
            businessField['destinationPlace'] = self.getcargoAreacode(order.targetSiteName)#目的地Y 编码格式
            businessField['isShowPremium'] = "N" #是否显示费率和保费 N
            businessField['isCarLoad'] = ""  #整车/零担N 1和2
            businessField['compensationLimit'] =  ""#赔偿限额N
            businessField['isInvoice'] =  ""#是否发票价N  Y和N
            businessField['isTax'] = "" #是否含税 N  Y和N
            businessField['loadType'] = ""#装载方式N   1：集装箱 2：非集装箱 3：箱式货车
            businessField['distance'] = ""      #运输距离
                      
            #基本参数
            paraminfo = {}
            paraminfo['channelOrderNo'] = order.paper_id   #渠道订单号唯一不可重复Y              
            paraminfo['channelId'] = channelId#"1287" #渠道ID固定值，由众安提供Y 
            paraminfo['productNo'] = productNo#"1416c49773a6a09902550c963757b21572ef721d32 "#产品ID固定值，由众安提供Y     
            paraminfo['coverage'] = ""#保额N
            paraminfo['premium'] = ""#保费N                   
            paraminfo['holderName'] = order.client.name#投保人名称Y              
            paraminfo['holderType'] = "100"  #投保人类型Y  100：个人  201：公司 
            paraminfo['holderCertType'] =  "I"#投保人证件类型Y   I：身份证  YY：营业执照  P：护照  Z：组织机构代码证 SW：税务登记证     
            paraminfo['holderCertNo'] = order.client.national_id#"91120106MA0025431x"#投保人证件号码Y  
            paraminfo['holderEmail'] = ""#投保人电子邮件N              
            paraminfo['holderLinkName'] = order.client.name#投保人联系姓名Y 
            paraminfo['holderTel'] = ""#投保人联系电话N     
            paraminfo['holderPostCode'] = ""#投保人邮编N     
            paraminfo['holderAddress'] = ""#投保人地址N              
            paraminfo['insureName'] = order.insured#被保险人名称Y 
            paraminfo['insureType'] = "100"#被保险人类型Y  100：个人  201：公司     
            paraminfo['insureCertType'] = "I"#"SW"#被保险人人证件类型Y   I：身份证  YY：营业执照  P：护照  Z：组织机构代码证 SW：税务登记证  
            paraminfo['insureCertNo'] = order.client.national_id#"110106MA0025432"#被保险人证件号码Y              
            paraminfo['insureEmail'] = ""#被保险人电子邮件N 
            paraminfo['insureLinkName'] = order.insured#被保险人姓名Y     
            paraminfo['insureTel'] = ""#被保险人联系电话N     
            paraminfo['insurePostCode'] = ""     #被保险人邮编N              
            paraminfo['insureAddress'] = ""#被保险人地址N 
            paraminfo['businessField'] = businessField   #险种业务字段

            paramdict = {"param":paraminfo
                   }
            paramsjson = json.dumps(paramdict)
            client = ZhongAnApiClient (env, appKey, privateKey, serviceName,version) 
            response = client.call (paramsjson)    
            return response
             
        #获取众安保险地址编码
        def getcargoArea(self,SiteName) :    
            startSiteNamelist = SiteName.split()
            zhixiashi = "北京市天津市上海市重庆市"
            count = len(startSiteNamelist)
            cargoshen = CargoArea.objects(Q(name__contains=startSiteNamelist[0]) )
            print(cargoshen.count())
            if  cargoshen:
                    for cargoshenobj in cargoshen:
                            if cargoshenobj.level =="1":
                                    if cargoshenobj.name in zhixiashi:
                                                  cargoshi = CargoArea.objects(name__contains=startSiteNamelist[0],parentcode=cargoshenobj.code) 
                                    else:
                                                  cargoshi = CargoArea.objects(name__contains=startSiteNamelist[1],parentcode=cargoshenobj.code) 
                                    if cargoshi:
                                                for cargoshiobj in cargoshi:
                                                            if cargoshiobj.level =="2":
                                                                     if cargoshiobj.name in zhixiashi:
                                                                               cargoxian = CargoArea.objects(name__contains=startSiteNamelist[1][:-1],parentcode=cargoshiobj.code )
                                                                     else:
                                                                               cargoxian = CargoArea.objects(name__contains=startSiteNamelist[2][:-1],parentcode=cargoshiobj.code )
                                                                     if cargoxian:
                                                                              for cargoxianobj in cargoxian:
                                                                                    if cargoxianobj.level =="3":
                                                                                          startSiteName = cargoxianobj.code
                                                                                    else:
                                                                                          startSiteName = cargoshiobj.code
                                                                     else:
                                                                          startSiteName = cargoshiobj.code
                                                            else:
                                                                  startSiteName = cargoshenobj.code
                                    else:
                                              cargoshi = CargoArea.objects(name__contains=startSiteNamelist[1])
                                              if  cargoshi:
                                                    for cargoshiobj in cargoshi:
                                                        if cargoshiobj.code[0:2] == cargoshenobj.code:
                                                                  startSiteName   = cargoshiobj.code
                                                        else:
                                                                  startSiteName = cargoshenobj.code
                                              else:
                                                    startSiteName = cargoshenobj.code
                            else:
                                      startSiteName = ""     
            else:
                        startSiteName = ""                            
            return     startSiteName      

        #获取投保地址编码                             
        def getcargoAreacode(self,SiteName) :    
               startSiteNamelist = SiteName.split()
               if  len(startSiteNamelist) >0:
                     sitecode =  startSiteNamelist[-1]
               return sitecode
               