#_*_coding:utf-8_*_
from symbol import parameters
__author__ = 'mlzx'

from common.tools_legoo import DocumentTools, DocumentFolderType, ImageTools, ImageFolderType
from common.tools import RequestTools
from common.tools import ConvertTools
from common.models import *
from django.contrib.auth import authenticate
from datetime import timedelta
from common.interface_helper import *
from uuid import uuid1
from mongoengine.django.auth import User
import re
#2016-12-19判断众安公司方法
from django.conf import settings
import xlrd
from xlrd import xldate_as_tuple
from wss.views_sendmessage import  send_wx_message
#压缩图片
from PIL import Image
import os


class DocumentBmsTools(RequestTools):

    #   验证保险公司
    def validation_head_company(self, head_company):
        name = self.get_parameter("name").strip()
        if name:
            if len(name)>20:
                raise ParameterError('保险公司名称过长，名称不可超过20个字符')
            else:
                head_company.name = name
#             head_company.name = name
        else:
            raise ParameterError('保险公司名称不能为空')
        description = self.get_parameter('description').strip()
        head_company.description = description
        phone = self.get_parameter('phone').strip()
        head_company.phone = phone
        # docking_rate = self.get_parameter('docking_rate').strip()
        # if docking_rate:
        #     try:
        #         docking_rate = float(docking_rate)
        #         company.docking_rate = docking_rate
        #     except Exception:
        #         raise ParameterError("系统对接投保基础费率类型错误")
        # else:
        #     raise ParameterError('系统对接投保基础费率不能为空')
        # car_rate = self.get_parameter('car_rate').strip()
        # if car_rate:
        #     try:
        #         car_rate = float(car_rate)
        #         company.car_rate = car_rate
        #     except Exception:
        #         raise ParameterError("单票投保费率类型错误")
        # else:
        #     raise ParameterError('单车单次投保基础费率不能为空')
        # batch_rate = self.get_parameter('batch_rate').strip()
        # if batch_rate:
        #     try:
        #         batch_rate = float(batch_rate)
        #         company.batch_rate = batch_rate
        #     except Exception:
        #         raise ParameterError("单票货物投保基础费类型错误")
        # else:
        #     raise ParameterError('单票货物投保基础费率不能为空')
        return head_company

    #   验证保险分公司
    def validation_tail_company(self, tail_company):
        name = self.get_parameter("name").strip()
        if name:
            if len(name)>20:
                raise ParameterError('保险公司名称过长，名称不可超过20个字符')
            else:
                tail_company.name = name
        else:
            raise ParameterError('保险公司名称不能为空')
        simple_name = self.get_parameter("simple_name").strip()
        if simple_name:
            if len(simple_name)>10:
                raise ParameterError('保险公司简称过长，分公司简称不可超过10个字符')
            else:
                tail_company.simple_name = simple_name
        else:
            raise ParameterError('保险公司简称不能为空')
        head_company_id = self.get_parameter("head_company_id").strip()
        if head_company_id:
            head_company = InsuranceCompanyParent.objects(id=head_company_id).first()
            if head_company:
                tail_company.parent = head_company
            else:
                raise ParameterError('您选择的总公司不存在')
        else:
            raise ParameterError('请选择总公司')
        return tail_company

    #   验证保险文档
    def validation_document(self, insurance_document):
        name = self.get_parameter("name").strip()
        if name:
            insurance_document.name = name
        else:
            raise ParameterError('保险文档名称不能为空')
        simple_name = self.get_parameter('simple_name').strip()
        if len(simple_name) <= 10:
            insurance_document.simple_name = simple_name
        else:
            raise ParameterError('文档简称长度不能大于10个字符')
        note = self.get_parameter('note').strip()
        insurance_document.note = note

        company_id = self.get_parameter('company_id').strip()
        if company_id:
            company = InsuranceCompany.objects(id=company_id).first()
            if company:
                insurance_document.company = company
            else:
                raise ParameterError("您选择的保险公司不存在")
        else:
            raise ParameterError("请选择文档所属保险公司")

        content = self.get_parameter('content')
        insurance_document.content = content

        document_file = self.request.FILES.get('document_file')
        if document_file:
            document_tools = DocumentTools()
            insurance_document.file_url = document_tools.save(request_file=document_file, file_folder=DocumentFolderType.document, old_file='')
        elif not insurance_document.file_url:
            raise ParameterError('文档不能为空')

        # insurance_document.save()
        # # 产品
        # product_ids = self.request.POST.getlist('insurance_product', [])
        # if product_ids:
        #     insurance_products = InsuranceProducts.objects(id__in=product_ids)
        #     for insurance_product in insurance_products:
        #         if insurance_document not in insurance_product.documents:
        #             insurance_product.documents.append(insurance_document)
        #             insurance_product.save()
        return insurance_document

    #   验证产品
    def validation_insurance_product(self, insurance_product):
        name = self.get_parameter("name").strip()
        if name:
            insurance_product.name = name
        else:
            raise ParameterError('产品名称不能为空')
        # 产品类型
        product_type = self.get_parameter('product_type').strip()
        if product_type:
            insurance_product.product_type = product_type
        else:
            raise ParameterError("您选择的产品类型不存在")
        # 产品优先级
        product_priority = self.get_parameter('product_priority').strip()
        if product_priority:
            product_priority = int(product_priority)
            if product_priority >=1 and product_priority <= 100:
                product_list_count =  InsuranceProducts.objects( priority = product_priority , product_type = product_type ).count()
                if product_list_count >1:
                    if product_type !="jdclbx":
                        raise ParameterError("您创建的产品优先级已存在请选择其他数字")
                elif product_list_count ==1:
                    product_set =  InsuranceProducts.objects( priority = product_priority , product_type = product_type ).first()
                    if product_set.id != insurance_product.id:
                        if product_type !="jdclbx":
                            raise ParameterError("您创建的产品优先级已存在请选择其他数字")
                else:
                    insurance_product.priority = product_priority
            else:
                raise ParameterError("产品优先级应为1至100的整数")
        else:
            insurance_product.priority = 50
            
        # 产品免赔
        deductible = self.get_parameter('deductible').strip()
        if deductible:
            if len(deductible)>1000:
                raise ParameterError("填写的产品免赔内容过长")
            insurance_product.deductible = deductible
        else:
            raise ParameterError("请填写产品免赔")
        # 2017/07/03产品险别
        risks = self.get_parameter('risks').strip()
        if risks:
            if len(risks)>1000:
                raise ParameterError("填写的产品险别内容过长")
            insurance_product.risks = risks
        else:
            raise ParameterError("请填写产品险别")
            
        # 2017/05/22添加产品对接字段
        create_way = self.get_parameter('create_way').strip()
        if create_way:
            insurance_product.create_way = create_way
        else:
            raise ParameterError("请选择产品来源")
        
        if create_way !='yzb':
            third_party_url = self.get_parameter('third_party_url').strip()
            third_product_number = self.get_parameter('third_product_number').strip()
            merchant_number = self.get_parameter('merchant_number').strip()
            if not third_party_url or not third_product_number or not merchant_number:
                raise ParameterError("创建的产品来源第三方，第三方接口地址，第三方产品编号，第三方渠道商户编码必须全部填写")
            else:
                insurance_product.third_party_url=third_party_url
                insurance_product.third_product_number=third_product_number
                insurance_product.merchant_number=merchant_number
        else:
            insurance_product.third_party_url=''
            insurance_product.third_product_number=''
            insurance_product.merchant_number=''
            
        #2017/6/1添加产品可报用户类型
        a=1
        if create_way =='hjb':
            choose_user_list =self.request.REQUEST.getlist("choose_user")
            if len(choose_user_list)==0:
                raise ParameterError("创建的产品来源于汇聚宝公司，请填写产品可承包被保人身份")
            user_type_list = []
            try:
                for  user_type in choose_user_list:
                    print(user_type)
                    user_type_list.append(user_type)
                insurance_product.user_type_list =user_type_list
            except Exception as e:
                raise ParameterError( str(e))
        
        # 2017/06/2添加产品最低保费控制
        #保险公司最低保费
        insurance_lowest_price = self.get_parameter('insurance_lowest_price').strip()
        if insurance_lowest_price:
            try:
                insurance_lowest_price1= float(insurance_lowest_price)*100
            except:
                raise ParameterError( '保险公司最低保费应为数字')
            try:
                insurance_lowest_price2= int(insurance_lowest_price1)
            except:
                raise ParameterError( '保险公司最低保费应为数字。')
            if insurance_lowest_price1>insurance_lowest_price2 or insurance_lowest_price1<0:
                raise ParameterError( '保险公司最低保费最多为两位小数的正数。')
            insurance_product.insurance_lowest_price = insurance_lowest_price2
        else:
            raise ParameterError("请输入保险公司最低保费")
        
        #运之宝最低保费
        lowest_price = self.get_parameter('lowest_price').strip()
        if lowest_price:
            try:
                lowest_price1= float(lowest_price)*100
            except:
                raise ParameterError( '运之宝最低保费应为数字')
            try:
                lowest_price2= int(lowest_price)*100
            except:
                raise ParameterError( '运之宝最低保费应为数字。')
            if lowest_price1>lowest_price2 or lowest_price1<0:
                raise ParameterError( '运之宝最低保费最多为两位小数的正数。')
            if lowest_price2<insurance_lowest_price2:
                raise ParameterError( '运之宝最低保费不能小于保险公司最低保费。')
            insurance_product.lowest_price = lowest_price2
        else:
            raise ParameterError("请输入运之宝最低保费")
        
        if product_type=="jdclbx":
            insurance_product.intermediarys = []
            intermediarys_ids = self.request.POST.getlist('choose_intermediary', [])
            if intermediarys_ids:
                try:
                    insurance_intermediarys = Intermediary.objects(id__in=intermediarys_ids)
                    for insurance_intermediary in insurance_intermediarys:
                        if insurance_intermediary not in insurance_product.intermediarys:
                            insurance_product.intermediarys.append(insurance_intermediary)
                except:
                    raise ParameterError("中介渠道查询出错，请稍后再试")
            else:
                print("未选择中介渠道")
        
        #产品费率
        elif product_type=="batch":
            #可保货物价值
            insurance_price_min = self.get_parameter('insurance_price_min').strip()
            if insurance_price_min:
                insurance_price_min = int(insurance_price_min)
                if insurance_price_min<0:
                    raise ParameterError("可保货物金额不能为负数")
                try:
                    insurance_price_min1 = insurance_price_min * 100
                    insurance_product.insurance_price_min = insurance_price_min1
                except Exception:
                    raise ParameterError("可保货物金额异常")
            else:
                raise ParameterError('可保货物金额不能为空')
            
            
            #可保货物价值最大值
            insurance_price_max = self.get_parameter('insurance_price_max').strip()
            if insurance_price_max:
                insurance_price_max = int(insurance_price_max)
                if insurance_price_max<0:
                    raise ParameterError("可保货物金额不能为负数")
                if insurance_price_max <insurance_price_min:
                    raise ParameterError("可保货物金额最大值应大于最小值")
                try:
                    insurance_price_max1 = insurance_price_max * 100
                    insurance_product.insurance_price_max = insurance_price_max1
                except Exception:
                    raise ParameterError("可保货物金额异常")
            else:
                raise ParameterError('可保货物金额不能为空')
            
            
            commission_ratio = self.get_parameter('commission_ratio').strip()
            if commission_ratio:
                try:
                    commission_ratio = float(commission_ratio)
                except Exception:
                    raise ParameterError("手续费比例异常，只能输入两位小数的数字")
                if commission_ratio == 0.0:
                    commission_ratio = float(commission_ratio)
                    insurance_product.commission_ratio = commission_ratio
                    #raise ParameterError("手续费比例不能为0")
                else:
                    insurance_product.commission_ratio = commission_ratio
            else:
                raise ParameterError('手续费比例不能为空')
            
            
            rate = self.get_parameter('rate').strip()
            if rate:
                try:
                    rate = float(rate)
                    insurance_product.rate = rate
                    insurance_product.product_rate_list=[] #清空货物类型费率清单列表
                except Exception:
                    raise ParameterError("费率类型异常")
            else:
                raise ParameterError('费率不能为空')
            
            insurance_company_rate = self.get_parameter('insurance_company_rate').strip()
            if insurance_company_rate:
                try:
                    insurance_company_rate = float(insurance_company_rate)
                    insurance_product.insurance_company_rate = insurance_company_rate
                except Exception:
                    raise ParameterError("保险公司费率异常，只能输入两位小数的数字")
            else:
                raise ParameterError('保险公司费率不能为空')
            
        elif product_type=="car":
            commission_ratio = self.get_parameter('commission_ratio').strip()
            if commission_ratio:
                try:
                    commission_ratio = float(commission_ratio)
                    #insurance_product.commission_ratio = commission_ratio
                except Exception:
                    raise ParameterError("手续费比例异常，只能输入两位小数的数字")
                if commission_ratio == 0.0:
                    insurance_product.commission_ratio = 0.0
                    #raise ParameterError("手续费比例不能为0")
                else:
                    insurance_product.commission_ratio = commission_ratio
            else:
                raise ParameterError('手续费比例不能为空')
            
            rate = self.get_parameter('rate').strip()
            if rate:
                try:
                    rate = float(rate)
                    insurance_product.rate = rate
                    insurance_product.product_rate_list=[] #清空货物类型费率清单列表
                except Exception:
                    raise ParameterError("费率类型异常")
            else:
                raise ParameterError('费率不能为空')

            insurance_company_rate = self.get_parameter('insurance_company_rate').strip()
            if insurance_company_rate:
                try:
                    insurance_company_rate = float(insurance_company_rate)
                    insurance_product.insurance_company_rate = insurance_company_rate
                except Exception:
                    raise ParameterError("保险公司费率异常，只能输入两位小数的数字")
            else:
                raise ParameterError('保险公司费率不能为空')

        # 货物类型费率清单
        elif  product_type=="ticket":
            #可保货物价值
            insurance_price_min = self.get_parameter('insurance_price_min').strip()
            if insurance_price_min:
                insurance_price_min = int(insurance_price_min)
                if insurance_price_min<0:
                    raise ParameterError("可保货物金额不能为负数")
                try:
                    insurance_price_min1 = insurance_price_min * 100
                    insurance_product.insurance_price_min = insurance_price_min1
                except Exception:
                    raise ParameterError("可保货物金额异常")
            else:
                raise ParameterError('可保货物金额不能为空')
            
            
            #可保货物价值最大值
            insurance_price_max = self.get_parameter('insurance_price_max').strip()
            if insurance_price_max:
                insurance_price_max = int(insurance_price_max)
                if insurance_price_max<0:
                    raise ParameterError("可保货物金额不能为负数")
                if insurance_price_max <insurance_price_min:
                    raise ParameterError("可保货物金额最大值应大于最小值")
                try:
                    insurance_price_max1 = insurance_price_max * 100
                    insurance_product.insurance_price_max = insurance_price_max1
                except Exception:
                    raise ParameterError("可保货物金额异常")
            else:
                raise ParameterError('可保货物金额不能为空')
            
            #产品费率列表
            insurance_product.rate = 0
            product_rate_list =self.request.POST.getlist('position')
            product_state=self.request.POST.getlist('insurance_state')
            insurance_product.product_rate_list=[]
            hwlx_list=[]
            if len(product_rate_list)>0:
                insurance_product.rate = 0.0
                for product_rate in product_rate_list:
                    try:
                        hwlx = self.request.POST.get("hwlx_" + product_rate)
                        cpfl = self.request.POST.get("cpfl_" + product_rate)
                        bxfl = self.request.POST.get("bxfl_" + product_rate)
                        sxfbl = self.request.POST.get("sxfbl_" + product_rate)
                        products_rate=ProductsRateList()
                    except:
                        raise ParameterError('产品货物费率清单初始化失败')
                    if hwlx:
                        try:
                            products_rate.good_type=hwlx
                            hwlx_list.append( hwlx )
                        except:
                            raise ParameterError('货物类型格式不正确')
                    else:
                        raise ParameterError('货物类型清单中有货物类型选项未选择')
                    if cpfl:
                        try:
                            cpfl = float(cpfl)
                            products_rate.products_rate=cpfl
                        except:
                            raise ParameterError('货物产品费率格式不正确')
                    else:
                        raise ParameterError('所有的产品费率不能为空')
                    if bxfl:
                        try:
                            bxfl = float(bxfl)
                            products_rate.insurance_rate=bxfl
                        except:
                            raise ParameterError('货物保险费率格式不正确')
                    else:
                        raise ParameterError('所有的保险费率不能为空')
                    if sxfbl:
                        try:
                            sxfbl = float(sxfbl)
                        except:
                            raise ParameterError('手续费比例格式不正确')
                        if sxfbl ==0.0:
                            products_rate.commission_ratio=sxfbl
                        else:
                            products_rate.commission_ratio=sxfbl
                        
                    else:
                        raise ParameterError('所有的手续费比例不能为空')
                    try:
                        insurance_product.product_rate_list.append( products_rate )
                    except:
                        raise ParameterError('货物类型，存储过程出错，请检查输入费率部分不能为空')
                    if len(hwlx_list)==len(set(hwlx_list)):
                        print("产品货物类型无重复项")
                    else:
                        raise ParameterError('产品货物类型不可有重复项，请重新选择')
            else:
                raise ParameterError("您未输入货物类型费率清单")
        else:
            raise ParameterError("产品类型暂不可保请重新选择")
        
        # 公司
        tail_company_id = self.get_parameter('tail_company_id').strip()
        if tail_company_id:
            company = InsuranceCompany.objects(id=tail_company_id).first()
            if company:
                insurance_product.company = company
            else:
                raise ParameterError("您选择的保险公司不存在")
        else:
            if product_type!="jdclbx":
                raise ParameterError("您未选择保险公司")

        # 险种类型
        insurance_type = self.get_parameter('insurance_type').strip()
        if insurance_type:
            insurance_product.insurance_type = insurance_type
        else:
            raise ParameterError("您选择的险种类型不存在")


        return insurance_product

    #   验证订单
    def validation_order(self, order):
        # 公司
        company_id = self.get_parameter('company_id').strip()
        if company_id:
            company = InsuranceCompany.objects(id=company_id).first()

            if company:
                order.company = company
            else:
                raise ParameterError('保险公司不存在')
        else:
            raise ParameterError('保险公司不能为空')
        #产品
        insurance_product_id = self.get_parameter('insurance_product_id').strip()
        if insurance_product_id:
            insurance_product = InsuranceProducts.objects(id=insurance_product_id).first()
            if insurance_product:
                order.insurance_product = insurance_product
                order.product_type = insurance_product.product_type
                order.insurance_type = insurance_product.insurance_type
#                 order.insurance_rate = insurance_product.rate#查看不同类型订单对应费率
            else:
                raise ParameterError('产品不存在')
        else:
            raise ParameterError('产品不能为空')
        #货物运输方式 -
        transport_type=self.get_parameter("transport_type_id").strip()
        if transport_type:
            order.transport_type = transport_type
        else:
            order.transport_type = '1'
        #投保人
        client_id = self.get_parameter('client_id').strip()
        if client_id:
            client = Client.objects(id=client_id).first()
            if client:
                order.client = client
            else:
                raise ParameterError('客户不存在')
        else:
            raise ParameterError('客户不能为空')
        #投保人身份
        client_type=self.get_parameter("client_type").strip()
        client_detail=''
        if client_type:
            if client_type== 'person':
                client_detail='个人'
            if client_type == 'company':
                client_detail='物流公司'
            if client_type not in insurance_product.user_type_list:
                raise ParameterError('所选产品不可承包被报人身份为'+str(client_detail)+'的用户')
            order.client_type = client_type
        else:
            raise ParameterError('被保人身份不能为空')
        
        #投保人姓名
        client_name = self.get_parameter('client_name').strip()
        if client_name:
            if len(client_name)>50:
                raise ParameterError('输入投保人姓名过长，长度不可超过50位')
            order.client_name = client_name
        else:
            if client.company_name:
                order.client_name = client.company_name
            elif client.name:
                order.client_name = client.name
            else:
                raise ParameterError('请输入投保人姓名')
            
        #投保人身份证号
#         client_id_card = self.get_parameter('client_id_card').strip()
#         if client_id_card:
#             if len(client_id_card)>19:
#                 raise ParameterError('输入投保人证件号过长，号码长度不可超过19位')
#             order.client_id_card = client_id_card
#         else:
#             if client.organ:
#                 order.client_id_card = client.organ
#             elif client.business_license_id:
#                 order.client_id_card = client.business_license_id    
#             elif client.national_id:
#                 order.client_id_card = client.national_id
#             else:
#                 raise ParameterError('请输入投保人证件号')

        #被投保人姓名
        insured = self.get_parameter('insured').strip()
        if insured:
            if len(insured)>50:
                raise ParameterError('输入被保险人姓名过长，名称不可超过50位')
            order.insured = insured
        else:
            if order.client_name:
                order.insured = order.client_name
            else:
                raise ParameterError('请输入被保险人姓名')

        
        #被投保人身份证号
#         insured_id_card = self.get_parameter('insured_id_card').strip()
#         if insured_id_card:
#             if len(insured_id_card)>19:
#                 raise ParameterError('输入被保险人证件号过长，号码长度不可超过19位')
#             order.insured_id_card = insured_id_card
#         else:
#             if order.client_id_card:
#                 order.insured_id_card = order.client_id_card
#             else:
#                 raise ParameterError('请输入被保险人证件号')   
                

        #起运地
        startSiteName_prov = self.get_parameter('startSiteName_prov').strip()
        startSiteName_city = self.get_parameter('startSiteName_city').strip()
        startSiteName_dist = self.get_parameter('startSiteName_dist').strip()
        if startSiteName_prov in insurance_product.no_insurable_route:
            raise ParameterError('起运地所选省份，本产品不可保')
        if startSiteName_prov and startSiteName_city:
            order.startSiteName = startSiteName_prov + ' '+startSiteName_city
            if startSiteName_dist:
               order.startSiteName = startSiteName_prov + ' '+startSiteName_city +' '+startSiteName_dist
        else:
            raise ParameterError('起运地不能为空')

        #目的地
        targetSiteName_prov = self.get_parameter('targetSiteName_prov').strip()
        targetSiteName_city = self.get_parameter('targetSiteName_city').strip()
        targetSiteName_dist = self.get_parameter('targetSiteName_dist').strip()
        if targetSiteName_prov in insurance_product.no_insurable_route:
            print(insurance_product.no_insurable_route)
            raise ParameterError('目的地所选省份，本产品不可保')
        if targetSiteName_prov and targetSiteName_city:
            order.targetSiteName = targetSiteName_prov + " " + targetSiteName_city
            if targetSiteName_dist:
                order.targetSiteName = targetSiteName_prov + " " + targetSiteName_city+' '+targetSiteName_dist
        else:
            raise ParameterError('目的地不能为空')
        
        if order.targetSiteName ==order.startSiteName:
            raise ParameterError('起运地和目的地不能完全一致')

        # #保险起期
        # expectStartTime = self.get_parameter('expectStartTime').strip()
        # if expectStartTime:
        #     try:
        #         order.expectStartTime = expectStartTime
        #     except Exception:
        #         raise ParameterError("日期格式错误，请填写正确的日期格式")
        # else:
        #     raise ParameterError('保险起期不能为空')
        order.expectStartTime = datetime.now()

        #产品类型
        product_type = self.request.POST.get('product_type', '').strip()
        if ConvertTools.validate_choices(product_type, InsuranceProducts.PRODUCT_TYPE):
            order.product_type = product_type
            if product_type == 'car':
                #保额
                insurance_price = self.get_parameter('insurance_price').strip()
                if insurance_price:
                    try:
                        insurance_price1=float(insurance_price)*100
                        insurance_price2=int(insurance_price1)
                    except:
                       raise ParameterError('请输入数字') 
                else:
                    raise ParameterError('保额不能为空')
                if insurance_price2<0:
                    raise ParameterError('保额不能为负数')
                if insurance_price1>insurance_price2:
                    raise ParameterError('保额最多输入两位小数')
                insurance_price=insurance_price2
                if insurance_price2 > 200000000:
                        raise ParameterError('货物价值上限2000000元')
                elif insurance_price2 <= 100000:
                        insurance_price = 100000
                else:
                        insurance_price = insurance_price2
                order.insurance_price = insurance_price 

                order.commission_ratio = insurance_product.commission_ratio
                car_transport_id = self.get_parameter('car_transport_id').strip()
                if car_transport_id:
                    a=len(car_transport_id)
                    if len(car_transport_id) >20:
                        raise ParameterError('运单号长度过长，不能超过20位')
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
                    try:
                        car_commodityCases=int(car_commodityCases)
                    except:
                        try:
                            car_commodityCases=float(car_commodityCases)
                        except:
                            raise ParameterError('输入的货物数量不为数字')
                    if car_commodityCases>0:
                        order.commodityCases = str(car_commodityCases)
                    else:
                        raise ParameterError('货物数量未大于零')                    
                    #order.commodityCases = car_commodityCases
                else:
                    raise ParameterError('货物数量不能为空')

            elif product_type == 'batch':
#**************************************测试数据
                if order.company.paper_id == settings.ZHONGAN_COMPANY_CODE:
                    #包装类型
                    order.pack_method = '1001'
                    #投保货物类型
                    common_good='CB016-1'
                    if common_good:
                        order_cargo =Cargo.objects(cargo_number=common_good).first()
                        order.cargo = order_cargo
                    else:
                        raise ParameterError('车次保险未选择具体货物')
                    #运单号
                    order.transport_id = "整车"
                    #默认货物名称
                    order.commodityName = '零担货物'
                
                #货物总件数
                batch_commodityCases = self.get_parameter('batch_commodityCases').strip()
                if batch_commodityCases:
                    try:
                        batch_commodityCases1=float(batch_commodityCases)
                        batch_commodityCases2=int(batch_commodityCases)
                        if batch_commodityCases1 !=batch_commodityCases2:
                            raise ParameterError('货物件数请输入整数') 
                        else:
                            order.commodityCases = str(batch_commodityCases2)
                    except:
                       raise ParameterError('货物件数请输入数字') 
                else:
                    raise ParameterError('货物件数不能为空')
                
                
#*********************测试数据结束
                 #保额
                insurance_price = self.get_parameter('batch_insurance_price').strip()
                if insurance_price:
                    try:
                        insurance_price1=float(insurance_price)*100
                        insurance_price2=int(insurance_price1)
                    except:
                       raise ParameterError('请输入数字') 
                else:
                    raise ParameterError('保额不能为空')
                if insurance_price2<0:
                    raise ParameterError('保额不能为负数')
                if insurance_price1>insurance_price2:
                    raise ParameterError('保额最多输入两位小数')
                insurance_price=insurance_price2
                min_price = order.insurance_product.insurance_price_min
                max_price = order.insurance_product.insurance_price_max
                if insurance_price< min_price or insurance_price> max_price:
                        message="货物价值不在所投保产品可保范围内，本产品货物价值范围："+str(min_price/100)+"至"+str(max_price/100)+"元"
                        raise ParameterError(message)
                order.insurance_price = insurance_price 
      
                order_state = self.get_parameter('order_state').strip()
                order.commission_ratio = insurance_product.commission_ratio
                batch_plate_number = self.get_parameter('batch_plate_number').strip()
                short = self.get_parameter('short_number').strip()
                mid = self.get_parameter('mid_number').strip()
                if batch_plate_number:
                    if not short or not mid:
                        raise ParameterError('请选择车牌号前两位。如“黑A')
                    if re.match(r'^[a-z_A-Z_0-9]{5}$', batch_plate_number):
                         batch_plate_number = batch_plate_number.upper()
                         plate_number = short +" "+mid +batch_plate_number
                         order.plate_number = plate_number
                    else:
                        raise ParameterError('您输入的车牌号不正确，请输入由英文或数字组成的五位字符串')
                else:
                    raise ParameterError('车牌号不能为空')

                batch_plate_number_plus = self.get_parameter('batch_plate_number_plus').strip()
                if batch_plate_number_plus:
                    order.plate_number_plus = batch_plate_number_plus

                # 车次清单文档
                batch_file = self.request.FILES.get('batch_file')
                old_file=''
                if batch_file:
                    if order_state =="edit":
                        old_file = order.batch_url
                    document_tools = DocumentTools()
                    order.batch_url = document_tools.save(request_file=batch_file, file_folder=DocumentFolderType.batch, old_file=old_file )

                #车次清单图片
                batch_image_list = self.request.FILES.getlist('batch_image_list', '')
                if batch_image_list:
                    if order_state =="edit":
                        order.batch_image_list = []
                    image_tool = ImageTools()
                    for batch_image in batch_image_list:
                        batch_image_url = image_tool.save(request_file=batch_image, file_folder=ImageFolderType.batch, old_file='')
                        if batch_image_url:
                            order.batch_image_list.append(batch_image_url)
                        else:
                            raise ParameterError('保存清单图片失败')
                        

                #车次清单list

                position_list = self.request.POST.getlist('position')
                if len(position_list) > 0:
                    if order_state =="edit":
                        order.batch_list =[]
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
                                    hwsl=int(hwsl)
                                except:
                                    try:
                                        hwsl=float(hwsl)
                                    except:
                                        raise ParameterError('输入的货物数量不为数字')
                                if hwsl>0:
                                    batches.commodityCases = str(hwsl)
                                else:
                                    raise ParameterError('货物数量未大于零')
#                                 try:
#                                     hwsl = int(hwsl)
#                                     batches.commodityCases = hwsl
#                                 except Exception:
#                                     raise ParameterError('请输入正数字')
                            else:
                                raise ParameterError('货物数量不能为空')
                            order.batch_list.append(batches)
                        except ParameterError as e:
                            raise e
                        except Exception as e:
                            pass

#                 if not position_list and not batch_image_list and not batch_file:
#                     raise ParameterError("保险清单内容，三选一")
                if not order.batch_list and not order.batch_image_list and not order.batch_url:
                    raise ParameterError("保险清单内容，三选一")
                


            elif product_type == 'ticket':
                #包装类型
                pack_detail = self.get_parameter('pack_detail_id').strip()
                if pack_detail:
                    order.pack_method = pack_detail
                else:
                    raise ParameterError('包装类型不能为空')
                
                #投保货物类型
                good_type=self.get_parameter("good_type_id").strip()
                if good_type:
                    order.good_type = good_type
                    common_good=self.get_parameter("common_good_id").strip()
                    if common_good:
#                         order.common_good_detail = common_good
                        order_cargo =Cargo.objects(id=common_good).first()
                        order.cargo = order_cargo
                    else:
                        raise ParameterError('单票保险未选择具体货物')
                
                else:
                    raise ParameterError('投保货物类型未填写')
                
                
                #保额
                insurance_price = self.get_parameter('insurance_price').strip()
                if insurance_price:
                    try:
                        insurance_price1=float(insurance_price)*100
                        insurance_price2=int(insurance_price1)
                    except:
                       raise ParameterError('请输入数字') 
                else:
                    raise ParameterError('保额不能为空')
                if insurance_price2<0:
                    raise ParameterError('保额不能为负数')
                if insurance_price1>insurance_price2:
                    raise ParameterError('保额最多输入两位小数')
                insurance_price=insurance_price2
                min_price = order.insurance_product.insurance_price_min
                max_price = order.insurance_product.insurance_price_max
                if insurance_price< min_price or insurance_price> max_price:
                        message="货物价值不在所投保产品可保范围内，本产品货物价值范围："+str(min_price/100)+"至"+str(max_price/100)+"元"
                        raise ParameterError(message)
                order.insurance_price = insurance_price 
                    
                
                ticket_transport_id = self.get_parameter('ticket_transport_id').strip()
                if ticket_transport_id:
                    if len(ticket_transport_id)>20:
                        raise ParameterError('运单号不能最多输入20个字符')
                    if re.match(r'^[a-z_A-Z_0-9_\u4e00-\u9fa5]+$', ticket_transport_id):
                        order.transport_id = ticket_transport_id
                    else:
                         raise ParameterError('运单号不能输入特殊字符')

                ticket_plate_number = self.get_parameter('ticket_plate_number').strip()
                ticket_short_number = self.get_parameter('ticket_short_number').strip()
                ticker_mid_number = self.get_parameter('ticker_mid_number').strip()
                
                if ticket_plate_number:
                    if not ticket_short_number or not ticker_mid_number:
                        raise ParameterError('请选择车牌号前两位。如“黑A')
                    if re.match(r'^[a-z_A-Z_0-9]{5}$', ticket_plate_number):
                         ticket_plate_number = ticket_plate_number.upper()
                         plate_number = ticket_short_number +" "+ticker_mid_number +ticket_plate_number
                         order.plate_number = plate_number
                    else:
                        raise ParameterError('您输入的车牌号不正确，请输入由英文或数字组成的五位字符串')
#                 else:
#                     raise ParameterError('车牌号不能为空')
#                 if ticket_plate_number:
#                     if len(ticket_plate_number) <= 10:
#                         order.plate_number = ticket_plate_number
#                     else:
#                         raise ParameterError('您输入的车牌号不正确')

                if not ticket_transport_id and not ticket_plate_number:
                    raise ParameterError('车牌号和运单号至少填写一个')

                ticket_plate_number_plus = self.get_parameter('ticket_plate_number_plus').strip()
                if ticket_plate_number_plus:
                    order.plate_number_plus = ticket_plate_number_plus

                ticket_commodityName = self.get_parameter('ticket_commodityName').strip()
                if ticket_commodityName:
                    order.commodityName = ticket_commodityName
                else:
                    raise ParameterError('货物名称不能为空')

                ticket_commodityCases = self.get_parameter('ticket_commodityCases').strip()
                if ticket_commodityCases:
                    try:
                        ticket_commodityCases=int(ticket_commodityCases)
                    except:
                        try:
                            ticket_commodityCases=float(ticket_commodityCases)
                        except:
                            raise ParameterError('输入的货物数量不为数字')
                    if ticket_commodityCases>0:
                        order.commodityCases = str(ticket_commodityCases)
                    else:
                        raise ParameterError('货物数量未大于零')
                    
                else:
                    raise ParameterError('货物数量不能为空')

        else:
            raise ParameterError('非法的产品类型')
        #2017/12/01添加众安部分
        test_product_name = order.insurance_product.company.parent.description
        if "众安"  in order.insurance_product.company.parent.description:
            product_type = str(order.product_type)
            #单票保险验证资料
            if product_type == "ticket":
                tb_client_type = self.get_parameter("tb_client_type_ticket", "")#单票保险用户身份
                holderCertNo = self.get_parameter("holderCertNo_ticket", "")#单票保险投保人证件号
                taxpayerRegNum = self.get_parameter("taxpayerRegNum_ticket", "")#单票保险纳税人识别号 
            elif  product_type == "batch":
                tb_client_type = self.get_parameter("tb_client_type", "")#单票保险用户身份
                holderCertNo = self.get_parameter("holderCertNo", "")#单票保险投保人证件号
                taxpayerRegNum = self.get_parameter("taxpayerRegNum", "")#单票保险纳税人识别号 
            #车次保险验证资料
            tb_holderCertType = self.get_parameter("tb_holderCertType", "")#投保人证件类型
            bb_insureCertType = self.get_parameter("bb_insureCertType", "")#被保人证件类型
            bb_insureCertNo = self.get_parameter("bb_insureCertNo", "")#被保人证件号
            
            if product_type == "ticket":
                if not tb_client_type:
                    raise ParameterError('请选择投保人身份')
                if tb_client_type == "company":
                    order.tb_client_type = "company"
                    if not taxpayerRegNum:
                        raise ParameterError('请填写纳税人识别号 ')
                    else:
                        if len(holderCertNo) > 20 :
                            raise ParameterError('填写的纳税人识别号号码过长 ')
                        order.taxpayerRegNum =str(taxpayerRegNum)
                elif tb_client_type == "person":
                    order.tb_client_type = "person"
                    if not holderCertNo:
                        raise ParameterError('请填写投保人身份证号 ')
                    else:
                        if len(holderCertNo) != 18 :
                            raise ParameterError('请输入正确投保人身份证号 ')
                        order.holderCertNo =str(holderCertNo)
                else:
                    raise ParameterError('请选择投保人身份 ')
            #车次保险验证
            elif product_type == "batch":
                trailerNo = self.get_parameter("batch_plate_number_plus", "")#挂车牌号
                if not tb_client_type:
                    raise ParameterError('请选择投保人身份')
                if not taxpayerRegNum:
                    raise ParameterError('请填写纳税人识别号')
                if not tb_holderCertType:
                    raise ParameterError('请选择投保人证件类型')
                if not holderCertNo:
                    raise ParameterError('请填写投保人证件号')
                if not bb_insureCertType:
                    raise ParameterError('请选择证件类型')
                if not bb_insureCertNo:
                    raise ParameterError('请填写被保人证件号')
                if not trailerNo:
                    raise ParameterError('请填写挂车牌号')
                #投保人身份
                if tb_client_type == "company":
                    order.tb_client_type = "company"
                elif tb_client_type == "person":
                    order.tb_client_type = "person"
                else:
                    raise ParameterError('请选择投保人身份状态不正确,请退出当前页面重新进入')
                #投保人纳税人识别号
                if len(holderCertNo) > 20 :
                    raise ParameterError('填写的纳税人识别号号码过长 ')
                order.taxpayerRegNum =str(taxpayerRegNum)
                
                #投保人证件类型
                if tb_holderCertType == "TY":
                    order.tb_holderCertType = "TY"
                elif tb_holderCertType == "Z":
                    order.tb_holderCertType = "Z"
                else:
                    raise ParameterError('投保人证件类型状态不正确,请退出当前页面重新进入')
                
                #投保人证件号
                if order.tb_holderCertType == "TY":
                    if len(holderCertNo) != 18:
                        raise ParameterError('投保人统一信用代码长度应为18位')
                    order.holderCertNo = str(holderCertNo)
                if order.tb_holderCertType == "Z":
                    if len(holderCertNo) != 9:
                        raise ParameterError('投保人组织机构代码长度应为9位')
                    order.holderCertNo = str(holderCertNo)
                    
                #被报人证件类型
                if bb_insureCertType == "TY":
                    order.bb_insureCertType = "TY"
                elif bb_insureCertType == "Z":
                    order.bb_insureCertType = "Z"
                else:
                    raise ParameterError('投保人证件类型状态不正确,请退出当前页面重新进入')
                
                #被投保人证件号
                if order.bb_insureCertType == "TY":
                    if len(bb_insureCertNo) != 18:
                        raise ParameterError('被保人统一信用代码长度应为18位')
                    order.bb_insureCertNo = str(bb_insureCertNo)
                if order.bb_insureCertType == "Z":
                    if len(bb_insureCertNo) != 9:
                        raise ParameterError('被保人组织机构代码长度应为9位')
                    order.bb_insureCertNo = str(bb_insureCertNo)
                
                #挂车牌号
                if len(trailerNo)<5 or len(trailerNo)>10:
                    raise ParameterError('挂车牌号长度不正确,应为5-10个字符')
                elif "挂" not in str(trailerNo):
                    raise ParameterError('挂车牌号应包含挂字')
                else:
                    order.plate_number_plus = str(trailerNo)
        return order
    
    #编辑订单图片
    def validation_edit_pic(self, order):
        insurance_image = self.request.FILES.get('insurance_image_edit', '')
        old_url = self.request.POST.get('image_url_edit')
        position = -1
        for i in range(len(order.insurance_image_list)):
            if str(order.insurance_image_list[i]) == old_url:
                position = i
                break
        if position < 0:
            raise ParameterError('要修改图片不存在')
        if insurance_image:
            image_tool = ImageTools()
            insurance_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file=old_url)
            if insurance_image_url:
                order.insurance_image_list[position] = insurance_image_url
            else:
                raise ParameterError('生成图片地址失败')
        else:
            raise ParameterError('未选择图片，请选择图片')
        return order

       #编辑车次图片
    def validation_edit_batch_pic(self, order):
        batch_image = self.request.FILES.get('batch_image_edit', '')
        old_url = self.request.POST.get('image_url_batch_edit')
        position = -1
        for i in range(len(order.batch_image_list)):
            if str(order.batch_image_list[i]) == old_url:
                position = i
                break
        if position < 0:
            raise ParameterError('要修改图片不存在')
        if batch_image:
            image_tool = ImageTools()
            batch_image_url = image_tool.save(request_file=batch_image, file_folder=ImageFolderType.batch, old_file=old_url)
            if batch_image_url:
                order.batch_image_list[position] = batch_image_url
            else:
                raise ParameterError('生成图片地址失败')
        else:
            raise ParameterError('未选择图片，请选择图片')
        return order
    

    # 车次清单
    def validation_batch_list(self, order, request):
        position_list = request.POST.getlist('position')
        if len(position_list) > 0:
            for position in position_list:
                try:
                    yd = request.POST.get("yd_" + position)
                    qyd = request.POST.get("qyd_" + position)
                    mdd = request.POST.get("mdd_" + position)
                    hwmc = request.POST.get("hwmc_" + position)
                    hwsl = request.POST.get("hwsl_" + position)
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
                            batches.commodityCases = hwsl
                        except Exception:
                            raise ParameterError('请输入正数字')
                    else:
                        raise ParameterError('货物数量不能为空')
                    order.batch_list.append(batches)
                except ParameterError as e:
                    raise e
                except Exception as e:
                    pass
        return order

        # 编辑车次清单
    def validation_batch_edit(self, order, request):
        yd_old = request.POST.get("batch_list_edit_id")
        yd = request.POST.get("modal_yd")
        qyd = request.POST.get("modal_qyd")
        mdd = request.POST.get("modal_mdd")
        hwmc = request.POST.get("modal_hwmc")
        hwsl = request.POST.get("modal_hwsl")

        for batch in order.batch_list:
            if batch.transport_id == yd_old:
                if yd:
                    batch.transport_id = yd
                else:
                    raise ParameterError('运单不能为空')
                if qyd:
                    batch.startSiteName = qyd
                else:
                    raise ParameterError('起运地不能为空')
                if mdd:
                    batch.targetSiteName = mdd
                else:
                    raise ParameterError('目的地不能为空')
                if hwmc:
                    batch.commodityName = hwmc
                else:
                    raise ParameterError('货物名称不能为空')
                if hwsl:
                    try:
                        hwsl = int(hwsl)
                        batch.commodityCases = hwsl
                    except Exception:
                        raise ParameterError('请输入正数字')
                else:
                    raise ParameterError('货物数量不能为空')
        return order

    #   验证保单号
    # def validation_insurance_id(self, order):
    #     insurance_id = self.get_parameter("insurance_id").strip()
    #     if insurance_id:
    #         order.insurance_id = insurance_id
    #     insurance_image_list = self.request.FILES.getlist('add_insurance_image_pic', '')
    #
    #     image_tool = ImageTools()
    #     temp = []
    #     if insurance_image_list:
    #         for insurance_image in insurance_image_list:
    #             batch_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
    #             if not batch_image_url:
    #                 request_tool.set_message(order.paper_id+'生成图片地址失败')
    #                 return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]) + get_parameter)
    #             else:
    #                 temp.append(batch_image_url)
    #     else:
    #         request_tool.set_message('导入失败，请填入保单图片')
    #         return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]) + get_parameter)
    #
    #     return order



    #   验证认证
    def validation_certificate(self, certificate):
        # name = self.get_parameter("name").strip()
        # if name:
        #     certificate.name = name
        # else:
        #     raise ParameterError('姓名不能为空')

        national_image = self.request.FILES.get('national_image', '')
        if national_image:
            image_tool = ImageTools()
            national_image_url = image_tool.save(request_file=national_image, file_folder=ImageFolderType.user, old_file='')
            if national_image_url:
                certificate.national_image = national_image_url
            else:
                raise ParameterError('保存身份证正面图片失败')
        else:
            raise ParameterError('请选择添加身份证正面图片')

        national_image_down = self.request.FILES.get('national_image_down', '')
        if national_image_down:
            image_tool = ImageTools()
            national_image_down_url = image_tool.save(request_file=national_image_down, file_folder=ImageFolderType.user, old_file='')
            if national_image_down_url:
                certificate.national_image_down = national_image_down_url
            else:
                raise ParameterError('保存身份证背面图片失败')
        else:
            raise ParameterError('请选择添加身份证背面图片')

        user_type = self.get_parameter("user_type").strip()
        if user_type:
            certificate.user_type = user_type
        else:
            raise ParameterError('认证目标不能为空')

        user_classify = self.get_parameter("user_classify").strip()
        if user_classify:
            certificate.user_classify = user_classify

        if user_type == 'transport':
            business_license_image = self.request.FILES.get('business_license_image', '')
            if business_license_image:
                image_tool = ImageTools()
                business_license_image_url = image_tool.save(request_file=business_license_image, file_folder=ImageFolderType.user, old_file='')
                if business_license_image_url:
                    certificate.business_license_image = business_license_image_url
                else:
                    raise ParameterError('保存营业执照正本图片失败')
            else:
                raise ParameterError('请选择添加营业执照正本图片')

            organ_image = self.request.FILES.get('organ_image', '')
            if organ_image:
                image_tool = ImageTools()
                organ_image_url = image_tool.save(request_file=organ_image, file_folder=ImageFolderType.user, old_file='')
                if organ_image_url:
                    certificate.organ_image = organ_image_url
                else:
                    raise ParameterError('保存组织机构代码证失败')
            # else:
            #     raise ParameterError('请选择添加组织机构代码证')
            #根据杨帆3.30删掉税务登记证
            # tax_image = self.request.FILES.get('tax_image', '')
            # if tax_image:
            #     image_tool = ImageTools()
            #     tax_image_url = image_tool.save(request_file=tax_image, file_folder=ImageFolderType.user, old_file='')
            #     if tax_image_url:
            #         certificate.tax_image = tax_image_url
            #     else:
            #         raise ParameterError('保存税务登记证失败')
            # else:
            #     raise ParameterError('请选择添加税务登记证')

            operating_permit_image = self.request.FILES.get('operating_permit_image', '')
            if operating_permit_image:
                image_tool = ImageTools()
                operating_permit_image_url = image_tool.save(request_file=operating_permit_image, file_folder=ImageFolderType.user, old_file='')
                if operating_permit_image_url:
                    certificate.operating_permit_image = operating_permit_image_url
                else:
                    raise ParameterError('保存道路运输经营许可证失败')
            else:
                raise ParameterError('请选择添加道路运输经营许可证')

        elif user_type == 'driver':
            driver_image = self.request.FILES.get('driver_image', '')
            if driver_image:
                image_tool = ImageTools()
                driver_image_url = image_tool.save(request_file=driver_image, file_folder=ImageFolderType.user, old_file='')
                if driver_image_url:
                    certificate.driver_image = driver_image_url
                else:
                    raise ParameterError('保存驾驶证失败')
            else:
                raise ParameterError('请选择添加驾驶证')

            plate_image = self.request.FILES.get('plate_image', '')
            if plate_image:
                image_tool = ImageTools()
                plate_image_url = image_tool.save(request_file=plate_image, file_folder=ImageFolderType.user, old_file='')
                if plate_image_url:
                    certificate.plate_image = plate_image_url
                else:
                    raise ParameterError('保存行驶证失败')
            else:
                raise ParameterError('请选择添加行驶证')

            transportation_image = self.request.FILES.get('transportation_image', '')
            if transportation_image:
                image_tool = ImageTools()
                transportation_image_url = image_tool.save(request_file=transportation_image, file_folder=ImageFolderType.user, old_file='')
                if transportation_image_url:
                    certificate.transportation_image = transportation_image_url
                else:
                    raise ParameterError('保存营运证失败')
            else:
                raise ParameterError('请选择添加营运证')
        elif user_type == 'boss':
            if user_classify == 'units':
                business_license_image_boss = self.request.FILES.get('business_license_image_boss', '')
                if business_license_image_boss:
                    image_tool = ImageTools()
                    business_license_image_boss_url = image_tool.save(request_file=business_license_image_boss, file_folder=ImageFolderType.user, old_file='')
                    if business_license_image_boss_url:
                        certificate.business_license_image = business_license_image_boss_url
                    else:
                        raise ParameterError('保存营业执照图片失败')
                else:
                    raise ParameterError('请选择添加营业执照图片')

                organ_image = self.request.FILES.get('organ_image_boss', '')
                if organ_image:
                    image_tool = ImageTools()
                    organ_image_url = image_tool.save(request_file=organ_image, file_folder=ImageFolderType.user, old_file='')
                    if organ_image_url:
                        certificate.organ_image = organ_image_url
                    else:
                        raise ParameterError('保存组织机构代码证失败')
        elif user_type == 'owner':
            print("申请车主认证")
        else:
            raise ParameterError('认证类型不正确')
        return certificate

   #   重新认证
    def validation_certificate_repeat(self, certificate):
        if not certificate.national_id:
            national_image = self.request.FILES.get('national_image', '')
            if national_image:
                image_tool = ImageTools()
                national_image_url = image_tool.save(request_file=national_image, file_folder=ImageFolderType.user, old_file='')
                if national_image_url:
                    certificate.national_image = national_image_url
                else:
                    raise ParameterError('保存身份证正面图片失败')
            else:
                raise ParameterError('请选择添加身份证正面图片')

            national_image_down = self.request.FILES.get('national_image_down', '')
            if national_image_down:
                image_tool = ImageTools()
                national_image_down_url = image_tool.save(request_file=national_image_down, file_folder=ImageFolderType.user, old_file='')
                if national_image_down_url:
                    certificate.national_image_down = national_image_down_url
                else:
                    raise ParameterError('保存身份证背面图片失败')
            else:
                raise ParameterError('请选择添加身份证背面图片')

        user_type = self.get_parameter("user_type").strip()
        if user_type:
            certificate.user_type = user_type
        else:
            raise ParameterError('认证目标不能为空')

        user_classify = self.get_parameter("user_classify").strip()
        if user_classify:
            certificate.user_classify = user_classify

        if user_type == 'transport':
            if not certificate.business_license_id:
                business_license_image = self.request.FILES.get('business_license_image', '')
                if business_license_image:
                    image_tool = ImageTools()
                    business_license_image_url = image_tool.save(request_file=business_license_image, file_folder=ImageFolderType.user, old_file='')
                    if business_license_image_url:
                        certificate.business_license_image = business_license_image_url
                    else:
                        raise ParameterError('保存营业执照正本图片失败')
                else:
                    raise ParameterError('请选择添加营业执照正本图片')
            if not certificate.organ:
                organ_image = self.request.FILES.get('organ_image', '')
                if organ_image:
                    image_tool = ImageTools()
                    organ_image_url = image_tool.save(request_file=organ_image, file_folder=ImageFolderType.user, old_file='')
                    if organ_image_url:
                        certificate.organ_image = organ_image_url
                    else:
                        raise ParameterError('保存组织机构代码证失败')
                # else:
                #     raise ParameterError('请选择添加组织机构代码证')
            # if not certificate.tax_id:
            #     tax_image = self.request.FILES.get('tax_image', '')
            #     if tax_image:
            #         image_tool = ImageTools()
            #         tax_image_url = image_tool.save(request_file=tax_image, file_folder=ImageFolderType.user, old_file='')
            #         if tax_image_url:
            #             certificate.tax_image = tax_image_url
            #         else:
            #             raise ParameterError('保存税务登记证失败')
                # else:
                #     raise ParameterError('请选择添加税务登记证')
            if not certificate.operating_permit_id:
                operating_permit_image = self.request.FILES.get('operating_permit_image', '')
                if operating_permit_image:
                    image_tool = ImageTools()
                    operating_permit_image_url = image_tool.save(request_file=operating_permit_image, file_folder=ImageFolderType.user, old_file='')
                    if operating_permit_image_url:
                        certificate.operating_permit_image = operating_permit_image_url
                    else:
                        raise ParameterError('保存道路运输经营许可证失败')
                else:
                    raise ParameterError('请选择添加道路运输经营许可证')

        elif user_type == 'driver':
            if not certificate.driver_id:
                driver_image = self.request.FILES.get('driver_image', '')
                if driver_image:
                    image_tool = ImageTools()
                    driver_image_url = image_tool.save(request_file=driver_image, file_folder=ImageFolderType.user, old_file='')
                    if driver_image_url:
                        certificate.driver_image = driver_image_url
                    else:
                        raise ParameterError('保存驾驶证失败')
                else:
                    raise ParameterError('请选择添加驾驶证')
            if not certificate.plate_number:
                plate_image = self.request.FILES.get('plate_image', '')
                if plate_image:
                    image_tool = ImageTools()
                    plate_image_url = image_tool.save(request_file=plate_image, file_folder=ImageFolderType.user, old_file='')
                    if plate_image_url:
                        certificate.plate_image = plate_image_url
                    else:
                        raise ParameterError('保存行驶证失败')
                else:
                    raise ParameterError('请选择添加行驶证')
            if not certificate.transportation_license_id:
                transportation_image = self.request.FILES.get('transportation_image', '')
                if transportation_image:
                    image_tool = ImageTools()
                    transportation_image_url = image_tool.save(request_file=transportation_image, file_folder=ImageFolderType.user, old_file='')
                    if transportation_image_url:
                        certificate.transportation_image = transportation_image_url
                    else:
                        raise ParameterError('保存营运证失败')
                else:
                    raise ParameterError('请选择添加营运证')
        elif user_type == 'boss':
            if user_classify == 'units':
                if not certificate.business_license_id:
                    business_license_image_boss = self.request.FILES.get('business_license_image_boss', '')
                    if business_license_image_boss:
                        image_tool = ImageTools()
                        business_license_image_boss_url = image_tool.save(request_file=business_license_image_boss, file_folder=ImageFolderType.user, old_file='')
                        if business_license_image_boss_url:
                            certificate.business_license_image = business_license_image_boss_url
                        else:
                            raise ParameterError('保存营业执照图片失败')
                    else:
                        raise ParameterError('请选择添加营业执照图片')

                organ_image = self.request.FILES.get('organ_image_boss', '')
                if organ_image:
                    image_tool = ImageTools()
                    organ_image_url = image_tool.save(request_file=organ_image, file_folder=ImageFolderType.user, old_file='')
                    if organ_image_url:
                        certificate.organ_image = organ_image_url
                    else:
                        raise ParameterError('保存组织机构代码证失败')
        else:
            raise ParameterError('认证类型不正确')
        return certificate

#   验证优惠券
    def validation_coupon(self, coupon):
        name = self.get_parameter("name").strip()
        if name:
            coupon.name = name
        else:
            raise ParameterError('姓名不能为空')

        describe = self.get_parameter("describe").strip()
        if describe:
            coupon.describe = describe

        # 产品
        product_id = self.get_parameter('product_id').strip()
        if product_id:
            insurance_product = InsuranceProducts.objects(id=product_id).first()
            if insurance_product:
                coupon.product = insurance_product
            else:
                raise ParameterError('产品不存在')
        else:
            raise ParameterError('产品不能为空')

        end_date = self.get_parameter("end_date").strip()
        now = datetime.now()
        otherStyleTime = now.strftime("%Y-%m-%d ")
        if end_date:
            if end_date< otherStyleTime:
                raise ParameterError('截至日期早于当前日期')
            coupon.end_date = end_date
        else:
            raise ParameterError('截至日期不能为空')

        # max_count = self.get_parameter("max_count").strip()
        # try:
        #     if max_count:
        #         max_count = int(max_count)
        #         coupon.max_count = max_count
        # except Exception:
        #     raise ParameterError("数据类型错误，请填写整数")
        #
        # min_price = self.get_parameter("min_price").strip()
        # try:
        #     if min_price:
        #         min_price = int(min_price)
        #         coupon.min_price = min_price
        # except Exception:
        #     raise ParameterError("数据类型错误，请填写整数")
        #
        # max_price = self.get_parameter("max_price").strip()
        # try:
        #     if max_count:
        #         max_price = int(max_price)
        #         coupon.max_price = max_price
        # except Exception:
        #     raise ParameterError("数据类型错误，请填写整数")

        rate = self.get_parameter("rate").strip()
        try:
            if rate:
                rate = float(rate)
                coupon.rate = rate
        except Exception:
            raise ParameterError("数据类型错误，请填写整数")
        return coupon





#   验证公众号的物流公司
    def validation_logistics(self, logistics):
        company_name = self.get_parameter("company_name").strip()
        if company_name:
            logistics.company_name = company_name
        else:
            raise ParameterError('公司名称不能为空')

        #公司图片
        logistics_image_list = self.request.FILES.getlist('logistics_image_list', '')
        if logistics_image_list:
            image_tool = ImageTools()
            for logistics_image in logistics_image_list:
                logistics_image_url = image_tool.save(request_file=logistics_image, file_folder=ImageFolderType.logistics, old_file='')
                if logistics_image_url:
                    logistics.logistics_image_list.append(logistics_image_url)
                else:
                    raise ParameterError('保存公司图片失败')

        special_line_list = self.get_parameter("special_line_list").strip()
        if special_line_list:
            special_line_list = special_line_list.split('-')
            logistics.special_line_list = special_line_list
        else:
            raise ParameterError('运输专线不能为空')

        person = self.get_parameter("person").strip()
        if person:
            logistics.person = person

        person1 = self.get_parameter("person1").strip()
        if person1:
            logistics.person1 = person1

        phone = self.get_parameter("phone").strip()
        if phone:
            logistics.phone = phone

        phone1 = self.get_parameter("phone1").strip()
        if phone1:
            logistics.phone1 = phone1

        phone2 = self.get_parameter("phone2").strip()
        if phone2:
            logistics.phone2 = phone2

        description = self.get_parameter("content").strip()
        if description:
            logistics.description = description

        priority = self.request.POST.get('priority', '').strip()
        if priority:
            try:
                priority = int(priority)
                if priority < 0:
                    raise ParameterError("优先级不能是负数")
            except ValueError:
                raise ParameterError("优先级不是有效的非负整数")
            logistics.priority = priority
        else:
           raise ParameterError("优先级不能为空，请输入非负整数") 

        return logistics



#   验证公众号的律师
    def validation_campaign_lawyer(self, campaign_lawyer):
        name = self.get_parameter("name").strip()
        if name:
            if len(name)>20:
                raise ParameterError('姓名长度不能超过20个字符')
            campaign_lawyer.name = name
        else:
            raise ParameterError('姓名不能为空')

        #个人头像
        icon = self.request.FILES.get('icon', '')
        edit_hidden = self.get_parameter("edit_hidden").strip()
        if icon:
            image_tool = ImageTools()
            if edit_hidden:
                old_icon = campaign_lawyer.icon
                icon_url = image_tool.save(request_file=icon, file_folder=ImageFolderType.lawyer, old_file=old_icon)
                if icon_url:
                    campaign_lawyer.icon = icon_url
                else:
                    raise ParameterError('保存个人头像失败')

            else:
                icon_url = image_tool.save(request_file=icon, file_folder=ImageFolderType.lawyer, old_file='')
                if icon_url:
                    campaign_lawyer.icon = icon_url
                else:
                    raise ParameterError('保存个人头像失败')

        phone = self.get_parameter("phone").strip()
        if phone:
            if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', phone):
                raise ParameterError( '请输入正确的手机号码')
            campaign_lawyer.phone = phone

        phone1 = self.get_parameter("phone1").strip()
        if phone1:
            if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', phone1):
                raise ParameterError( '请核对手机号码')
            campaign_lawyer.phone1 = phone1

        address = self.get_parameter("address").strip()
        if address:
            campaign_lawyer.address = address

        qualified = self.get_parameter("qualified").strip()
        if qualified:
            campaign_lawyer.qualified = qualified
        else:
            raise ParameterError('律师资格证书不能为空')

        practice = self.get_parameter("practice").strip()
        if practice:
            try:
                count= CampaignLawyer.objects(practice=practice).count()
            except:
                count=0
            if count>1:
               raise ParameterError('律师执业证号已存在')
            if count ==1:
                test_lawyer = CampaignLawyer.objects(practice=practice).first()
                if test_lawyer.id != campaign_lawyer.id:
                    raise ParameterError('律师执业证号已存在，请检查后重新输入。或联系管理员确定证件真实性。')
                else:
                    campaign_lawyer.practice = practice
            if count ==0:
                 campaign_lawyer.practice = practice
        else:
            raise ParameterError('律师执业证号不能为空')

        description = self.get_parameter("content").strip()
        if description:
            description=description.replace("\r\n"," ")
            campaign_lawyer.description = description

        priority = self.request.POST.get('priority', '').strip()
        if priority:
            try:
                priority = int(priority)
                if priority < 0:
                    raise ParameterError("优先级不能是负数")
            except ValueError:
                raise ParameterError("优先级不是有效的非负整数")
            campaign_lawyer.priority = priority

        return campaign_lawyer

   #验证司机
    def validation_campaign_truckers(self, truckers):
        name = self.get_parameter("user_name").strip()
        if name:
            truckers.user_name = name
        else:
            raise ParameterError('姓名不能为空')
        
        user_phone = self.get_parameter("user_phone").strip()
        if user_phone:
                truckers.user_phone = user_phone
        else:
            raise ParameterError('联系电话不能为空')
        
        user_age = self.get_parameter("user_age").strip()
        if user_age and user_age.isdigit() :
            truckers.user_age = user_age
        else:
            raise ParameterError('年龄不能为空，且只能是数字')
        #车辆图片
        icon = self.request.FILES.get('user_icon', '')
        edit_hidden = self.get_parameter("edit_hidden").strip()
        image_tool = ImageTools()
        if edit_hidden:
            old_icon = truckers.user_image
            if icon:
                icon_url = image_tool.save(request_file=icon, file_folder=ImageFolderType.driver, old_file=old_icon)
                if icon_url:
                    truckers.user_image = icon_url
                else:
                    raise ParameterError('保存车辆图片失败')

        else:
            if icon:
                icon_url = image_tool.save(request_file=icon, file_folder=ImageFolderType.driver, old_file='')
                if icon_url:
                     truckers.user_image = icon_url
                else:
                    raise ParameterError('保存车辆图片失败')
            else:
                raise ParameterError('未上传车辆图片')
        #行驶证图片
        plate_image_list = self.request.FILES.getlist('plate_image', '')
        if plate_image_list:
            if edit_hidden:
                a=[]
                truckers.plate_image_list=a
                
            for plate_image in plate_image_list:
                image_tool = ImageTools()
                plate_image_url = image_tool.save(request_file=plate_image, file_folder=ImageFolderType.driver, old_file='')
                if plate_image_url:
                    try:
                        truckers.plate_image_list.append(plate_image_url)
                    except:
                        raise ParameterError("保存行驶证图片失败")
                else:
                    raise ParameterError("生成行驶证图片链接失败")
        #保单图片
        insurance_image_list = self.request.FILES.getlist('insurance_image', '')
        if insurance_image_list:
            if edit_hidden:
                b=[]
                truckers.insurance_image_list=b
            for insurance_image in insurance_image_list:
                image_tool = ImageTools()
                insurance_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.driver, old_file='')
                if insurance_image_url:
                    try:
                        truckers.insurance_image_list.append(insurance_image_url)
                    except:
                        raise ParameterError("保存保单图片失败")
                else:
                    raise ParameterError("生成保单图片链接失败")
        #车辆类型
        car_type = self.get_parameter("car_type").strip()
        if car_type:
            truckers.car_type = car_type
        else:
            raise ParameterError('车辆类型不能为空')
            
        if  int(car_type) == 5:  #车辆类型为其他时，必须填写
            car_type_other = self.get_parameter("car_type_other").strip()
            if car_type_other:
                truckers.car_type_other = car_type_other
            else:
                raise ParameterError('车辆类型选择其他时必须填写，不能为空')
            
        car_length = self.get_parameter("car_length").strip()        
        if car_length:
            truckers.car_length = car_length
        else:
            raise ParameterError('车长不能为空')
            
        if  int(car_length) == 19:#车长选择其他时必须填写
            car_length_other = self.get_parameter("car_length_other").strip()
            if car_length_other:
                truckers.car_length_other = car_length_other
            else:
                raise ParameterError('车长选择其他时必须填写，不能为空')

        car_num_head = self.get_parameter("car_num_head").strip()
        if car_num_head:
            truckers.car_num_head = car_num_head
        else:
            raise ParameterError('车牌号(头)不能为空，如果没有，请填无')

        car_num_foot = self.get_parameter("car_num_foot").strip()
        if car_num_foot:
            truckers.car_num_foot = car_num_foot
        else:
            raise ParameterError('车牌号(挂)不能为空，如果没有，请填无')
        
        car_init_date = self.get_parameter("car_init_date").strip()
        if car_init_date:
            truckers.car_init_date = car_init_date
        else:
            raise ParameterError('初始登记日期不能为空')
        
        car_ton = self.get_parameter("car_ton").strip()
        if car_ton:
            truckers.car_ton = car_ton
        else:
            raise ParameterError('吨位不能为空')
        if truckers.special_line_list:
            truckers.special_line_list = []
        special_line = self.get_parameter("special_line_list").strip()
        if special_line:
            special_line_list = special_line.split(' ')
            for special_line in special_line_list:
                k,v= special_line.split('-')
                roadList=RoadList()
                roadList.start_line = k
                roadList.end_line = v
                truckers.special_line_list.append(roadList)
        else:
            raise ParameterError('常走线路不能为空')
        
        description = self.get_parameter("content").strip()
        if description:
            truckers.description = description

        priority = self.request.POST.get('priority', '').strip()
        if priority:
            try:
                priority = int(priority)
                if priority < 0:
                    raise ParameterError("优先级不能是负数")
            except ValueError:
                raise ParameterError("优先级不是有效的非负整数")
            truckers.priority = priority

        return truckers

#   验证车辆
    def validation_create_car(self, create_car):
        profile_phone= self.get_parameter("profile_phone").strip()#用户电话
        plate_number= self.get_parameter("plate_number").strip()#车牌号
        start_date= self.get_parameter("start_date").strip()# 选择起保年份
        plate_expiration_periods= self.get_parameter("plate_expiration_periods").strip()# 行驶证校验有效期
        plate_image_left = self.request.FILES.get('id_plate_image_left', '')     #行驶证正页
        plate_image_right = self.request.FILES.get('id_plate_image_right', '')    #行驶证附页
        commercial_image = self.request.FILES.get('id_commercial_image', '')    #商业险
        liability_image = self.request.FILES.get('id_liability_image', '')     #交强险
        client = Client.objects(profile__phone=profile_phone).first()
        now = datetime.now()
        otherStyleTime = now.strftime("%Y-%m-%d ")
        if client:
            certificate = Certificate.objects(client=client,state='success').first()
            if certificate:
                create_car.client=client
            else:
                raise ParameterError('所选用户未通过实名认证，请先实名认证')
        else:
            raise ParameterError('没有找到对应的注册用户')
        #更新车牌号校验存储规则
        short = self.get_parameter('short_number').strip()
        mid = self.get_parameter('mid_number').strip()
        if plate_number:
            if not short or not mid:
                raise ParameterError('请选择车牌号前两位。如“黑A')
            if re.match(r'^[a-z_A-Z_0-9]{5}$', plate_number):
                 plate_number = plate_number.upper()
                 plate_number1 = short +mid +" "+plate_number
                 create_car.plate_number=plate_number1
            else:
                raise ParameterError('您输入的车牌号不正确，请输入由英文或数字组成的五位字符串')
        else:
            raise ParameterError('车牌号不能为空')
#         if plate_number:
#             plate_number = plate_number.upper()
#             create_car.plate_number=plate_number
#         else:
#             raise ParameterError('未输入车牌号')
        now_year = now.strftime("%Y ")
        if start_date:
            create_car.start_date=start_date
        else:
            create_car.start_date=now_year
        if plate_expiration_periods:
            now_month=now.strftime("%Y-%m")
            if plate_expiration_periods<now_month:
                raise ParameterError('输入的校验有效期已过期')
            else:
                create_car.plate_expiration_periods=plate_expiration_periods
        else:
            raise ParameterError('未输入行驶证校验有效期')
        #行驶证
        if plate_image_left:
            image_tool = ImageTools()
            plate_image_left_url = image_tool.save(request_file=plate_image_left, file_folder=ImageFolderType.car, old_file='')
            if plate_image_left_url:
                create_car.plate_image_left.append( plate_image_left_url )
            else:
                raise ParameterError('保存行驶证照片正页正面图片失败')
        else:
            raise ParameterError('请选择添加行驶证照片正页正面图片')
        
        if plate_image_right:
            image_tool = ImageTools()
            plate_image_right_url = image_tool.save(request_file=plate_image_right, file_folder=ImageFolderType.car, old_file='')
            if plate_image_right_url :
                create_car.plate_image_left.append( plate_image_right_url )
            else:
                raise ParameterError('保存行驶证照片附页正面图片失败')
        else:
            raise ParameterError('请选择添加行驶证照片附页正面图片')
           #交强险 
        if liability_image:
            image_tool = ImageTools()
            liability_image_url = image_tool.save(request_file=liability_image, file_folder=ImageFolderType.car, old_file='')
            if liability_image_url :
                create_car.liability_image  = liability_image_url 
            else:
                raise ParameterError('保存交强险照片失败')
        else:
            raise ParameterError('请选择添加交强险照片图片')
        #商业险
        if commercial_image:
            image_tool = ImageTools()
            commercial_image_url = image_tool.save(request_file=commercial_image, file_folder=ImageFolderType.car, old_file='')
            if commercial_image_url :
                create_car.commercial_image  = commercial_image_url 
            else:
                raise ParameterError('保存商业险照片图片失败')
        else:
            raise ParameterError('请选择添加商业险照片图片')
        

        return create_car
    
#验证货物
    def validation_cargo(self, cargo):
        cargo_state= self.get_parameter("cargo_state").strip()
        if cargo_state =="create":
            cargo_priority= self.get_parameter("cargo_priority").strip()
            cargo_number= self.get_parameter("cargo_number").strip()
            cargo_describe= self.get_parameter("cargo_describe").strip()
            cargo_state1= self.get_parameter("cargo_insurance_state").strip()
            count = Cargo.objects(cargo_priority=cargo_priority,cargo_number=cargo_number, cargo_name = cargo_describe).count()
            if count>0:
                 raise ParameterError('货物信息已存在，请不可重复创建')
        elif cargo_state =="edit":
            cargo_priority= self.get_parameter("cargo_priority_edit").strip()
            cargo_number= self.get_parameter("cargo_number_edit").strip()
            cargo_describe= self.get_parameter("cargo_describe_edit").strip()
            cargo_state1= self.get_parameter("cargo_insurance_state_edit").strip()
            count = Cargo.objects(cargo_priority=cargo_priority,cargo_number=cargo_number, cargo_name = cargo_describe).count()
            if count>1:
                raise ParameterError('编辑后的货物信息已存在，请重新填写')
        else:
            raise ParameterError('不能判断货物信息编辑状态')
        count = Cargo.objects(cargo_number=cargo_number).count()
        if count>1:
            raise ParameterError('货物编码重复，请重新填写')
        elif count ==1:
            approve_cargo=Cargo.objects(cargo_number=cargo_number).first()
            if approve_cargo.id != cargo.id:
                raise ParameterError('货物编码已存在，请重新填写')
        if cargo_describe:
                try:
                    cargo.cargo_name = cargo_describe
                except:
                    raise ParameterError('货物名称存储失败')
        else:
            raise ParameterError('未输入货物名称')
        if cargo_priority:
            try:
                    cargo_priority = int(cargo_priority)
            except:
                    raise ParameterError('货物优先级应为正整数')
            try:
                    cargo.cargo_priority = cargo_priority
            except:
                    raise ParameterError('货物优先级存储失败')
        else:
            raise ParameterError('未输入优先级')
        if cargo_number:
            try:
                    cargo.cargo_number = cargo_number
            except:
                    raise ParameterError('货物编号名称存储失败') 
        else:
            raise ParameterError('未输入货物编号')
        #货物状态
        if cargo_state1:
            try:
                if cargo_state1 =="0":
                    cargo.state =False
                elif cargo_state1 =="1":
                    cargo.state =True  
                else:
                    raise ParameterError('网络不稳定，货物小类投保状态不正确')
            except:
                     raise ParameterError('货物小类投保状态存储失败')
        else:
            raise ParameterError('未输入货物编号')
        return cargo
        
#关联货物详情
    def validation_cargo_and_product(self, insurance_product,cargo,product_cargo):
        product_rate_type= self.get_parameter("product_rate_name").strip()
#         count = ProductCargo.objects(good_type=product_rate_type, product=insurance_product,cargo=product_cargo).count()
        test1=0
        for product_rate in insurance_product.product_rate_list:
            if product_rate.good_type == product_rate_type:
                test1=1
                break
        if test1==0:
            raise ParameterError('本产品无此货物类型')
        count = ProductCargo.objects(product=insurance_product,cargo=cargo).count()
        if count>0:
            cargo_name=cargo.cargo_name
            message  = cargo_name+"已对应本产品承包的其他类型货物"
            raise ParameterError(message)
        product_cargo.state=product_rate_type
        if insurance_product:
            product_cargo.product=insurance_product
        else:
            raise ParameterError('未找到所选产品')
        if cargo:
            product_cargo.cargo=cargo
        else:
            raise ParameterError('未找到所选货物')

        return product_cargo  
        
      #验证平台产品类型
    def validation_platform_products(self, platformProducts,content):
        wx_state = self.get_parameter("wx_state").strip()     #状态
        insurance_name= self.get_parameter("insurance_name").strip()
        if insurance_name:
            try:
                    platformProducts.name = insurance_name
            except:
                    raise ParameterError('产品名称保存失败')
        else:
            raise ParameterError('产品名称不能为空')
      #列表显示图片
        wx_product_pic = self.request.FILES.get('wx_product_pic', '')     #列表显示图片
        if wx_product_pic:
            print(wx_product_pic.size)
            if wx_product_pic.size > 50000:#图片大小不能超过300k
                raise ParameterError('上传的产品图标过大，图片大小不能超过50k')
            image_tool = ImageTools()
            old_wx_product_pic1 =""
            if wx_state =="edit":
                old_wx_product_pic1 =platformProducts.wx_product_pic
            wx_product_pic_url = image_tool.save(request_file=wx_product_pic, file_folder=ImageFolderType.wx_share, old_file=old_wx_product_pic1)
            if wx_product_pic_url:
                try:
                    platformProducts.wx_product_pic = wx_product_pic_url
                except:
                    raise ParameterError('保存产品图标失败。')
            else:
                raise ParameterError('保存列表页产品图标失败')
        else:
            if wx_state =="create":
                raise ParameterError('请选择添加产品图标图片')
        #产品类型
        product_type= self.get_parameter("product_type").strip()
        if product_type:
            try:
                    platformProducts.product_type = product_type
            except:
                    raise ParameterError('产品类型保存失败')
        else:
            raise ParameterError('产品类型不能为空')
        priority= self.get_parameter("priority").strip()
        if priority:
            try:
                    platformProducts.priority = priority
            except:
                    raise ParameterError('优先级保存失败')
        else:
            raise ParameterError('优先级不能为空')
        
        isline= self.get_parameter("isline").strip()
        if isline:
            try:
                    platformProducts.isline = isline
            except:
                    raise ParameterError('投保方式保存失败')
        else:
            raise ParameterError('投保方式不能为空')
        if isline =='2':
                    product_url= self.get_parameter("product_url").strip()
                    if product_url:
                        try:
                                platformProducts.product_url = product_url
                        except:
                                raise ParameterError('产品链接地址保存失败')
                    else:
                        raise ParameterError('产品链接地址不能为空')
        else:
            insurance_feature= self.get_parameter("insurance_feature").strip()
            if insurance_feature:
                try:
                        platformProducts.product_characteristic = insurance_feature
                except:
                        raise ParameterError('产品特点保存失败')
            else:
                raise ParameterError('产品特点不能为空')
            if content:
                try:
                        platformProducts.product_introduce = content
                except:
                        raise ParameterError('产品介绍保存失败')
            else:
                raise ParameterError('产品介绍不能为空')
        #*********************************微信端分享页面内容验证
        #标题
        wx_share_title= self.get_parameter("wx_share_title").strip()
        if wx_share_title:
            if len(wx_share_title)>22:
                raise ParameterError('微信分享标题最多输入22个字符')
            try:
                    platformProducts.wx_share_title = wx_share_title
            except:
                    raise ParameterError('微信分享标题保存失败')
        else:
            raise ParameterError('微信分享标题不能为空')
        wx_share_title= self.get_parameter("wx_share_title").strip()
        #描述
        wx_share_desc= self.get_parameter("wx_share_desc").strip()
        if wx_share_desc:
            if len(wx_share_desc)>50:
                raise ParameterError('微信分享描述最多输入50个字符')
            try:
                    platformProducts.wx_share_desc = wx_share_desc
            except:        
                    raise ParameterError('微信分享描述保存失败')
        else:
            raise ParameterError('微信分享描述不能为空')
        #分享显示图片
#         wx_state = self.get_parameter("wx_state").strip()     #状态
        if  wx_state !="create" and  wx_state !="edit":
            raise ParameterError('网络不稳定，未确定产品编译状态。')
        wx_share_pic = self.request.FILES.get('wx_share_pic', '')     #分享显示图片
        if wx_share_pic:
            print(wx_share_pic.size)
   #         if wx_share_pic.size > 50000:#图片大小不能超过300k
   #             raise ParameterError('上传的分享图片过大，图片大小不能超过50k')
            image_tool = ImageTools()
            old_wx_share_pic1 =""
            if wx_state =="edit":
                old_wx_share_pic1 =platformProducts.wx_share_pic
            wx_share_pic_url = image_tool.save(request_file=wx_share_pic, file_folder=ImageFolderType.wx_share, old_file=old_wx_share_pic1)
            if wx_share_pic_url:
                try:
                    platformProducts.wx_share_pic=wx_share_pic_url
                except:
                    raise ParameterError('保存分享显示图片失败。')
            else:
                raise ParameterError('保存分享显示图片失败')
        else:
            if wx_state =="create":
                raise ParameterError('请选择添加分享显示图片')

        return platformProducts    
        
        
#验证货物大类
    def validation_cargo_type(self, cargotype):
        cargo_type_state= self.get_parameter("cargo_type_state").strip()
        if cargo_type_state =="create":
            ct_name= self.get_parameter("ct_name").strip()
            ct_priority= self.get_parameter("ct_priority").strip()
            ct_state= self.get_parameter("ct_state").strip()
            try:
                count = CargoType.objects(ct_name=ct_name,ct_priority=ct_priority, ct_state = ct_state).count()
            except:
                count=0
            if count>0:
                 raise ParameterError('货物大类信息已存在，请不可重复创建')
        elif cargo_type_state =="edit":
            ct_name= self.get_parameter("ct_name_edit").strip()
            ct_priority= self.get_parameter("ct_priority_edit").strip()
            ct_state= self.get_parameter("ct_state_edit").strip()
            try:
                count = CargoType.objects(ct_name=ct_name,ct_priority=ct_priority, ct_state = ct_state).count()
            except:
                count=0
            if count>1:
                raise ParameterError('编辑后的货物大类信息已存在，请重新填写')
        else:
            raise ParameterError('不能判断货物大类信息编辑状态')
        count1 = CargoType.objects(ct_name=ct_name).count()
        if count>1:
            raise ParameterError('货物大类名称已存在，请重新填写')
        elif count1 ==1:
            approve_cargo=CargoType.objects(ct_name=ct_name).first()
            a=approve_cargo.id
            b=approve_cargo.ct_name
            c=cargotype.id
            if approve_cargo.id != cargotype.id :
                raise ParameterError('货物大类名称编码已存在，请重新填写')
        if not ct_name or not ct_state:
            raise ParameterError('货物大类名称，状态，两者都不可为空，优先级为空则默认值为50,请补充信息')
        try:
            cargotype.ct_name =ct_name
        except:
                 raise ParameterError('货物大类名称存储失败')
        try:
            ct_priority = int(ct_priority)
            cargotype.ct_priority =ct_priority
        except:
                 raise ParameterError('货物大类优先级应为正数')
#         if ct_state !="0" or ct_state !="1":
#             raise ParameterError('网络不稳定，货物大类投保状态不正确')
        try:
            if ct_state =="0":
                cargotype.ct_state =False
            elif ct_state =="1":
                cargotype.ct_state =True  
            else:
                raise ParameterError('网络不稳定，货物大类投保状态不正确')
        except:
                 raise ParameterError('货物大类投保状态存储失败')
        return cargotype
        
        
        
    #验证中介渠道
    def validation_intermediary(self, intermediary):
        intermediary_name = self.request.POST.get('intermediary_name')
        if intermediary_name:
            intermediary.intermediary_name=intermediary_name
        else:
            raise ParameterError("中介名称不可为空")
        intermediary_introduce = self.request.POST.get('intermediary_description')
        if intermediary_introduce:
            intermediary.intermediary_introduce=intermediary_introduce
        else:
            raise ParameterError("中介描述不可为空")
        
        intermediary_profit_point = self.request.POST.get('intermediary_profit_point')
        if intermediary_profit_point:
            try:
                intermediary_profit_point= float(intermediary_profit_point)
            except:
                raise ParameterError("中介利润点请输入数字")
            if intermediary_profit_point <0:
                raise ParameterError("中介利润点为正数")
            if intermediary_profit_point*100 > int(intermediary_profit_point*100):
                raise ParameterError("中介利润点最多输入两位小数")
            intermediary.intermediary_profit_point=intermediary_profit_point
        else:
            raise ParameterError("中介利润点不可为空")
        
        intermediary_phone = self.request.POST.get('intermediary_phone')
        if intermediary_phone:
            if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', intermediary_phone):
                if not re.match(r'^(0[0-9]{2,3}-)[0-9]{5,9}$', intermediary_phone):
#                 0\d{2,3}-\d{5,9}|0\d{2,3}-\d{5,9}

                    raise ParameterError( '请核对联系电话，可输入手机号或座机号，座机号码格式为“0451-5555555”')
            intermediary.intermediary_phone=intermediary_phone
        else:
            raise ParameterError("中介电话不可为空")
        
        #可承包订单车辆类型
        choose_car_type_list = self.request.REQUEST.getlist("choose_car_type")
        car_type_list = []
        intermediary.order_car_type =[]
        if not choose_car_type_list:
            raise ParameterError("可保保单车辆类型不可为空")
        if choose_car_type_list:
            for car_type  in choose_car_type_list:
                car_type_list.append(car_type)
        intermediary.order_car_type=car_type_list
            
        #车牌号
        choose_plate_list = self.request.REQUEST.getlist("choose_plate")
        plate_number_list = []
        intermediary.plate_number_list =[]
        if not choose_plate_list:
            raise ParameterError("可保车牌省份不可为空")
        if choose_plate_list:
            for plate  in choose_plate_list:
                plate_number_list.append(plate)
        intermediary.plate_number_list=plate_number_list
        
        choose_company_list = self.request.REQUEST.getlist("choose_com")
        company_list = []
        intermediary.intermediary_company_list =[]
        if choose_company_list:
            try:
                company_list = InsuranceCompany.objects(id__in=choose_company_list)
                for company_set in company_list:
                    if company_set not in intermediary.intermediary_company_list :
                        intermediary.intermediary_company_list.append(company_set)
            except:
                raise ParameterError("关联分公司查询出错，请稍后再试")
        return intermediary
        
    #   验证机动车保险订单
    def validation_jdclbx(self, jdclbx_order):
        jdclbx_state = self.get_parameter('jdclbx_state').strip()       #订单状态
        #车辆信息部分
        id_plate_image_left = self.request.FILES.get('id_plate_image_left', '')     #行驶证正页
        id_plate_image_right = self.request.FILES.get('id_plate_image_right', '')     #行驶证附页
        short_number = self.get_parameter('short_number').strip()       #车牌号第一位
        mid_number = self.get_parameter('mid_number').strip()       #车牌号第二位
        plate_number = self.get_parameter('plate_number').strip()       #车牌号后五位
        car_type = self.get_parameter('car_type').strip()       #车辆类型
        holder = self.get_parameter('holder').strip()       #所有人
        use_property = self.get_parameter('use_property').strip()       #车使用性质
        brand_digging = self.get_parameter('brand_digging').strip()       #品牌型号
        car_number = self.get_parameter('car_number').strip()       #车辆识别代码
        engine_number = self.get_parameter('engine_number').strip()       #发动机号
        issue_date = self.get_parameter('issue_date').strip()       #注册日期
        people_number = self.get_parameter('people_number').strip()       #核载人数(位)
        load_weight = self.get_parameter('load_weight').strip()       #核载质量(Kg)
        #添加字段
        order_car_type = self.get_parameter('order_car_type').strip()       #投保车辆大类选择
        city_area = self.get_parameter('city_area').strip()       #车辆城市编码
        
        #行驶证正页
        if id_plate_image_left:
            image_tool = ImageTools()
            try:
                plate_image_left_url = image_tool.save(request_file=id_plate_image_left, file_folder=ImageFolderType.jdclbx, old_file='')
                if plate_image_left_url:
                    jdclbx_order.plate_image_left=plate_image_left_url
                else:
                    raise ParameterError('行驶证正页图片上传失败')
            except:
                raise ParameterError('保存行驶证正页失败')
        else:
            if jdclbx_state == 'create':
                raise ParameterError('请上传行驶证正页图片')
        #行驶证附页
        if id_plate_image_right:
            image_tool = ImageTools()
            try:
                plate_image_right_url = image_tool.save(request_file=id_plate_image_right, file_folder=ImageFolderType.jdclbx, old_file='')
                if plate_image_right_url:
                    jdclbx_order.plate_image_right=plate_image_right_url
                else:
                    raise ParameterError('行驶证附页图片上传失败')
            except:
                raise ParameterError('保存行驶证附页失败')
        else:
            if jdclbx_state == 'create':
                raise ParameterError('请上传行驶证附页图片')
        
        ##投保车辆大类选择
        if order_car_type:
            jdclbx_order.order_car_type = order_car_type
        else:
            raise ParameterError('请选择投保车辆大类')
        
        #车辆城市编码
        if city_area:
            try:
                city_set = CargoArea.objects(code=city_area).first()
            except:
                raise ParameterError('网络不稳定，未找到对应城市信息')
            jdclbx_order.city = city_set
        else:
            raise ParameterError('请选择车辆城市')
        
        #车牌号
        if short_number and mid_number and plate_number:
            if re.match(r'^[a-z_A-Z_0-9]{5}$', plate_number):
                plate_number = plate_number.upper()
                jdclbx_order.plate_number = short_number+' '  + mid_number+' ' + plate_number
            else:
                raise ParameterError('您输入的车牌号不正确，请输入英文或数字')
        else:
            raise ParameterError('请输入车牌号')
        
        #2017添加验证部分
        #根据车牌号和订单货物大类筛选适合本订单的保险中介渠道
        if order_car_type == 'passenger_car':
                order_car_type_name ='九座以下客车'
        elif order_car_type == 'truck':  
            order_car_type_name ='货车'
        else:
            order_car_type_name = order_car_type
        intermediary_list = Intermediary.objects.filter(state = True, order_car_type__icontains=order_car_type, plate_number_list__icontains=short_number )
        test_count =intermediary_list.count()
        if test_count == 0:
            message = "暂未开通"+str(order_car_type_name) + '车牌号为' + str(short_number)+ '部分投保业务'
            raise ParameterError(message)
        else:
            intermediary_list_test=[]
            user_set = User.objects(is_active=True)
            #transport_set = transport_set.filter(user__in=user_set)
            for intermediary_detail in intermediary_list:
                try:
                    intermediary_people_count = IntermediaryPeople.objects(intermediary =intermediary_detail , user__in=user_set ).count()
                    if intermediary_people_count>0:
                        intermediary_list_test.append(intermediary_detail)
                except:
                    pass
            if len(intermediary_list_test)>0:
                jdclbx_order.intermediary_list = intermediary_list_test
            else:
                message = "暂未开通"+str(order_car_type_name) + '车牌号为' + str(short_number)+ '部分投保业务。'
                raise ParameterError(message)
        
            
        #车辆类型
        if car_type:
            jdclbx_order.car_type = car_type
        else:
#             jdclbx_order.car_type =''
             raise ParameterError('请选择车辆类型')
        #所有人
        if holder:
            jdclbx_order.holder = holder
        else:
            jdclbx_order.holder = ''
#             raise ParameterError('请输入所有人')
        #使用性质
        if use_property:
            jdclbx_order.use_property = use_property
        else:
#             jdclbx_order.use_property = ''
            raise ParameterError('请选择使用性质')
        #品牌型号
        if brand_digging:
            brand_digging = brand_digging.upper()
            jdclbx_order.brand_digging = brand_digging
        else:
            jdclbx_order.brand_digging = ''
#             raise ParameterError('请输入品牌型号')
        #车辆识别代码
        if car_number:
            car_number = car_number.replace(' ', '')
            test_answer=checkVIN(car_number)
            if test_answer == 'success':
                jdclbx_order.car_number = car_number
            else:
                raise ParameterError(test_answer)
        else:
            jdclbx_order.car_number =''
#             raise ParameterError('请输入车辆识别代码')
        #发动机号
        if engine_number:
            jdclbx_order.engine_number = engine_number
        else:
            jdclbx_order.car_number =''
#             raise ParameterError('请输入发动机号')
        #注册日期
        if issue_date:
            now = datetime.now()
            otherStyleTime = now.strftime("%Y-%m-%d ")
            if otherStyleTime < issue_date:
                raise ParameterError('车辆注册日期不能晚于当前时间')
            jdclbx_order.issue_date = issue_date
        else:
            pass
#             raise ParameterError('请输入车辆注册日期')
        #核载人数(位)
        if people_number:
            jdclbx_order.people_number = people_number
        else:
            jdclbx_order.people_number = ''
        #核载质量(Kg)
        if load_weight:
            jdclbx_order.load_weight = load_weight
        else:
            jdclbx_order.load_weight =''
#         if not people_number  and not load_weight:
#             raise ParameterError('请输入核载人数或核载质量')

        #录入投保人信息
        client_id = self.get_parameter('client_id').strip()       #投保使用账户
        user_classify = self.get_parameter('user_classify').strip()       #投保人身份选择
        #录入投保人信息--单位
        business_license_image = self.request.FILES.get('business_license_image', '')     #营业执照
        applicant_company_name = self.get_parameter('applicant_company_name').strip()       #单位名称
        organ_number = self.get_parameter('organ_number').strip()       #组织机构号(或营业执照号)
        #录入投保人信息--个人
        id_card_up = self.request.FILES.get('id_card_up', '')     #身份证正面
        id_card_down = self.request.FILES.get('id_card_down', '')     #身份证背面
        applicant_name = self.get_parameter('applicant_name').strip()       #投保人姓名
        certificate_number = self.get_parameter('certificate_number').strip()       #身份证号
        applicant_phone = self.get_parameter('applicant_phone').strip()       #投保人手机号
        #录入投保人信息--被保人
        insured_information = self.get_parameter('insured_information').strip()       #被保人身份信息选择，same同投保人，different手工录入
        #insured_name = self.get_parameter('insured_name').strip()       #被保人姓名
        insured_phone = self.get_parameter('insured_phone').strip()       #被保人手机号
        policy_address = self.get_parameter('policy_address').strip()       #保单邮寄地址
        startSiteName_prov = self.get_parameter('startSiteName_prov').strip()       #保单邮寄地址前部-省
        startSiteName_city = self.get_parameter('startSiteName_city').strip()       #保单邮寄地址前部-市
        startSiteName_dist = self.get_parameter('startSiteName_dist').strip()       #保单邮寄地址前部-区
        #2017/2/8添加字段
        insured_classify = self.get_parameter('insured_classify').strip()       #被保人身份选择
        insured_card_up = self.request.FILES.get('insured_card_up', '')     #身份证正面
        insured_card_down = self.request.FILES.get('insured_card_down', '')     #身份证背面
        insured_applicant_name = self.get_parameter('insured_applicant_name').strip()       #被保人姓名
        insured_certificate_number = self.get_parameter('insured_certificate_number').strip()       #身份证号
        insured_business_license_image = self.request.FILES.get('insured_business_license_image', '')     #营业执照
        insured_applicant_company_name = self.get_parameter('insured_applicant_company_name').strip()       #单位名称
        insured_organ_number = self.get_parameter('insured_organ_number').strip()       #组织机构号(或营业执照号)
        
        #使用账户
        if client_id:
            try:
                client_set = Client.objects(id = client_id).first()
                if client_set:
                    jdclbx_order.client = client_set
                else:
                    raise ParameterError("未找到所选择的账户信息，请核对后重新选择")
            except:
                raise ParameterError('网络延迟，未获取到使用的账户信息，请刷新后重新选择')
        else:
            raise ParameterError('请选择使用的账户')
         
        #投保人身份选择
        #单位
        if user_classify =='unit':
            jdclbx_order.user_classify = user_classify
            #营业执照
            if business_license_image:
                image_tool = ImageTools()
                try:
                    business_license_image_url = image_tool.save(request_file=business_license_image, file_folder=ImageFolderType.jdclbx, old_file='')
                    if business_license_image_url:
                        jdclbx_order.business_license_image=business_license_image_url
                    else:
                        raise ParameterError('营业执照图片上传失败')
                except:
                    raise ParameterError('保存营业执照失败')
            else:
                if jdclbx_state == 'create':
                    raise ParameterError('请上传营业执照图片')
            #单位名称
            if applicant_company_name:
                jdclbx_order.applicant_company_name = applicant_company_name
            else:
                jdclbx_order.applicant_company_name =''
#                 raise ParameterError('请输入单位名称')
            if organ_number:
                jdclbx_order.organ = organ_number
            else:
                jdclbx_order.organ = ''
#                 raise ParameterError('请输入组织机构代码或营业执照号')
            if jdclbx_state == 'edit':
                #清空个人信息
                jdclbx_order.id_card_up=''
                jdclbx_order.id_card_down=''
                jdclbx_order.applicant_name = ''
                jdclbx_order.certificate_number = ''
        #个人
        elif user_classify == 'personal':
            jdclbx_order.user_classify = user_classify
            #身份证正面
            if id_card_up:
                image_tool = ImageTools()
                try:
                    id_card_up_url = image_tool.save(request_file=id_card_up, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_card_up_url:
                        jdclbx_order.id_card_up=id_card_up_url
                    else:
                        raise ParameterError('身份证正面图片上传失败')
                except:
                    raise ParameterError('保存身份证正面失败')
            else:
                if jdclbx_state == 'create':
                    raise ParameterError('请上传身份证正面图片')
            #身份证背面
            if id_card_down:
                image_tool = ImageTools()
                try:
                    id_card_down_url = image_tool.save(request_file=id_card_down, file_folder=ImageFolderType.jdclbx, old_file='')
                    if id_card_up_url:
                        jdclbx_order.id_card_down=id_card_down_url
                    else:
                        raise ParameterError('身份证背面图片上传失败')
                except:
                    raise ParameterError('保存身份证背面失败')
            else:
                if jdclbx_state == 'create':
                    raise ParameterError('请上传身份证背面图片')
            #投保人姓名
            if applicant_name:
                jdclbx_order.applicant_name = applicant_name
            else:
                jdclbx_order.applicant_name = ''
#                 raise ParameterError('请输入投保人姓名')
            #身份证号
            if certificate_number:
                test_idcard_number=checkIdcard(certificate_number)
                if test_idcard_number=='success':
                    jdclbx_order.certificate_number = certificate_number
                else:
                    raise ParameterError(test_idcard_number)
            else:
                jdclbx_order.certificate_number =''
#                 raise ParameterError('请输入投保人身份证号')
            if jdclbx_state == 'edit':
                #清空单位信息
                jdclbx_order.applicant_company_name=''
                jdclbx_order.business_license_image=''
                jdclbx_order.organ=''
        else:
            raise ParameterError('请选择投保人身份，单位或个人')
        #投保人手机号
        if applicant_phone:
            if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', applicant_phone):
                raise ParameterError( '请输入正确的投保人手机号码')
            jdclbx_order.applicant_phone = applicant_phone
        else:
             raise ParameterError('请输入投保人手机号')
         #被保人身份信息选择
        if insured_information == 'same':
            if jdclbx_order.user_classify == 'unit':
                jdclbx_order.insured_name = jdclbx_order.applicant_company_name
                jdclbx_order.insured_phone = jdclbx_order.applicant_phone
                jdclbx_order.insured_license_image = jdclbx_order.business_license_image#营业执照
                jdclbx_order.insured_number = jdclbx_order.organ#组织机构证件号码
                jdclbx_order.insured_classify = jdclbx_order.user_classify#被保险人身份状态
                jdclbx_order.insured_card_up = ''
                jdclbx_order.insured_card_down = ''
            elif jdclbx_order.user_classify == 'personal':
                jdclbx_order.insured_name = jdclbx_order.applicant_name 
                jdclbx_order.insured_phone = jdclbx_order.applicant_phone
                jdclbx_order.insured_classify = jdclbx_order.user_classify#被保险人身份状态
                jdclbx_order.insured_number = jdclbx_order.certificate_number#被保险人身份证号码
                jdclbx_order.insured_card_up = jdclbx_order.id_card_up#身份证正页
                jdclbx_order.insured_card_down = jdclbx_order.id_card_down#身份证背面
                jdclbx_order.insured_license_image = ''
            else:
                raise ParameterError('投保人状态出错，请选择手工录入方式')
        elif  insured_information =='different':
            #单位
            if insured_classify =='unit':
                jdclbx_order.insured_classify = insured_classify
                #营业执照
                if insured_business_license_image:
                    image_tool = ImageTools()
                    try:
                        insured_business_image_url = image_tool.save(request_file=insured_business_license_image, file_folder=ImageFolderType.jdclbx, old_file='')
                        if insured_business_image_url:
                            jdclbx_order.insured_license_image=insured_business_image_url
                        else:
                            raise ParameterError('被保人营业执照图片上传失败')
                    except:
                        raise ParameterError('保存被保人营业执照失败')
                else:
                    if jdclbx_state == 'create':
                        raise ParameterError('请上传被保人营业执照图片')
                #单位名称
                if insured_applicant_company_name:
                    jdclbx_order.insured_name = insured_applicant_company_name
                else:
                    jdclbx_order.insured_name = ''
#                     raise ParameterError('请输入被保人单位名称')
                if insured_organ_number:
                    jdclbx_order.insured_number = insured_organ_number
                else:
                    jdclbx_order.insured_number =''
#                     raise ParameterError('请输入被保人组织机构代码或营业执照号')
                if jdclbx_state == 'edit':
                    #清空个人信息
                    jdclbx_order.insured_card_up=''
                    jdclbx_order.insured_card_down=''
            #个人
            elif insured_classify == 'personal':
                jdclbx_order.insured_classify = insured_classify
                #身份证正面
                if insured_card_up:
                    image_tool = ImageTools()
                    try:
                        insured_card_up_url = image_tool.save(request_file=insured_card_up, file_folder=ImageFolderType.jdclbx, old_file='')
                        if insured_card_up_url:
                            jdclbx_order.insured_card_up=insured_card_up_url
                        else:
                            raise ParameterError('身份证正面图片上传失败')
                    except:
                        raise ParameterError('保存身份证正面失败')
                else:
                    if jdclbx_state == 'create':
                        raise ParameterError('请上传身份证正面图片')
                #身份证背面
                if insured_card_down:
                    image_tool = ImageTools()
                    try:
                        insured_card_down_url = image_tool.save(request_file=insured_card_down, file_folder=ImageFolderType.jdclbx, old_file='')
                        if insured_card_down_url:
                            jdclbx_order.insured_card_down = insured_card_down_url
                        else:
                            raise ParameterError('身份证背面图片上传失败')
                    except:
                        raise ParameterError('保存身份证背面失败')
                else:
                    if jdclbx_state == 'create':
                        raise ParameterError('请上传身份证背面图片')
                #投保人姓名
                if insured_applicant_name:
                    jdclbx_order.insured_name = insured_applicant_name
                else:
                    jdclbx_order.insured_name =''
#                     raise ParameterError('请输入投保人姓名')
                #身份证号
                if insured_certificate_number:
                    test_idcard_number1=checkIdcard(insured_certificate_number)
                    if test_idcard_number1=='success':
                        jdclbx_order.insured_number = insured_certificate_number
                    else:
                        message1 = '被保人' + str(test_idcard_number1)
                        raise ParameterError(message1)
                    
                else:
                     jdclbx_order.insured_number =''
#                     raise ParameterError('请输入投保人身份证号')
                if jdclbx_state == 'edit':
                    #清空单位信息
                    jdclbx_order.insured_license_image=''
            else:
                raise ParameterError('请选择被保人身份，单位或个人')
                
            
#              if insured_name:
#                  jdclbx_order.insured_name = insured_name
#              else:
#                  raise ParameterError('请输入被投保人姓名')
            if insured_phone:
                 if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', insured_phone):
                     raise ParameterError( '请输入正确的被投保人手机号码')
                 jdclbx_order.insured_phone = insured_phone
            else:
                 raise ParameterError('请输入被投保人手机号')
        else:
             raise ParameterError('请输入选择被保人信息录入方式')
         
        
        #2017/2/8添加新需求，北京部分订单无保单邮寄地址
        if city_area != '1101':
            #邮寄地址前缀
            startSiteName_prov = self.get_parameter('startSiteName_prov').strip()       #保单邮寄地址前部-省
            try:
                prov_set = CargoArea.objects(code =startSiteName_prov ).first()
                prov_name =str(prov_set.name)
            except:
                raise ParameterError('网络不稳定，未获取保单邮寄地址省份信息')
            
            startSiteName_city = self.get_parameter('startSiteName_city').strip()       #保单邮寄地址前部-市
            try:
                city_set = CargoArea.objects(code =startSiteName_city ).first()
                city_name =str(city_set.name)
            except:
                raise ParameterError('网络不稳定，未获取保单邮寄地址市级信息。')
            
            startSiteName_dist = self.get_parameter('startSiteName_dist').strip()       #保单邮寄地址前部-区
            try:
                dist_set = CargoArea.objects(code =startSiteName_dist ).first()
                dist_name =str(dist_set.name)
            except:
                raise ParameterError('网络不稳定，为获取保单邮寄地址区级信息')
            
            if prov_name and city_name and dist_name:
                mail_address = str(prov_name)+ ' ' + str(city_name) +' ' +str(dist_name)
                jdclbx_order.mail_address =mail_address
            else:
                raise ParameterError('网络不稳定，为获取保单邮寄地址省市区三级全部信息')
            
            #保单邮寄地址
            if policy_address:
                 jdclbx_order.policy_address = policy_address
            else:
                 raise ParameterError('请输入保单邮寄地址')

        #录入投保种类
        liability_state = self.get_parameter('liability_state').strip()       #交强险
        vehicle_vessel_tax_state = self.get_parameter('vehicle_vessel_tax_state').strip()       #车船税
        third_insurance = self.get_parameter('third_insurance').strip()       #三者险
        damage_insurance = self.get_parameter('damage_insurance').strip()       #车损险
        glass_insurance = self.get_parameter('glass_insurance').strip()       #玻璃险
        driver_insurance = self.get_parameter('driver_insurance').strip()       #司机险
        theft_insurance = self.get_parameter('theft_insurance').strip()       #盗抢险
        passenger_insurance = self.get_parameter('passenger_insurance').strip()       #乘客险
        iop_insurance = self.get_parameter('iop_insurance').strip()       #不计免赔险
        autoignition_insurance = self.get_parameter('autoignition_insurance').strip()       #自燃损失
        wading_insurance = self.get_parameter('wading_insurance').strip()       #涉水险
        scratch_insurance = self.get_parameter('scratch_insurance').strip()       #划痕险
        liability_expectStartTime = self.get_parameter('liability_expectStartTime').strip()       #交强险保险起期
        commercial_expectStartTime = self.get_parameter('commercial_expectStartTime').strip()       #商业险保险起期
        special_agreement = self.get_parameter('special_agreement').strip()       #特别约定
        
        #交强险
        if liability_state=="yes":
            jdclbx_order.liability_state = True
        else:
            jdclbx_order.liability_state = False
         #车船税
        if vehicle_vessel_tax_state=="yes":
            jdclbx_order.vehicle_vessel_tax_state = True
        else:
            jdclbx_order.vehicle_vessel_tax_state = False
         #三者险
        if third_insurance:
            try:
                third_insurance1 = float(third_insurance)
                third_insurance2 = int(third_insurance)
                if third_insurance2 < third_insurance1:
                    raise ParameterError('网络不稳定，获取三者险状态错误，请重新选择三者险投保状态。')
                else:
                    jdclbx_order.third_insurance = third_insurance2
            except:
                raise ParameterError('网络不稳定，获取三者险状态错误，请重新选择三者险投保状态')
        else:
            raise ParameterError('请选择三者险投保状态')
        #车损险
        if damage_insurance=="yes":
            jdclbx_order.damage_insurance = True
        else:
            jdclbx_order.damage_insurance = False
        #玻璃险
        if glass_insurance:
            jdclbx_order.glass_insurance = glass_insurance
        else:
            raise ParameterError('请选择玻璃险投保状态')
        #司机险
        if driver_insurance:
            try:
                driver_insurance1 = float(driver_insurance)
                driver_insurance2 = int(driver_insurance)
                if driver_insurance2 < driver_insurance1:
                    raise ParameterError('网络不稳定，获取司机险状态错误，请重新选择三者险投保状态。')
                else:
                    jdclbx_order.driver_insurance = driver_insurance2
            except:
                raise ParameterError('网络不稳定，获取司机险状态错误，请重新选择三者险投保状态')
        else:
            raise ParameterError('请选择司机险投保状态')
        #盗抢险
        if theft_insurance=="yes":
            jdclbx_order.theft_insurance = True
        else:
            jdclbx_order.theft_insurance = False
        #乘客险
        if passenger_insurance:
            try:
                passenger_insurance1 = float(passenger_insurance)
                passenger_insurance2 = int(passenger_insurance)
                if passenger_insurance2 < passenger_insurance1:
                    raise ParameterError('网络不稳定，获取乘客险状态错误，请重新选择三者险投保状态。')
                else:
                    jdclbx_order.passenger_insurance = passenger_insurance2
            except:
                raise ParameterError('网络不稳定，获取乘客险状态错误，请重新选择三者险投保状态')
        else:
            raise ParameterError('请选择乘客险投保状态')
        #不计免赔险
        if iop_insurance=="yes":
            jdclbx_order.iop_insurance = True
        else:
            jdclbx_order.iop_insurance = False
        #自燃损失
        if autoignition_insurance=="yes":
            jdclbx_order.autoignition_insurance = True
        else:
            jdclbx_order.autoignition_insurance = False
        #涉水险
        if wading_insurance=="yes":
            jdclbx_order.wading_insurance = True
        else:
            jdclbx_order.wading_insurance = False
        #划痕险
        if scratch_insurance:
            try:
                scratch_insurance1 = float(scratch_insurance)
                scratch_insurance2 = int(scratch_insurance)
                if scratch_insurance2 < scratch_insurance1:
                    raise ParameterError('网络不稳定，获取划痕险状态错误，请重新选择划痕险状态。')
                else:
                    jdclbx_order.scratch_insurance = scratch_insurance2
            except:
                raise ParameterError('网络不稳定，获取划痕险状态错误，请重新选择划痕险投保状态')
        else:
            raise ParameterError('请选择划痕险投保状态')
        #交强险保险起期
        if liability_state=="yes":
            if liability_expectStartTime:
                now = datetime.now()
                otherStyleTime = now.strftime("%Y-%m-%d ")
#                 if otherStyleTime > liability_expectStartTime:
#                     raise ParameterError('交强险保险起期不能早于当前时间')
                jdclbx_order.liability_expectStartTime = liability_expectStartTime
            else:
                raise ParameterError('请选择交强险保险起期')
        #商业险保险起期
        if commercial_expectStartTime:
            now = datetime.now()
            otherStyleTime = now.strftime("%Y-%m-%d ")
#             if otherStyleTime > commercial_expectStartTime:
#                 raise ParameterError('商业险保险起期不能早于当前时间')
            jdclbx_order.commercial_expectStartTime = commercial_expectStartTime
        else:
            raise ParameterError('请选择商业险保险起期')
        #特别约定
        if special_agreement:
            if len(special_agreement)>150:
                raise ParameterError('请简短描述特别约定内容，包括标点一共不可超过150字')
            jdclbx_order.special_agreement = special_agreement
        else:
            jdclbx_order.special_agreement = ''

        return jdclbx_order
    
    #2017-09-12添加可修改支付成功的保单
    #   验证机动车保险订单详情
    def validation_jdclbx_detail(self, jdclbx_order):
        car_type = self.get_parameter('car_type').strip()       #车辆类型
        holder = self.get_parameter('holder').strip()       #所有人
        use_property = self.get_parameter('use_property').strip()       #车使用性质
        brand_digging = self.get_parameter('brand_digging').strip()       #品牌型号
        car_number = self.get_parameter('car_number').strip()       #车辆识别代码
        engine_number = self.get_parameter('engine_number').strip()       #发动机号
        issue_date = self.get_parameter('issue_date').strip()       #注册日期
        people_number = self.get_parameter('people_number').strip()       #核载人数(位)
        load_weight = self.get_parameter('load_weight').strip()       #核载质量(Kg)
        
        
        #车辆类型
        if car_type:
            jdclbx_order.car_type = car_type
        else:
            jdclbx_order.car_type =''
#              raise ParameterError('请选择车辆类型')
        #所有人
        if holder:
            jdclbx_order.holder = holder
        else:
            jdclbx_order.holder = ''
#             raise ParameterError('请输入所有人')
        #使用性质
        if use_property:
            jdclbx_order.use_property = use_property
        else:
            jdclbx_order.use_property = ''
#             raise ParameterError('请选择使用性质')
        #品牌型号
        if brand_digging:
            brand_digging = brand_digging.upper()
            jdclbx_order.brand_digging = brand_digging
        else:
            jdclbx_order.brand_digging = ''
#             raise ParameterError('请输入品牌型号')
        #车辆识别代码
        if car_number:
            car_number = car_number.replace(' ', '')
            test_answer=checkVIN(car_number)
            if test_answer == 'success':
                jdclbx_order.car_number = car_number
            else:
                raise ParameterError(test_answer)
        else:
            jdclbx_order.car_number =''
#             raise ParameterError('请输入车辆识别代码')
        #发动机号
        if engine_number:
            jdclbx_order.engine_number = engine_number
        else:
            jdclbx_order.car_number =''
#             raise ParameterError('请输入发动机号')
        #注册日期
        if issue_date:
            now = datetime.now()
            otherStyleTime = now.strftime("%Y-%m-%d ")
            if otherStyleTime < issue_date:
                raise ParameterError('车辆注册日期不能晚于当前时间')
            jdclbx_order.issue_date = issue_date
        else:
            pass
#             raise ParameterError('请输入车辆注册日期')
        #核载人数(位)
        if people_number:
            jdclbx_order.people_number = people_number
        else:
            jdclbx_order.people_number = ''
        #核载质量(Kg)
        if load_weight:
            jdclbx_order.load_weight = load_weight
        else:
            jdclbx_order.load_weight =''
#         if not people_number  and not load_weight:
#             raise ParameterError('请输入核载人数或核载质量')

        #录入投保人信息
        client_id = self.get_parameter('client_id').strip()       #投保使用账户
        user_classify = jdclbx_order.user_classify       #投保人身份选择
        #录入投保人信息--单位
        applicant_company_name = self.get_parameter('applicant_company_name').strip()       #单位名称
        organ_number = self.get_parameter('organ_number').strip()       #组织机构号(或营业执照号)
        #录入投保人信息--个人
        applicant_name = self.get_parameter('applicant_name').strip()       #投保人姓名
        certificate_number = self.get_parameter('certificate_number').strip()       #身份证号
        applicant_phone = self.get_parameter('applicant_phone').strip()       #投保人手机号
        #录入投保人信息--被保人
        insured_information = 'different'      #被保人身份信息选择，same同投保人，different手工录入
        #insured_name = self.get_parameter('insured_name').strip()       #被保人姓名
        insured_phone = self.get_parameter('insured_phone').strip()       #被保人手机号
        policy_address = self.get_parameter('policy_address').strip()       #保单邮寄地址
        startSiteName_prov = self.get_parameter('startSiteName_prov').strip()       #保单邮寄地址前部-省
        startSiteName_city = self.get_parameter('startSiteName_city').strip()       #保单邮寄地址前部-市
        startSiteName_dist = self.get_parameter('startSiteName_dist').strip()       #保单邮寄地址前部-区
        #2017/2/8添加字段
        insured_classify = jdclbx_order.insured_classify      #被保人身份选择
        insured_applicant_name = self.get_parameter('insured_applicant_name').strip()       #被保人姓名
        insured_certificate_number = self.get_parameter('insured_certificate_number').strip()       #身份证号
        insured_business_license_image = self.request.FILES.get('insured_business_license_image', '')     #营业执照
        insured_applicant_company_name = self.get_parameter('insured_applicant_company_name').strip()       #单位名称
        insured_organ_number = self.get_parameter('insured_organ_number').strip()       #组织机构号(或营业执照号)

         
        #投保人身份选择
        #单位
        if user_classify =='unit':
            jdclbx_order.user_classify = user_classify
            #单位名称
            if applicant_company_name:
                jdclbx_order.applicant_company_name = applicant_company_name
            else:
                jdclbx_order.applicant_company_name =''
#                 raise ParameterError('请输入单位名称')
            if organ_number:
                jdclbx_order.organ = organ_number
            else:
                jdclbx_order.organ = ''
#                 raise ParameterError('请输入组织机构代码或营业执照号')

        #个人
        elif user_classify == 'personal':
            jdclbx_order.user_classify = user_classify
            #投保人姓名
            if applicant_name:
                jdclbx_order.applicant_name = applicant_name
            else:
                jdclbx_order.applicant_name = ''
#                 raise ParameterError('请输入投保人姓名')
            #身份证号
            if certificate_number:
                test_idcard_number=checkIdcard(certificate_number)
                if test_idcard_number=='success':
                    jdclbx_order.certificate_number = certificate_number
                else:
                    raise ParameterError(test_idcard_number)
            else:
                jdclbx_order.certificate_number =''
#                 raise ParameterError('请输入投保人身份证号')
        else:
            raise ParameterError('请选择投保人身份，单位或个人')
        #投保人手机号
        if applicant_phone:
            if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', applicant_phone):
                raise ParameterError( '请输入正确的投保人手机号码')
            jdclbx_order.applicant_phone = applicant_phone
        else:
             raise ParameterError('请输入投保人手机号')
         #被保人身份信息选择
        if  insured_information =='different':
            #单位
            if insured_classify =='unit':
                jdclbx_order.insured_classify = insured_classify

                #单位名称
                if insured_applicant_company_name:
                    jdclbx_order.insured_name = insured_applicant_company_name
                else:
                    jdclbx_order.insured_name = ''
#                     raise ParameterError('请输入被保人单位名称')
                if insured_organ_number:
                    jdclbx_order.insured_number = insured_organ_number
                else:
                    jdclbx_order.insured_number =''
#                     raise ParameterError('请输入被保人组织机构代码或营业执照号')
            #个人
            elif insured_classify == 'personal':
                jdclbx_order.insured_classify = insured_classify

                #投保人姓名
                if insured_applicant_name:
                    jdclbx_order.insured_name = insured_applicant_name
                else:
                    jdclbx_order.insured_name =''
#                     raise ParameterError('请输入投保人姓名')
                #身份证号
                if insured_certificate_number:
                    test_idcard_number1=checkIdcard(insured_certificate_number)
                    if test_idcard_number1=='success':
                        jdclbx_order.insured_number = insured_certificate_number
                    else:
                        message1 = '被保人' + str(test_idcard_number1)
                        raise ParameterError(message1)
                    
                else:
                     jdclbx_order.insured_number =''
#                     raise ParameterError('请输入投保人身份证号')
            else:
                raise ParameterError('请选择被保人身份，单位或个人')
            if insured_phone:
                 if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', insured_phone):
                     raise ParameterError( '请输入正确的被投保人手机号码')
                 jdclbx_order.insured_phone = insured_phone
            else:
                 raise ParameterError('请输入被投保人手机号')
        else:
             raise ParameterError('请输入选择被保人信息录入方式')
         
        
        #2017/2/8添加新需求，北京部分订单无保单邮寄地址
        city_area=str(jdclbx_order.city.code)
        if city_area != '1101':
            #邮寄地址前缀
            startSiteName_prov = self.get_parameter('startSiteName_prov').strip()       #保单邮寄地址前部-省
            try:
                prov_set = CargoArea.objects(code =startSiteName_prov ).first()
                prov_name =str(prov_set.name)
            except:
                raise ParameterError('网络不稳定，为获取保单邮寄地址省份信息')
            
            startSiteName_city = self.get_parameter('startSiteName_city').strip()       #保单邮寄地址前部-市
            try:
                city_set = CargoArea.objects(code =startSiteName_city ).first()
                city_name =str(city_set.name)
            except:
                raise ParameterError('网络不稳定，为获取保单邮寄地址市级信息')
            
            startSiteName_dist = self.get_parameter('startSiteName_dist').strip()       #保单邮寄地址前部-区
            try:
                dist_set = CargoArea.objects(code =startSiteName_dist ).first()
                dist_name =str(dist_set.name)
            except:
                raise ParameterError('网络不稳定，为获取保单邮寄地址区级信息')
            
            if prov_name and city_name and dist_name:
                mail_address = str(prov_name)+ ' ' + str(city_name) +' ' +str(dist_name)
                jdclbx_order.mail_address =mail_address
            else:
                raise ParameterError('网络不稳定，为获取保单邮寄地址省市区三级全部信息')
            
            #保单邮寄地址
            if policy_address:
                 jdclbx_order.policy_address = policy_address
            else:
                 raise ParameterError('请输入保单邮寄地址')
        else:
            jdclbx_order.mail_address =''
            jdclbx_order.policy_address = ''

        return jdclbx_order
    
#已经弃用（第二版）
#验证中介下保险公司的费率
    def validation_intermediary_rate(self, intermediary_rate_set):
        add_company_id= self.get_parameter("add_company_id").strip()
        liability_process_price= self.get_parameter("liability_process_price").strip()
        commercial_process_price= self.get_parameter("commercial_process_price").strip()
        if not add_company_id:
            raise ParameterError('网络延迟，公司信息获取失败，请稍后再试。')
        if not liability_process_price:
            raise ParameterError('请输入交强险手续费比例')
        if not commercial_process_price:
            raise ParameterError('请输入商业险手续费比例')
        
        try:
            add_company_set = InsuranceCompany.objects(id=add_company_id).first()
        except:
            raise ParameterError('网络延迟，公司信息获取失败，请稍后再试')
        
        if not add_company_set:
            raise ParameterError('网络延迟，公司信息获取失败，请稍后再试。')
        else:
             intermediary_rate_set.company=add_company_set
        
        #验证交强险手续费比例
        try:
            liability_process_price1 = float(liability_process_price) 
        except:
           raise ParameterError('交强险手续费为数字，最多保护两位小数。如：20.55%，请输入20.55') 
        if liability_process_price1>=100:
           raise ParameterError('交强险手续费应小于100%')
        liability_process_price2 = round(liability_process_price1,2)#保留两位小数
        if liability_process_price1>liability_process_price2:
           raise ParameterError('交强险手续费为数字，最多保护两位小数。如：20.55%，请输入20.55。') 
        intermediary_rate_set.liability_process_price=liability_process_price1
        
        #验证商业险手续费比例
        try:
            commercial_process_price1 = float(commercial_process_price) 
        except:
           raise ParameterError('商业险手续费为数字，最多保护两位小数。如：20.55%，请输入20.55') 
        if commercial_process_price1>=100:
           raise ParameterError('商业险手续费应小于100%')
        commercial_process_price2 = round(commercial_process_price1,2)#保留两位小数
        if commercial_process_price1>commercial_process_price2:
           raise ParameterError('商业险手续费为数字，最多保护两位小数。如：20.55%，请输入20.55。') 
        intermediary_rate_set.commercial_process_price=commercial_process_price1
        return intermediary_rate_set    
    
    
    #   2017验证添加用户信息
    def validation_certificate_new(self, certificate):
        national_image = self.request.FILES.get('national_image', '')
        if national_image:
            image_tool = ImageTools()
            national_image_url = image_tool.save(request_file=national_image, file_folder=ImageFolderType.user, old_file='')
            if national_image_url:
                certificate.national_image = national_image_url
            else:
                raise ParameterError('保存身份证正面图片失败')
#         else:
#             raise ParameterError('请选择添加身份证正面图片')

        national_image_down = self.request.FILES.get('national_image_down', '')
        if national_image_down:
            image_tool = ImageTools()
            national_image_down_url = image_tool.save(request_file=national_image_down, file_folder=ImageFolderType.user, old_file='')
            if national_image_down_url:
                certificate.national_image_down = national_image_down_url
            else:
                raise ParameterError('保存身份证背面图片失败')
#         else:
#             raise ParameterError('请选择添加身份证背面图片')

        user_type = self.get_parameter("user_type").strip()
        if user_type:
            certificate.user_type = user_type
        else:
            certificate.user_type = 'registered'

        user_classify = self.get_parameter("user_classify").strip()
        if user_classify:
            certificate.user_classify = user_classify
        else:
            certificate.user_classify = ''

        if user_type == 'transport':
            business_license_image = self.request.FILES.get('business_license_image', '')
            if business_license_image:
                image_tool = ImageTools()
                business_license_image_url = image_tool.save(request_file=business_license_image, file_folder=ImageFolderType.user, old_file='')
                if business_license_image_url:
                    certificate.business_license_image = business_license_image_url
                else:
                    raise ParameterError('保存营业执照正本图片失败')
#             else:
#                 raise ParameterError('请选择添加营业执照正本图片')

            organ_image = self.request.FILES.get('organ_image', '')
            if organ_image:
                image_tool = ImageTools()
                organ_image_url = image_tool.save(request_file=organ_image, file_folder=ImageFolderType.user, old_file='')
                if organ_image_url:
                    certificate.organ_image = organ_image_url
                else:
                    raise ParameterError('保存组织机构代码证失败')
 
            operating_permit_image = self.request.FILES.get('operating_permit_image', '')
            if operating_permit_image:
                image_tool = ImageTools()
                operating_permit_image_url = image_tool.save(request_file=operating_permit_image, file_folder=ImageFolderType.user, old_file='')
                if operating_permit_image_url:
                    certificate.operating_permit_image = operating_permit_image_url
                else:
                    raise ParameterError('保存道路运输经营许可证失败')
#             else:
#                 raise ParameterError('请选择添加道路运输经营许可证')

        elif user_type == 'driver':
            driver_image = self.request.FILES.get('driver_image', '')
            if driver_image:
                image_tool = ImageTools()
                driver_image_url = image_tool.save(request_file=driver_image, file_folder=ImageFolderType.user, old_file='')
                if driver_image_url:
                    certificate.driver_image = driver_image_url
                else:
                    raise ParameterError('保存驾驶证失败')
#             else:
#                 raise ParameterError('请选择添加驾驶证')

            plate_image = self.request.FILES.get('plate_image', '')
            if plate_image:
                image_tool = ImageTools()
                plate_image_url = image_tool.save(request_file=plate_image, file_folder=ImageFolderType.user, old_file='')
                if plate_image_url:
                    certificate.plate_image = plate_image_url
                else:
                    raise ParameterError('保存行驶证失败')
#             else:
#                 raise ParameterError('请选择添加行驶证')

            transportation_image = self.request.FILES.get('transportation_image', '')
            if transportation_image:
                image_tool = ImageTools()
                transportation_image_url = image_tool.save(request_file=transportation_image, file_folder=ImageFolderType.user, old_file='')
                if transportation_image_url:
                    certificate.transportation_image = transportation_image_url
                else:
                    raise ParameterError('保存营运证失败')
#             else:
#                 raise ParameterError('请选择添加营运证')
        elif user_type == 'boss':
            if user_classify == 'units':
                business_license_image_boss = self.request.FILES.get('business_license_image_boss', '')
                if business_license_image_boss:
                    image_tool = ImageTools()
                    business_license_image_boss_url = image_tool.save(request_file=business_license_image_boss, file_folder=ImageFolderType.user, old_file='')
                    if business_license_image_boss_url:
                        certificate.business_license_image = business_license_image_boss_url
                    else:
                        raise ParameterError('保存营业执照图片失败')
#                 else:
#                     raise ParameterError('请选择添加营业执照图片')

                organ_image = self.request.FILES.get('organ_image_boss', '')
                if organ_image:
                    image_tool = ImageTools()
                    organ_image_url = image_tool.save(request_file=organ_image, file_folder=ImageFolderType.user, old_file='')
                    if organ_image_url:
                        certificate.organ_image = organ_image_url
                    else:
                        raise ParameterError('保存组织机构代码证失败')
        elif user_type == 'owner':
            print("申请车主认证")
        elif user_type == '':
            print("注册用户认证")
        else:
            raise ParameterError('认证类型不正确')
        return certificate
    
    #   2017验证完善用户信息
    def validation_part_imformation(self, certificate):
        try:
            result = self.request.GET.get('type', '')
            if not result:
                raise ParameterError('网络问题，未获取到补充信息参数.')
        except:
            raise ParameterError('网络问题，未获取到补充信息参数')
        if result == 'national':
            national_id = self.get_parameter("modal_national_id").strip()  
            certificate.national_id = national_id
            national_name = self.request.POST.get('modal_national_name', '')
            certificate.name = national_name
            try:
                national_effective_time = self.request.POST.get('modal_national_effective', '')
                if national_effective_time:
                    now = datetime.now()
                    otherStyleTime = now.strftime("%Y-%m-%d ")
                    if otherStyleTime > national_effective_time:
                        raise ParameterError ( '身份证有效时间不能早于当前时间')
                    certificate.national_effective_time = national_effective_time
            except Exception as e:
                message= str(e)
                raise ParameterError ( '身份证有效时间格式不正确,例：2015-09-09')
        elif result == 'business':
            business_id = self.request.POST.get('modal_business_id', '')
            certificate.business_license_id = business_id
            business_name = self.request.POST.get('modal_business_name', '')
            certificate.company_name = business_name
        elif result == 'organ':
            organ_id = self.request.POST.get('modal_organ_id', '')
            certificate.organ = organ_id
        elif result == 'operating':
            operating_id = self.request.POST.get('modal_operating_id', '')
            certificate.operating_permit_id = operating_id
        elif result == 'driver':
            driver_id = self.request.POST.get('modal_driver_id', '')
            certificate.driver_id = driver_id
        elif result == 'transportation':
            transportation_id = self.request.POST.get('modal_transportation_id', '')
            certificate.transportation_license_id = transportation_id
        elif result == 'plate':
            plate_number = self.get_parameter('plate_number').strip()
            short = self.get_parameter('short_number').strip()
            mid = self.get_parameter('mid_number').strip()
            if plate_number:
                if not short or not mid:
                    raise ParameterError('请选择车牌号前两位。如“黑A')
                if re.match(r'^[a-z_A-Z_0-9]{5}$', plate_number):
                     plate_number = plate_number.upper()
                     plate_number1 = short+" " +mid +" "+plate_number
                     certificate.plate_number =  plate_number1
                else:
                    raise ParameterError('您输入的车牌号不正确，请输入由英文或数字组成的五位字符串')
            car_type = self.request.POST.get('modal_car_type', '')
            certificate.car_type = car_type
            certificate.client.car_type =car_type
            holder = self.request.POST.get('modal_holder', '')
            certificate.holder = holder
            use_property = self.request.POST.get('modal_use_property', '')
            certificate.client.use_property =use_property
            certificate.use_property = use_property
            brand_digging = self.request.POST.get('modal_brand_digging', '')
            certificate.brand_digging = brand_digging
            engine_number = self.request.POST.get('modal_engine_number', '')
            certificate.engine_number = engine_number
            issue_date =self.request.POST.get('modal_issue_date', '')
            if issue_date:
                now = datetime.datetime.now()
                otherStyleTime = now.strftime("%Y-%m-%d ")
                if otherStyleTime < issue_date:
                    raise ParameterError('车辆发证日期不能晚于当前时间')
                certificate.issue_date = issue_date
            
        else:
            raise ParameterError('网络问题，补充信息类型错误.')
        try:
            certificate.client.save()
        except Exception as e:
            raise ParameterError('网络问题，同步信息出错.'+str(e))
#         type = self.get_parameter("type").strip()
        return certificate
    
    #2017/12/04添加员工保险验证
    def validation_create_employee(self, employee):
        #添加状态
        employee_state = self.get_parameter('employee_state').strip()
        #用户
        client_id = self.get_parameter('client_id').strip()
        if client_id:
            client = Client.objects(id=client_id).first()
            if client:
                employee.client = client
            else:
                raise ParameterError('用户不存在')
        else:
            raise ParameterError('用户不能为空')
        #保单号
        paper_id = self.get_parameter('paper_id').strip()
        if not paper_id:
            raise ParameterError('保单号不能为空')
        else:
            if len(paper_id) >100:
                raise ParameterError('保单号不能超过100个字符')
            employee.paper_id = str(paper_id)
        
        #承保公司
        tail_company_id = self.get_parameter('tail_company_id').strip()
        if tail_company_id:
            company = InsuranceCompany.objects(id=tail_company_id).first()
            if company:
                employee.company = company
            else:
                raise ParameterError("您选择的保险公司不存在")
        else:
             raise ParameterError("您未选择保险公司")
         
        #险种
        insurance_type = self.get_parameter('insurance_type').strip()
        if not insurance_type:
            raise ParameterError('请选择险种')
        employee.insurance_type = str(insurance_type)
        
        #死亡伤残保险金额
        death_disability_price = self.get_parameter('death_disability_price').strip()
        if not death_disability_price:
            raise ParameterError('请输入死亡伤残保险金额')
        else:
            if len(death_disability_price) >100:
                raise ParameterError('保单号不能超过100个字符')
            employee.death_disability_price = str(death_disability_price)
        
        #医疗费保险金额
        medical_price = self.get_parameter('medical_price').strip()
        if not medical_price:
            raise ParameterError('医疗费保险金额不能为空')
        else:
            if len(medical_price) >100:
                raise ParameterError('保单号不能超过100个字符')
            employee.medical_price = str(medical_price)
        
        #误工费保险金额
        loss_working_price = self.get_parameter('loss_working_price').strip()
        if not loss_working_price:
            raise ParameterError('误工费保险金额不能为空')
        else:
            if len(loss_working_price) >100:
                raise ParameterError('误工费保险金额不能超过100个字符')
            employee.loss_working_price = str(loss_working_price)
            
        #住院津贴保险金额
        hospitalization_price = self.get_parameter('hospitalization_price').strip()
        if not hospitalization_price:
            raise ParameterError('住院津贴保险金额不能为空')
        else:
            if len(hospitalization_price) >100:
                raise ParameterError('住院津贴保险金额不能超过100个字符')
            employee.hospitalization_price = str(hospitalization_price)
            
        #免赔
        deductible = self.get_parameter('deductible').strip()
        if not deductible:
            raise ParameterError('免赔不能为空')
        else:
            if len(deductible) >100:
                raise ParameterError('免赔不能超过100个字符')
            employee.deductible = str(deductible)
            
        #上传保单方式
        insurance_type = self.get_parameter('up_state').strip()
        if not insurance_type:
            raise ParameterError('请选择保单上传方式')
        else:
            if insurance_type not in ['picture' , 'web_url' , 'pdf']:
                raise ParameterError('请选择正确保单上传方式')
#             else:
#                 employee.up_state = str(insurance_type)
        #上传保单内容
        insurance_image_list=""
        try:
            if insurance_type == 'web_url':
                insurance_image_list = self.request.POST.get('insurance_image', '')
            else:
                insurance_image_list = self.request.FILES.getlist('insurance_image', '')
        except Exception as e:
            raise ParameterError("提取保单信息出错："+str(e))
        
        if not insurance_image_list:
                if employee_state == "create" :
                    raise ParameterError("请补充保单文件")
                elif employee_state == "edit" and  insurance_type != employee.up_state:
                    raise ParameterError("请补充保单文件")
                else:
                    pass
        else:
            employee.up_state = str(insurance_type)
            employee.insurance_image_list=[]
             #保单图片
            if insurance_type == 'picture':
                try:
                    image_tool = ImageTools()
                    if insurance_image_list:
                        for insurance_image in insurance_image_list:
                            order_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
                            if not order_image_url:
                                raise ParameterError("生成保单图片地址失败")
                            else:
                                employee.insurance_image_list.append(order_image_url)
                except ParameterError as e:
                    # 初始化错误信息
                    raise ParameterError("图片上传失败"+str(e))
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
                                raise ParameterError(str(e)+'保单文件上传失败')
                            liability_document_url.append(file_url)
                        if not liability_document_url:
                            raise ParameterError('生成保单文件地址失败')
                        else:
                            employee.insurance_image_list=liability_document_url
            elif insurance_type == 'web_url':
                    if insurance_image_list:
                        insurance_web_url = []
                        insurance_image_list = str(insurance_image_list)
                        insurance_web_url.append(insurance_image_list)
                        employee.insurance_image_list = insurance_web_url
        #其他部分          
        position_list = self.request.POST.getlist('position')
        employee.other_list =[]
        if len(position_list) > 0:
            try:
                test1=position_list[0]
                mc1 = self.request.POST.get("mc_" + test1)
                nr1 = self.request.POST.get("nr_" + test1)
            except Exception as e:
                raise ParameterError('网络延迟，请检查补充信息部分'+str(e))
            if len(position_list) == 1  and mc1=="" and nr1=="":
                pass
            else:
                for position in position_list:
                    try:
                        mc = self.request.POST.get("mc_" + position)
                        nr = self.request.POST.get("nr_" + position)
                        others = OtherList()
                        if mc:
                            others.field_name = mc
                        else:
                            raise ParameterError('添加的字段名称不能为空')
                        if nr:
                            others.field_content = nr
                        else:
                            raise ParameterError('添加的字段内容不能为空')
                        employee.other_list.append(others)
                    except ParameterError as e:
                        raise ParameterError(str(e))
                    except Exception as e:
                        pass
                    
        #保单开始日期
        date_start = self.get_parameter('date_start').strip()    
        if date_start:
            try:
                date_start=date_start  +" 00:00:00"
                date_start= datetime.strptime(date_start,"%Y-%m-%d %H:%M:%S")
                employee.date_start=date_start
            except:
                pass
        else:
            raise ParameterError('请添加员工保单开始日期')
        
        #保单结束日期
        date_stop = self.get_parameter('date_stop').strip()    
        if date_stop:
            try:
                date_stop=date_stop  +" 00:00:00"
                date_stop= datetime.strptime(date_stop,"%Y-%m-%d %H:%M:%S")
                employee.date_stop=date_stop
            except:
                pass
        else:
            raise ParameterError('请添加员工保单截止日期')
        
        if date_stop<date_start:
            raise ParameterError('员工保单截止日期不能早与开始日期')
        
        #上传人员名单方式
        up_roster = self.get_parameter('up_roster').strip()
        if not up_roster:
            raise ParameterError('请选择上传人员名单方式')
        else:
            if up_roster not in ['picture' , 'manual' , 'pdf']:
                raise ParameterError('请选择正确人员名单方式')
            
        #上传人员名单图片和PDF
        if  up_roster == 'picture' or up_roster == 'pdf' :
            roster_image_list=""
            try:
                roster_image_list = self.request.FILES.getlist('roster_image', '')
            except Exception as e:
                raise ParameterError("提取员工名单文件信息出错："+str(e))
        
            if not roster_image_list:
                    if employee_state == "create" :
                        raise ParameterError("请补充员工名单文件")
                    elif employee_state == "edit" and  up_roster != employee.up_roster:
                        raise ParameterError("请补充员工名单文件")
                    else:
                        pass
            else:
                employee.up_roster = str(up_roster)
                employee.roster_list =[]
                employee.roster_list_manual =[]
                
            #上传图片
            if up_roster == 'picture'  :
                try:
                    image_tool = ImageTools()
                    if roster_image_list:
                        for roster_image in roster_image_list:
                            roster_image_url = image_tool.save(request_file=roster_image, file_folder=ImageFolderType.insurance, old_file='')
                            if not roster_image_url:
                                raise ParameterError("生成保单图片地址失败")
                            else:
                                employee.roster_list.append(roster_image_url)
                except ParameterError as e:
                    # 初始化错误信息
                    raise ParameterError("图片上传失败"+str(e))
            #上传pdf
            if  up_roster == 'pdf' :
                if roster_image_list:
                        roster_document_url=[]
                        for roster_image  in roster_image_list:
                            document_tools = DocumentTools()
                            try:
                                file_url = document_tools.save(request_file=roster_image, file_folder=DocumentFolderType.order, old_file='')
                            except Exception as e:
                                raise ParameterError(str(e)+'人员名单文件上传失败')
                            roster_document_url.append(file_url)
                        if not roster_document_url:
                            raise ParameterError('生成人员名单地址失败')
                        else:
                            employee.roster_list=roster_document_url
        #手动输入员工名单
        else:
            roster_position_list = self.request.POST.getlist('roster_position')
            employee.roster_list_manual =[]
            if len(roster_position_list) > 0:
                try:
                    test1=roster_position_list[0]
                    gz1 = self.request.POST.get("gz_" + test1)
                    xm1 = self.request.POST.get("xm_" + test1)
                    sfz1 = self.request.POST.get("sfz_" + test1)
                except Exception as e:
                    raise ParameterError('网络延迟，请检查补充信息部分'+str(e))
          
                for position in roster_position_list:
                    try:
                        gz = self.request.POST.get("gz_" + position)
                        xm = self.request.POST.get("xm_" + position)
                        sfz = self.request.POST.get("sfz_" + position)
                        rosterlist = RosterList()
                        if gz and xm and sfz :
                            rosterlist.work_type = str(gz)
                            rosterlist.name = str(xm)
                            rosterlist.id_number = str(sfz)
                        else:
                            raise ParameterError('添加员工名单中的字段内容不能为空')
                        employee.roster_list_manual.append(rosterlist)
                    except ParameterError as e:
                        raise ParameterError(str(e))
                    except Exception as e:
                        raise ParameterError(str(e))
            else:
                raise ParameterError('请添加人员名单')
        
        
        
        
        
        
        
        #保险显示状态           
        active = self.get_parameter('active').strip()          
        if active == 'show':
            employee.is_hidden = False
        else:
            employee.is_hidden = True
        
        return employee
    

    #2017/12/04添加货运年险保险验证
    def validation_create_freight(self, freight):
        #添加状态
        freight_state = self.get_parameter('freight_state').strip()
        #用户
        client_id = self.get_parameter('client_id').strip()
        if client_id:
            client = Client.objects(id=client_id).first()
            if client:
                freight.client = client
            else:
                raise ParameterError('用户不存在')
        else:
            raise ParameterError('用户不能为空')
        #保单号
        paper_id = self.get_parameter('paper_id').strip()
        if not paper_id:
            raise ParameterError('保单号不能为空')
        else:
            if len(paper_id) >100:
                raise ParameterError('保单号不能超过100个字符')
            freight.paper_id = str(paper_id)
        
        #承保公司
        tail_company_id = self.get_parameter('tail_company_id').strip()
        if tail_company_id:
            company = InsuranceCompany.objects(id=tail_company_id).first()
            if company:
                freight.company = company
            else:
                raise ParameterError("您选择的保险公司不存在")
        else:
             raise ParameterError("您未选择保险公司")
         
        #险种
        insurance_type = self.get_parameter('insurance_type').strip()
        if not insurance_type:
            raise ParameterError('请选择险种')
        freight.insurance_type = str(insurance_type)
        
        #单车保险金额
        single_vehicle_price = self.get_parameter('single_vehicle_price').strip()
        if not single_vehicle_price:
            raise ParameterError('请输入单车保险金额')
        else:
            if len(single_vehicle_price) >100:
                raise ParameterError('单车保险金额不能超过100个字符')
            freight.single_vehicle_price = str(single_vehicle_price)
            
        #免赔
        deductible = self.get_parameter('deductible').strip()
        if not deductible:
            raise ParameterError('免赔不能为空')
        else:
            if len(deductible) >100:
                raise ParameterError('免赔不能超过100个字符')
            freight.deductible = str(deductible)
            
        #保费
        insurance_price = self.get_parameter('insurance_price').strip()
        if not insurance_price:
            raise ParameterError('请输入保费金额')
        else:
            if len(insurance_price) >100:
                raise ParameterError('保费金额不能超过100个字符')
            freight.insurance_price = str(insurance_price)
            
        #上传保单方式
        insurance_type = self.get_parameter('up_state').strip()
        if not insurance_type:
            raise ParameterError('请选择保单上传方式')
        else:
            if insurance_type not in ['picture' , 'web_url' , 'pdf']:
                raise ParameterError('请选择正确保单上传方式')
#             else:
#                 freight.up_state = str(insurance_type)
        #上传保单内容
        insurance_image_list=""
        try:
            if insurance_type == 'web_url':
                insurance_image_list = self.request.POST.get('insurance_image', '')
            else:
                insurance_image_list = self.request.FILES.getlist('insurance_image', '')
        except Exception as e:
            raise ParameterError("提取保单信息出错："+str(e))
        
        if not insurance_image_list:
                if freight_state == "create" :
                    raise ParameterError("请补充保单文件")
                elif freight_state == "edit" and  insurance_type != freight.up_state:
                    raise ParameterError("请补充保单文件")
                else:
                    pass
        else:
            freight.up_state = str(insurance_type)
            freight.insurance_image_list=[]
             #保单图片
            if insurance_type == 'picture':
                try:
                    image_tool = ImageTools()
                    if insurance_image_list:
                        for insurance_image in insurance_image_list:
                            order_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
                            if not order_image_url:
                                raise ParameterError("生成保单图片地址失败")
                            else:
                                freight.insurance_image_list.append(order_image_url)
                except ParameterError as e:
                    # 初始化错误信息
                    raise ParameterError("图片上传失败"+str(e))
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
                                raise ParameterError(str(e)+'保单文件上传失败')
                            liability_document_url.append(file_url)
                        if not liability_document_url:
                            raise ParameterError('生成保单文件地址失败')
                        else:
                            freight.insurance_image_list=liability_document_url
            elif insurance_type == 'web_url':
                    if insurance_image_list:
                        insurance_web_url = []
                        insurance_image_list = str(insurance_image_list)
                        insurance_web_url.append(insurance_image_list)
                        freight.insurance_image_list = insurance_web_url
         #保险显示状态           
        active = self.get_parameter('active').strip()          
        if active == 'show':
            freight.is_hidden = False
        else:
            freight.is_hidden = True
        
        #其他部分          
        position_list = self.request.POST.getlist('position')
        freight.other_list =[]
        if len(position_list) > 0:
            try:
                test1=position_list[0]
                mc1 = self.request.POST.get("mc_" + test1)
                nr1 = self.request.POST.get("nr_" + test1)
            except Exception as e:
                raise ParameterError('网络延迟，请检查补充信息部分'+str(e))
            if len(position_list) == 1  and mc1=="" and nr1=="":
                pass
            else:
                for position in position_list:
                    try:
                        mc = self.request.POST.get("mc_" + position)
                        nr = self.request.POST.get("nr_" + position)
                        others = OtherList()
                        if mc:
                            others.field_name = mc
                        else:
                            raise ParameterError('添加的字段名称不能为空')
                        if nr:
                            others.field_content = nr
                        else:
                            raise ParameterError('添加的字段内容不能为空')
                        freight.other_list.append(others)
                    except ParameterError as e:
                        raise ParameterError(str(e))
                    except Exception as e:
                        pass
                    
        #保单开始日期
        date_start = self.get_parameter('date_start').strip()    
        if date_start:
            try:
                date_start=date_start  +" 00:00:00"
                date_start= datetime.strptime(date_start,"%Y-%m-%d %H:%M:%S")
                freight.date_start=date_start
            except:
                pass
        else:
            raise ParameterError('请添加保单开始日期')
        
        #保单结束日期
        date_stop = self.get_parameter('date_stop').strip()    
        if date_stop:
            try:
                date_stop=date_stop  +" 00:00:00"
                date_stop= datetime.strptime(date_stop,"%Y-%m-%d %H:%M:%S")
                freight.date_stop=date_stop
            except:
                pass
        else:
            raise ParameterError('请添加保单截止日期')
        
        if date_stop<date_start:
            raise ParameterError('保单截止日期不能早与开始日期')
        
        return freight

    #2017/12/06添加个人保险验证
    def validation_create_personal(self, personal):
        #添加状态
        personal_state = self.get_parameter('personal_state').strip()
        #用户
        client_id = self.get_parameter('client_id').strip()
        if client_id:
            client = Client.objects(id=client_id).first()
            if client:
                personal.client = client
            else:
                raise ParameterError('用户不存在')
        else:
            raise ParameterError('用户不能为空')
        #保单号
        paper_id = self.get_parameter('paper_id').strip()
        if not paper_id:
            raise ParameterError('保单号不能为空')
        else:
            if len(paper_id) >100:
                raise ParameterError('保单号不能超过100个字符')
            personal.paper_id = str(paper_id)
        
        #承保公司
        tail_company_id = self.get_parameter('tail_company_id').strip()
        if tail_company_id:
            company = InsuranceCompany.objects(id=tail_company_id).first()
            if company:
                personal.company = company
            else:
                raise ParameterError("您选择的保险公司不存在")
        else:
             raise ParameterError("您未选择保险公司")
         
        #险种
        insurance_type = self.get_parameter('insurance_type').strip()
        if not insurance_type:
            raise ParameterError('请选择险种')
        personal.insurance_type = str(insurance_type)

         #保险显示状态           
        active = self.get_parameter('active').strip()          
        if active == 'show':
            personal.is_hidden = False
        else:
            personal.is_hidden = True
            
     #上传保单方式
        insurance_type = self.get_parameter('up_state').strip()
        if not insurance_type:
            raise ParameterError('请选择保单上传方式')
        else:
            if insurance_type not in ['picture' , 'web_url' , 'pdf']:
                raise ParameterError('请选择正确保单上传方式')
#             else:
#                 freight.up_state = str(insurance_type)
        #上传保单内容
        insurance_image_list=""
        try:
            if insurance_type == 'web_url':
                insurance_image_list = self.request.POST.get('insurance_image', '')
            else:
                insurance_image_list = self.request.FILES.getlist('insurance_image', '')
        except Exception as e:
            raise ParameterError("提取保单信息出错："+str(e))
        
        if not insurance_image_list:
                if personal_state == "create" :
                    raise ParameterError("请补充保单文件")
                elif personal_state == "edit" and  insurance_type != personal.up_state:
                    raise ParameterError("请补充保单文件")
                else:
                    pass
        else:
            personal.up_state = str(insurance_type)
            personal.insurance_image_list=[]
             #保单图片
            if insurance_type == 'picture':
                try:
                    image_tool = ImageTools()
                    if insurance_image_list:
                        for insurance_image in insurance_image_list:
                            order_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
                            if not order_image_url:
                                raise ParameterError("生成保单图片地址失败")
                            else:
                                personal.insurance_image_list.append(order_image_url)
                except ParameterError as e:
                    # 初始化错误信息
                    raise ParameterError("图片上传失败"+str(e))
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
                                raise ParameterError(str(e)+'保单文件上传失败')
                            liability_document_url.append(file_url)
                        if not liability_document_url:
                            raise ParameterError('生成保单文件地址失败')
                        else:
                            personal.insurance_image_list=liability_document_url
            elif insurance_type == 'web_url':
                    if insurance_image_list:
                        insurance_web_url = []
                        insurance_image_list = str(insurance_image_list)
                        insurance_web_url.append(insurance_image_list)
                        personal.insurance_image_list = insurance_web_url   
            
        
        #其他部分          
        position_list = self.request.POST.getlist('position')
        personal.other_list =[]
        if len(position_list) > 0:
            try:
                test1=position_list[0]
                mc1 = self.request.POST.get("mc_" + test1)
                nr1 = self.request.POST.get("nr_" + test1)
            except Exception as e:
                raise ParameterError('网络延迟，请检查补充信息部分'+str(e))
            if len(position_list) == 1  and mc1=="" and nr1=="":
                pass
            else:
                for position in position_list:
                    try:
                        mc = self.request.POST.get("mc_" + position)
                        nr = self.request.POST.get("nr_" + position)
                        others = OtherList()
                        if mc:
                            others.field_name = mc
                        else:
                            raise ParameterError('添加的字段名称不能为空')
                        if nr:
                            others.field_content = nr
                        else:
                            raise ParameterError('添加的字段内容不能为空')
                        personal.other_list.append(others)
                    except ParameterError as e:
                        raise ParameterError(str(e))
                    except Exception as e:
                        pass
                    
        #保单开始日期
        date_start = self.get_parameter('date_start').strip()    
        if date_start:
            try:
                date_start=date_start  +" 00:00:00"
                date_start= datetime.strptime(date_start,"%Y-%m-%d %H:%M:%S")
                personal.date_start=date_start
            except:
                pass
        else:
            raise ParameterError('请添加保单开始日期')
        
        #保单结束日期
        date_stop = self.get_parameter('date_stop').strip()    
        if date_stop:
            try:
                date_stop=date_stop  +" 00:00:00"
                date_stop= datetime.strptime(date_stop,"%Y-%m-%d %H:%M:%S")
                personal.date_stop=date_stop
            except:
                pass
        else:
            raise ParameterError('请添加保单截止日期')
        
        if date_stop<date_start:
            raise ParameterError('保单截止日期不能早与开始日期')
        
        return personal
    
    #2017/12/013添加其他保险验证
    def validation_create_other_insurance(self, other_insurance):
        #添加状态
        other_insurance_state = self.get_parameter('other_insurance_state').strip()
        #用户
        client_id = self.get_parameter('client_id').strip()
        if client_id:
            client = Client.objects(id=client_id).first()
            if client:
                other_insurance.client = client
            else:
                raise ParameterError('用户不存在')
        else:
            raise ParameterError('用户不能为空')
        
        #承保公司
        tail_company_id = self.get_parameter('tail_company_id').strip()
        if tail_company_id:
            company = InsuranceCompany.objects(id=tail_company_id).first()
            if company:
                other_insurance.company = company
            else:
                raise ParameterError("您选择的保险公司不存在")
        else:
             other_insurance.company = None
  

         #保险显示状态           
        active = self.get_parameter('active').strip()          
        if active == 'show':
            other_insurance.is_hidden = False
        else:
            other_insurance.is_hidden = True
            
     #上传保单方式
        insurance_type = self.get_parameter('up_state').strip()
        if not insurance_type:
            raise ParameterError('请选择保单上传方式')
        else:
            if insurance_type not in ['picture' , 'web_url' , 'pdf']:
                raise ParameterError('请选择正确保单上传方式')
#             else:
#                 freight.up_state = str(insurance_type)
        #上传保单内容
        insurance_image_list=""
        try:
            if insurance_type == 'web_url':
                insurance_image_list = self.request.POST.get('insurance_image', '')
            else:
                insurance_image_list = self.request.FILES.getlist('insurance_image', '')
        except Exception as e:
            raise ParameterError("提取保单信息出错："+str(e))
        
        if not insurance_image_list:
                if other_insurance_state == "create" :
                    raise ParameterError("请补充保单文件")
                elif other_insurance_state == "edit" and  insurance_type != other_insurance.up_state:
                    raise ParameterError("请补充保单文件")
                else:
                    pass
        else:
            other_insurance.up_state = str(insurance_type)
            other_insurance.insurance_image_list=[]
             #保单图片
            if insurance_type == 'picture':
                try:
                    image_tool = ImageTools()
                    if insurance_image_list:
                        for insurance_image in insurance_image_list:
                            order_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
                            if not order_image_url:
                                raise ParameterError("生成保单图片地址失败")
                            else:
                                other_insurance.insurance_image_list.append(order_image_url)
                except ParameterError as e:
                    # 初始化错误信息
                    raise ParameterError("图片上传失败"+str(e))
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
                                raise ParameterError(str(e)+'保单文件上传失败')
                            liability_document_url.append(file_url)
                        if not liability_document_url:
                            raise ParameterError('生成保单文件地址失败')
                        else:
                            other_insurance.insurance_image_list=liability_document_url
            elif insurance_type == 'web_url':
                    if insurance_image_list:
                        insurance_web_url = []
                        insurance_image_list = str(insurance_image_list)
                        insurance_web_url.append(insurance_image_list)
                        other_insurance.insurance_image_list = insurance_web_url   
            
        
        #其他部分          
        position_list = self.request.POST.getlist('position')
        other_insurance.other_list =[]
        if len(position_list) > 0:
            try:
                test1=position_list[0]
                mc1 = self.request.POST.get("mc_" + test1)
                nr1 = self.request.POST.get("nr_" + test1)
            except Exception as e:
                raise ParameterError('网络延迟，请检查补充信息部分'+str(e))
            if len(position_list) == 1  and mc1=="" and nr1=="":
                raise ParameterError('其他保险中自定义字段不能为空。')
            else:
                for position in position_list:
                    try:
                        mc = self.request.POST.get("mc_" + position)
                        nr = self.request.POST.get("nr_" + position)
                        others = OtherList()
                        if mc:
                            others.field_name = mc
                        else:
                            raise ParameterError('添加的字段名称不能为空')
                        if nr:
                            others.field_content = nr
                        else:
                            raise ParameterError('添加的字段内容不能为空')
                        other_insurance.other_list.append(others)
                    except ParameterError as e:
                        raise ParameterError(str(e))
                    except Exception as e:
                        pass
        else:
            raise ParameterError('其他保险中自定义字段不能为空')
        #保单开始日期
        date_start = self.get_parameter('date_start').strip()    
        if date_start:
            try:
                date_start=date_start  +" 00:00:00"
                date_start= datetime.strptime(date_start,"%Y-%m-%d %H:%M:%S")
                other_insurance.date_start=date_start
            except:
                pass
        else:
            raise ParameterError('请添加保单开始日期')
        
        #保单结束日期
        date_stop = self.get_parameter('date_stop').strip()    
        if date_stop:
            try:
                date_stop=date_stop  +" 00:00:00"
                date_stop= datetime.strptime(date_stop,"%Y-%m-%d %H:%M:%S")
                other_insurance.date_stop=date_stop
            except:
                pass
        else:
            raise ParameterError('请添加保单截止日期')
        
        if date_stop<date_start:
            raise ParameterError('保单截止日期不能早与开始日期')
        
        return other_insurance


#   2017-12-07验证车辆
    def validation_create_car_new(self, create_car):
        car_state_new = self.get_parameter('car_state_new').strip()       #车辆状态
        #订单信息
        client_id = self.get_parameter('client_id').strip()       #投保使用账户
        insured_classify =self.get_parameter('insured_classify').strip() #被保人身份
        insured_name = self.get_parameter('insured_name').strip()       #被保人姓名（单位名称）
        insured_number = self.get_parameter('insured_number').strip()       #被保人证件号或组织机构号
        #投保人
        if client_id:
            client = Client.objects(id=client_id).first()
            if client:
                create_car.client = client
            else:
                raise ParameterError('客户不存在')
        else:
            raise ParameterError('客户不能为空')
        #被保人身份
        if insured_classify:
            if insured_classify in ["personal","unit"]:
                create_car.insured_classify = insured_classify
            else:
                raise ParameterError('被保人身份不正确')
        else:
            raise ParameterError('请选择被保人身份')
        #被保人信息
        if insured_classify =="personal":
            if not insured_name:
                raise ParameterError('请输入被保人姓名')
            if not insured_number:
                raise ParameterError('请输入被保人身份证号')
        if insured_classify =="unit":
            if not insured_name:
                raise ParameterError('请输入被保单位名称')
            if not insured_number:
                raise ParameterError('请输入组织机构代码号或营业执照号码')
        create_car.insured_name = insured_name
        create_car.insured_number = insured_number
        
        #行驶证
        now = datetime.now()
        otherStyleTime  = now.strftime("%Y-%m-%d ")
        plate_image_left = self.request.FILES.get('id_plate_image_left', '')     #行驶证正页
        plate_image_right = self.request.FILES.get('id_plate_image_right', '')    #行驶证附页
        short = self.request.POST.get('short_number', '')        # 车牌号-1
        mid = self.request.POST.get('mid_number', '')        # 车牌号-2
        plate_number  = self.request.POST.get('plate_number', '')        # 车牌号-3
        car_type  = self.request.POST.get('car_type', '')                #车辆类型
        holder = self.request.POST.get('holder', '')#所有人
        use_property= self.request.POST.get('use_property', '')#使用性质
        brand_digging = self.request.POST.get('brand_digging', '')#品牌型号
        car_number   = self.request.POST.get('car_number', '')#车辆识别代码
        engine_number  = self.request.POST.get('engine_number', '')#发动机号
        issue_date  = self.request.POST.get('issue_date', '')#注册日期
        people_number   = self.request.POST.get('people_number', '')#核载人数
        load_weight   = self.request.POST.get('load_weight', '')#核载人数
        plate_expiration_periods   = self.request.POST.get('plate_expiration_periods', '')#校验有效期
        #2017/12/14添加四个时间
        license_expiration_time  = self.request.POST.get('license_expiration_time', '')#运营证到期时间
        grade_expiration_time  = self.request.POST.get('grade_expiration_time', '')#等级评定到期时间
        twolevel_expiration_time  = self.request.POST.get('twolevel_expiration_time', '')#二级维护到期时间
        trailer_expiration_time  = self.request.POST.get('trailer_expiration_time', '')#挂车车船稅到期时间
        award_date  = self.request.POST.get('award_date', '')#发证日期
        
        #行驶证
        if plate_image_left:
            image_tool = ImageTools()
            plate_image_left_url = image_tool.save(request_file=plate_image_left, file_folder=ImageFolderType.car, old_file='')
            if plate_image_left_url:
                create_car.plate_image_left.append( plate_image_left_url )
            else:
                raise ParameterError('保存行驶证照片正页正面图片失败')
        else:
            if car_state_new=="edit":
                pass
            else:
                raise ParameterError('请选择添加行驶证照片正页正面图片')
        
        if plate_image_right:
            image_tool = ImageTools()
            plate_image_right_url = image_tool.save(request_file=plate_image_right, file_folder=ImageFolderType.car, old_file='')
            if plate_image_right_url :
                create_car.plate_image_left.append( plate_image_right_url )
            else:
                raise ParameterError('保存行驶证照片附页正面图片失败')
        else:
            pass
#             if car_state_new=="edit":
#                 pass
#             else:
#                 raise ParameterError('请选择添加行驶证照片附页正面图片')
        #车牌号
        short = self.get_parameter('short_number').strip()
        mid = self.get_parameter('mid_number').strip()
        if plate_number:
            if not short or not mid:
                raise ParameterError('请选择车牌号前两位。如“黑A')
            if re.match(r'^[a-z_A-Z_0-9]{5}$', plate_number):
                 plate_number = plate_number.upper()
                 plate_number1 = short +mid +" "+plate_number
                 create_car.plate_number=plate_number1
            else:
                if "挂"  in plate_number:
                    plate_number2=plate_number.replace("挂","")
                    if re.match(r'^[a-z_A-Z_0-9]{4}$', plate_number2):
                        plate_number = plate_number.upper()
                        plate_number1 = short +mid +" "+plate_number
                        create_car.plate_number=plate_number1
                    else:
                        raise ParameterError('您输入的车牌号不正确，请输入由英文或数字组成的五位字符串 ，挂车车牌由”挂“字和四位英文数字组合')
                else:
                    raise ParameterError('您输入的车牌号不正确，请输入由英文或数字组成的五位字符串')
        else:
            raise ParameterError('车牌号不能为空')
        if car_type:
            create_car.car_type=car_type
        else:
            pass
#             raise ParameterError('请选择车辆类型错误')
        if holder:
            create_car.holder=holder
        else:
            pass
#             raise ParameterError('未输入车辆所有人')
        if use_property:
            create_car.use_property=use_property
#         else:
#             raise ParameterError('未输入使用性质')
        if brand_digging:
            create_car.brand_digging=brand_digging
#         else:
#             raise ParameterError('未输入品牌型号')
        if car_number:
            create_car.car_number=car_number
#         else:
#             raise ParameterError('未输入车辆识别代码')
        if engine_number:
            create_car.engine_number=engine_number
#         else:
#             raise ParameterError('未输入发动机号')
        if issue_date:
            if issue_date>otherStyleTime:
                raise ParameterError('注册日期不能大于当前日期')
            else:
                a=issue_date+" 00:00:00"
                issue_date= datetime.strptime(a,"%Y-%m-%d %H:%M:%S")
                create_car.issue_date=issue_date
#         else:
#             raise ParameterError('未输入注册日期')
        
        if people_number:
            create_car.people_number=people_number
        if load_weight:
            create_car.load_weight=load_weight
#         if  people_number=="" and load_weight=="":
#             raise ParameterError('“核载人数”或“核载质量”不能同时为空')
        
        #行驶证校验日期
        if plate_expiration_periods:
            now_month=now.strftime("%Y-%m")
            if plate_expiration_periods<now_month:
                raise ParameterError('输入的校验有效期已过期')
            else:
                try:
                    plate_expiration_periods=str(plate_expiration_periods) +"-01"  +" 00:00:00"
                    plate_expiration_periods= datetime.strptime(plate_expiration_periods,"%Y-%m-%d %H:%M:%S")
                    create_car.plate_expiration_periods=plate_expiration_periods
                except Exception as e:
                    pass
#                 test_e = str(e)
#                 raise ParameterError(str(e))
#             if plate_expiration_periods<now_month:
#                 raise ParameterError('输入的校验有效期已过期')
#             else:
#                 create_car.plate_expiration_periods=plate_expiration_periods
#         else:
#             raise ParameterError('未输入行驶证校验有效期')
        #运营证到期时间
        if license_expiration_time:
            try:
                license_expiration_time=license_expiration_time +"-01"  +" 00:00:00"
                license_expiration_time= datetime.strptime(license_expiration_time,"%Y-%m-%d %H:%M:%S")
                create_car.license_expiration_time=license_expiration_time
            except:
                pass
            
        #等级评定到期时间
        if grade_expiration_time:
            try:
                grade_expiration_time=grade_expiration_time+"-01"  +" 00:00:00"
                grade_expiration_time= datetime.strptime(grade_expiration_time,"%Y-%m-%d %H:%M:%S")
                create_car.grade_expiration_time=grade_expiration_time
            except:
                pass
            
    #二级维护到期时间
        if twolevel_expiration_time:
            try:
                twolevel_expiration_time=twolevel_expiration_time+"-01"  +" 00:00:00"
                twolevel_expiration_time= datetime.strptime(twolevel_expiration_time,"%Y-%m-%d %H:%M:%S")
                create_car.twolevel_expiration_time=twolevel_expiration_time
            except:
                pass
            
    #挂车车船稅到期时间
        if trailer_expiration_time:
            try:
                trailer_expiration_time=trailer_expiration_time+"-01"  +" 00:00:00"
                trailer_expiration_time= datetime.strptime(trailer_expiration_time,"%Y-%m-%d %H:%M:%S")
                create_car.trailer_expiration_time=trailer_expiration_time
            except:
                pass
            
    #发证日期
        if award_date:
            if award_date>otherStyleTime:
                raise ParameterError('发证日期不能大于当前日期')
            else:
                a=award_date+" 00:00:00"
                award_date= datetime.strptime(a,"%Y-%m-%d %H:%M:%S")
                create_car.award_date=award_date
         
        #交强险
        #liability_image = self.request.FILES.get('liability_image', '')     #交强险保单
        liability_number                = self.request.POST.get('liability_number', '')#保单号
        liability_tax              = self.request.POST.get('liability_tax', '')#车船税
        liability_price                  = self.request.POST.get('liability_price', '')#保费
        liability_date_start                 = self.request.POST.get('liability_date_start', '')#保险期限起始日期
        liability_date_stop       = self.request.POST.get('liability_date_stop', '')#保险期限终止日期
        liability_company                = self.request.POST.get('liability_company', '')#承保公司
        if not  liability_number and not liability_tax and not liability_price and not liability_date_start and not liability_date_stop and not liability_company:
            pass
        else:
            # 添加交强险保单图片
            #上传保单方式
            liability_up_state = self.get_parameter('liability_up_state').strip()
            if  liability_up_state:
                if liability_up_state not in ['picture' , 'web_url' , 'pdf']:
                    raise ParameterError('请选择正确的交强险保单上传方式')
    #             else:
    #                 freight.up_state = str(insurance_type)
            #上传保单内容
            liability_insurance_image_list=""
            try:
                if liability_up_state == 'web_url':
                    liability_insurance_image_list = self.request.POST.get('liability_insurance_image', '')
                else:
                    liability_insurance_image_list = self.request.FILES.getlist('liability_insurance_image', '')
            except Exception as e:
                raise ParameterError("提取保单信息出错："+str(e))
            
            if not liability_insurance_image_list:
                    if car_state_new == "create" :
                        pass
                    elif car_state_new == "edit" and  liability_up_state != create_car.liability_up_state:
                        if liability_up_state != create_car.liability_up_state and create_car.liability_image_list:
                            raise ParameterError("请补充交强险保单文件")
                    else:
                        pass
            else:
                create_car.liability_up_state = str(liability_up_state)
                create_car.liability_image_list=[]
                 #保单图片
                if liability_up_state == 'picture':
                    try:
                        image_tool = ImageTools()
                        if liability_insurance_image_list:
                            for insurance_image in liability_insurance_image_list:
                                order_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
                                if not order_image_url:
                                    raise ParameterError("生成保单图片地址失败")
                                else:
                                    create_car.liability_image_list.append(order_image_url)
                    except ParameterError as e:
                        # 初始化错误信息
                        raise ParameterError("图片上传失败"+str(e))
                #pdf文件保存
                elif liability_up_state == 'pdf':
                        if liability_insurance_image_list:
                            #交强险文档
                            liability_document_url=[]
                            for insurance_image in liability_insurance_image_list:
                                document_tools = DocumentTools()
                                try:
                                    file_url = document_tools.save(request_file=insurance_image, file_folder=DocumentFolderType.order, old_file='')
                                except Exception as e:
                                    raise ParameterError(str(e)+'保单文件上传失败')
                                liability_document_url.append(file_url)
                            if not liability_document_url:
                                raise ParameterError('生成保单文件地址失败')
                            else:
                                create_car.liability_image_list=liability_document_url
                elif liability_up_state == 'web_url':
                        if liability_insurance_image_list:
                            insurance_web_url = []
                            liability_insurance_image_list = str(liability_insurance_image_list)
                            insurance_web_url.append(liability_insurance_image_list)
                            create_car.liability_image_list = insurance_web_url   
            
            
            #添加交强险保单结束
#             if liability_image:
#                 image_tool = ImageTools()
#                 liability_image_url = image_tool.save(request_file=liability_image, file_folder=ImageFolderType.car, old_file='')
#                 if liability_image_url :
#                     create_car.liability_image  = liability_image_url 
#                 else:
#                     raise ParameterError('保存交强险照片失败')
#             else:
#                 if car_state_new=="edit" and create_car.liability_image :
#                     pass
#                 else:
#                     raise ParameterError('请选择添加交强险照片图片')
            if liability_number:
                create_car.liability_number=liability_number
#             else:
#                 raise ParameterError('交强险保单号未填写')
            if liability_tax:
                try:
                    liability_tax=int(float(liability_tax)*100)
                    create_car.liability_tax=liability_tax
                except:
                    raise ParameterError('交强险车船税只能为最多带两位小数的数字')
#             else:
#                 raise ParameterError('交强险车船税未填写')
            if liability_price:
                try:
                    liability_price=int(float(liability_price)*100)
                    create_car.liability_price=liability_price
                except:
                    raise ParameterError('交强险保费只能为最多带两位小数的数字')
#             else:
#                 raise ParameterError('交强险保费未填写')
            if liability_date_start:
                liability_date_start=liability_date_start+" 00:00:00"
                liability_date_start= datetime.strptime(liability_date_start,"%Y-%m-%d %H:%M:%S")
                create_car.liability_date_start=liability_date_start
#             else:
#                 raise ParameterError('交强险保险期限起始日期未填写')
            
            if liability_date_stop:
                liability_date_stop=liability_date_stop+" 00:00:00"
                liability_date_stop= datetime.strptime(liability_date_stop,"%Y-%m-%d %H:%M:%S")
                if liability_date_stop<liability_date_start:
                    raise ParameterError('交强险保险期限终止日期不能小于起始日期')
                else:
                    create_car.liability_date_stop=liability_date_stop
#             else:
#                 raise ParameterError('交强险保险期限终止日期未填写')
            
            if liability_company:
                try:
                    company = InsuranceCompany.objects(id=liability_company).first()
                    if company:
                        create_car.liability_company_new=company
                    else:
                        raise ParameterError("您选择的保险公司不存在")
                except:
                    raise ParameterError("您选择的保险公司不存在.")
#             else:
#                 raise ParameterError('交强险承保公司未填写')
        #商业险
        #commercial_image           = self.request.FILES.get('commercial_image', '')    #商业险
        commercial_num              = self.request.POST.get('commercial_num', '')#保单号
        commercial_price              = self.request.POST.get('commercial_price', '')#保费
        commercial_date_start    = self.request.POST.get('commercial_date_start', '')#保险期限起始日期
        commercial_date_stop    = self.request.POST.get('commercial_date_stop', '')#保险期限结束日期
        commercial_company    = self.request.POST.get('commercial_company', '')#承保公司
        
        if  not commercial_num and not commercial_price and not commercial_date_start and not commercial_date_stop and not commercial_company :
            pass#允许不填写商业险
        else:
                        # 添加商业险保单图片
            #上传保单方式
            commercial_up_state = self.get_parameter('commercial_up_state').strip()
            if  commercial_up_state:
                if commercial_up_state not in ['picture' , 'web_url' , 'pdf']:
                    raise ParameterError('请选择正确的商业险保单上传方式')
    #             else:
    #                 freight.up_state = str(insurance_type)
            #上传保单内容
            commercial_insurance_image_list=""
            try:
                if commercial_up_state == 'web_url':
                    commercial_insurance_image_list = self.request.POST.get('commercial_insurance_image', '')
                else:
                    commercial_insurance_image_list = self.request.FILES.getlist('commercial_insurance_image', '')
            except Exception as e:
                raise ParameterError("提取保单信息出错："+str(e))
            
            if not commercial_insurance_image_list:
                    if car_state_new == "create" :
                        pass
                    elif car_state_new == "edit" and  commercial_up_state != create_car.commercial_up_state:
                        if commercial_up_state != create_car.commercial_up_state and create_car.commercial_image_list:
                            raise ParameterError("请补充商业险保单文件")
                    else:
                        pass
            else:
                create_car.commercial_up_state = str(commercial_up_state)
                create_car.commercial_image_list=[]
                 #保单图片
                if commercial_up_state == 'picture':
                    try:
                        image_tool = ImageTools()
                        if commercial_insurance_image_list:
                            for insurance_image in commercial_insurance_image_list:
                                order_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
                                if not order_image_url:
                                    raise ParameterError("生成保单图片地址失败")
                                else:
                                    create_car.commercial_image_list.append(order_image_url)
                    except ParameterError as e:
                        # 初始化错误信息
                        raise ParameterError("图片上传失败"+str(e))
                #pdf文件保存
                elif commercial_up_state == 'pdf':
                        if commercial_insurance_image_list:
                            #商业险文档
                            commercial_document_url=[]
                            for insurance_image in commercial_insurance_image_list:
                                document_tools = DocumentTools()
                                try:
                                    file_url = document_tools.save(request_file=insurance_image, file_folder=DocumentFolderType.order, old_file='')
                                except Exception as e:
                                    raise ParameterError(str(e)+'保单文件上传失败')
                                commercial_document_url.append(file_url)
                            if not commercial_document_url:
                                raise ParameterError('生成保单文件地址失败')
                            else:
                                create_car.commercial_image_list=commercial_document_url
                elif commercial_up_state == 'web_url':
                        if commercial_insurance_image_list:
                            insurance_web_url = []
                            commercial_insurance_image_list = str(commercial_insurance_image_list)
                            insurance_web_url.append(commercial_insurance_image_list)
                            create_car.commercial_image_list = insurance_web_url   
            
            
            #添加商业险保单结束

            
#             if commercial_image:
#                 image_tool = ImageTools()
#                 commercial_image_url = image_tool.save(request_file=commercial_image, file_folder=ImageFolderType.car, old_file='')
#                 if commercial_image_url :
#                     create_car.commercial_image  = commercial_image_url 
#                 else:
#                     raise ParameterError('保存商业险照片图片失败')
#             else:
#                 if car_state_new=="edit" and create_car.commercial_image:
#                     pass
#                 else:
#                     raise ParameterError('请选择添加商业险照片图片')
            if commercial_num:
                create_car.commercial_num=commercial_num
#             else:
#                 raise ParameterError('商业险保单号未填写')
            if commercial_price:
                try:
                    commercial_price1=float(commercial_price)
                    commercial_price2 = int( commercial_price1*100)
                except:
                    raise ParameterError('商业险保费应为最多为两位小数的数字')
                create_car.commercial_price=commercial_price2
#             else:
#                 raise ParameterError('商业险保费未填写')
            if commercial_date_start:
                commercial_date_start=commercial_date_start+" 00:00:00"
                commercial_date_start= datetime.strptime(commercial_date_start,"%Y-%m-%d %H:%M:%S")
                create_car.commercial_date_start=commercial_date_start
#             else:
#                 raise ParameterError('商业险起始日期未填写') 
            if commercial_date_stop:
                commercial_date_stop=commercial_date_stop+" 00:00:00"
                commercial_date_stop =  datetime.strptime(commercial_date_stop,"%Y-%m-%d %H:%M:%S")
                if commercial_date_stop<commercial_date_start:
                    raise ParameterError('商业险结束日期不能大于开启日期')   
                else:
                    create_car.commercial_date_stop = commercial_date_stop
#             else:
#                 raise ParameterError('商业险结束日期未填写')
            if commercial_company:
                try:
                    commercial_company_set = InsuranceCompany.objects(id=commercial_company).first()
                    if commercial_company_set:
                        create_car.commercial_company_new=commercial_company_set
                    else:
                        raise ParameterError("商业险承保公司不存在")
                except:
                    raise ParameterError("您选择的商业险承保公司不存在.")
#             else:
#                 raise ParameterError('商业险承保公司公司未填写')
            #险种清单
            a=[]
            create_car.commercial_tax=a
            commercial_tax_list = self.request.POST.getlist('position')
            commercial_price1=0
            if len(commercial_tax_list) > 0:
                for commercial_tax in commercial_tax_list:
                    try:
                        xz = self.request.POST.get("xz_" + commercial_tax)
                        je =self.request.POST.get("je_" + commercial_tax)
                        bc =self.request.POST.get("bc_" + commercial_tax)
                        taxlist=TaxList()
                    except:
                        raise ParameterError('商业险险种格式不正确')
                    if xz:
                        taxlist.com_kind=xz
                    else:
                        raise ParameterError('商业险险种未填写')
                    if je:
                        try:
                            je=int(float(je)*100)
                            taxlist.com_price=je
                            commercial_price1=commercial_price1+je
                        except:
                            raise ParameterError('商业险保费只能为最多带两位小数的数字')
                        
                    else:
                        raise ParameterError('商业险险种保费未填写')
                    if xz in ["第三者责任险","划痕险","玻璃险","司机险","乘客险"]:
                        if not bc:
                            raise ParameterError('请补充对应保险类型保额')
                        else:
                            taxlist.com_notice=str(bc)
                    try:
                        create_car.commercial_price=commercial_price1#保证填写的总保费和各个险别总保费一致
                        create_car.commercial_tax.append( taxlist )
                    except:
                        raise ParameterError('险种存储过程出错，请检查输入保费部分（保费只能为最多带两位小数的数字）')
#             else:
#                 raise ParameterError('商业险险种不能为空') 
            #商业险结束

        #添加总保费
        try:
            create_car.total_price=create_car.liability_tax+create_car.liability_price+create_car.commercial_price
        except:
            raise ParameterError('总保费计算过程出错')

        return create_car
    
    #2017/12/20添加二手商品类型
    def validation_goods_type(self, goods_type):
        state = self.get_parameter("goods_type_state").strip()#状态
        name = self.get_parameter("name").strip()#类型名称
        priority = self.get_parameter("priority").strip()#优先级
        picture = self.request.FILES.get("picture")#上传图片
        active = self.get_parameter("active").strip()#是否显示
        if state  not in ['create','edit']:
            raise ParameterError('网络延迟，创建商品类型状态不正确，请退出当前页面重试。')
        #名称
        if  name:
            if len(name)>40:
                raise ParameterError('您输入的商品类型名称过长，请压缩在20个字以内')
            goods_type.name =  str(name)
        else:
            raise ParameterError('请输入商品类型名称')
        #优先级
        if priority :
            try:
                priority=int(priority)
            except:
                raise ParameterError("优先级只能为大于零的整数")
            if priority <=  0:
                raise ParameterError("优先级只能为大于零的整数。")
            goods_type.priority =  priority
        else:
            raise ParameterError("请输入优先级")
        
        #图标
        if picture :
            try:
                image_tool = ImageTools()
                picture_url = image_tool.save(request_file=picture, file_folder=ImageFolderType.mall, old_file='')
                if not picture_url:
                    raise ParameterError("生成图片地址失败")
                else:
                    goods_type.picture = picture_url
            except ParameterError as e:
                # 初始化错误信息
                raise ParameterError("图片上传失败"+str(e))
#         else:
#             if state == 'edit' and  goods_type.picture :
#                 pass
#             else:
#                 raise ParameterError("请上传图标图片")
        #显示状态
        if active not in ["show","hidden"]:
            ParameterError("请选择产品类型显示状态")
        else:
            if active =="show":
                goods_type.is_hidden =  False
            else:
                goods_type.is_hidden =  True
        
        return goods_type
    
    #验证用户商品
    def validation_mall_goods(self, mall_goods):
        state= self.get_parameter("mall_goods_state").strip()#编辑状态
        client_id= self.get_parameter("client_id").strip()#商品所有人
        goods_name= self.get_parameter("goods_name").strip()#商品名称
        goods_brand_digging= self.get_parameter("goods_brand_digging").strip()#品牌型号
        goods_count= self.get_parameter("goods_count").strip()#商品数量
        original_cost= self.get_parameter("original_cost").strip()#商品原价
        unit_price= self.get_parameter("unit_price").strip()#商品单价
        present_situation= self.get_parameter("present_situation").strip()#商品状态
        publish_state =self.get_parameter("publish_state").strip()
        other_notes= self.get_parameter("other_notes").strip()#商品状态补充信息
        goods_type= self.get_parameter("goods_type").strip()#商品分类
        
        #地址
        startSiteName_prov = self.get_parameter('startSiteName_prov').strip()#省
        startSiteName_city = self.get_parameter('startSiteName_city').strip()#市
        startSiteName_dist = self.get_parameter('startSiteName_dist').strip()#区
        policy_address = self.get_parameter('policy_address').strip()
        #地址结束
        contact_people= self.get_parameter("contact_people").strip()#联系人
        contact_phone= self.get_parameter("contact_phone").strip()#联系方式-手机
        contact_landline= self.get_parameter("contact_landline").strip()#联系方式-座机
        contact_qq= self.get_parameter("contact_qq").strip()#联系方式-QQ
        contact_wx= self.get_parameter("contact_wx").strip()#联系方式-wx
        goods_describe= self.get_parameter("goods_describe").strip()#商品描述
        picture_list = self.request.FILES.getlist('picture', '')#商品照片
        certificate_type= self.get_parameter("certificate_type").strip()#商品证明方式
        certificate_url= self.get_parameter("certificate_url").strip()#商品证明地址
        certificate_image_list = self.request.FILES.getlist('certificate_image', '')#商品价值证明照片
        active= self.get_parameter("active").strip()#显示状态
        
        #编辑状态
        if state not in ['create','edit']:
            raise ParameterError('网络问题，未获取商品创建状态')
        #用户
        if client_id :
            client = Client.objects(id=client_id).first()
            if client:
                mall_goods.client = client
        else:
            raise ParameterError('请选择商品所属用户')
        #商品名称
        if goods_name:
            if len(goods_name)>30:
                raise ParameterError('请名称最多输入30个字符')
            mall_goods.goods_name =str(goods_name)
        else:
            raise ParameterError('请输入商品名称')
        #品牌型号
        if goods_brand_digging:
            if len(goods_brand_digging)>100:
                raise ParameterError('请名称最多输入100个字符')
            mall_goods.goods_brand_digging =str(goods_brand_digging)
        #商品分类
        if goods_type:
            try:
                goods_type_set = GoodsType.objects(id=goods_type).first()
                if not goods_type_set:
                    raise ParameterError('请选择商品分类。')
            except:
                raise ParameterError('网络延迟，未找到对应商品分类，请退出重试')
            mall_goods.goods_type =goods_type_set
        else:
            raise ParameterError('请选择商品分类')
        #原价
        if original_cost:
            if len(original_cost)>30:
                raise ParameterError('原价最多输入30个字符')
            try:
                original_cost1=float(original_cost)*100
                original_cost2 =int(original_cost1)
                if original_cost2<original_cost1:
                    raise ParameterError('原价最多输入两位小数')
            except:
                raise ParameterError('原价只能输入数字')
            mall_goods.original_cost =int(original_cost2)
        else:
            raise ParameterError('请输入商品原价')
        #商品状态
        if present_situation:
            mall_goods.goods_present_situation =str(present_situation)
        else:
            raise ParameterError('请输入商品状态')
        #商品状态补充信息
        if present_situation == 'other':
            if other_notes:
                mall_goods.other_notes =str(other_notes)
            else:
                raise ParameterError('请输入商品状态补充信息')
        else:
            mall_goods.other_notes =''
        #单价
        if unit_price:
            if len(unit_price)>30:
                raise ParameterError('单价最多输入30个字符')
            try:
                unit_price1=float(unit_price)*100
                unit_price2 =int(unit_price1)
                if unit_price2<unit_price1:
                    raise ParameterError('单价最多输入两位小数')
            except:
                raise ParameterError('单价只能输入数字')
            mall_goods.unit_price =int(unit_price2)
        else:
            raise ParameterError('请输入商品单价')
        #数量
        if goods_count:
            if len(goods_count)>30:
                raise ParameterError('数量最多输入30个字符')
            mall_goods.goods_count =str(goods_count)
        else:
            raise ParameterError('请输入商品数量')
        
        
        #上架状态
        if publish_state:
            mall_goods.state =str(publish_state)
        else:
            raise ParameterError('请输入上架状态')
        
        
        
        #商品地址
        if not startSiteName_prov or not startSiteName_city or not startSiteName_dist or not policy_address:
            raise ParameterError('请输入商品所在位置')
        if startSiteName_prov and startSiteName_city:
            mail_address =startSiteName_prov + ' ' +startSiteName_city
        if startSiteName_dist:
            mail_address = mail_address + ' ' +startSiteName_dist
        mall_goods.mail_address =str(mail_address)
        mall_goods.policy_address =str(policy_address)
        #商品地址结束
        
        #联系人
        if contact_people:
            mall_goods.contact_people =str(contact_people)
        else:
            raise ParameterError('请输入联系人')
        #联系方式
        if not contact_phone and not contact_landline and not contact_qq and not contact_wx:
            raise ParameterError('手机号，座机号，QQ号，微信号四种联系方式请至少填写一种联系方式')
        #手机
        if contact_phone:
            if len(contact_phone)>80:
                raise ParameterError('您输入的手机号过长')
            mall_goods.contact_phone =str(contact_phone)
        else:
            mall_goods.contact_phone =''
        #座机号
        if contact_landline:
            if len(contact_landline)>80:
                raise ParameterError('您输入的座机号过长')
            mall_goods.contact_landline =str(contact_landline)
        else:
            mall_goods.contact_landline =''
        #QQ
        if contact_qq:
            if len(contact_qq)>80:
                raise ParameterError('您输入的QQ号过长')
            mall_goods.contact_qq =str(contact_qq)
        else:
            mall_goods.contact_qq =''
        #微信
        if contact_wx:
            if len(contact_wx)>80:
                raise ParameterError('您输入的微信号过长')
            mall_goods.contact_wx =str(contact_wx)
        else:
            mall_goods.contact_wx =''
        #商品描述
        if goods_describe:
            mall_goods.goods_describe =str(goods_describe)
        else:
            raise ParameterError('请输入商品描述')
        #商品图片
        if picture_list:
            if  state =="edit":
                mall_goods.goods_image_list = []
            for goods_image in picture_list:
                goods_size = goods_image.size
                try:
                    image_tool = ImageTools()
                    goods_image_url = image_tool.save(request_file=goods_image, file_folder=ImageFolderType.mall, old_file='')
                    if goods_image_url:
                        mall_goods.goods_image_list.append(goods_image_url)
                    else:
                        raise ParameterError('保存商品图片失败')
                except Exception as e:
                    message ='商品图片上传失败' +str(e)
                    raise ParameterError(message)
                #压缩图片
                if goods_image_url:
                    try:
                        BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                        image_main_url = BASE_ROOT+"/static/"+goods_image_url
                        new_size =os.path.getsize(image_main_url)
                        sImg=Image.open(image_main_url)  
                        w,h=sImg.size  
                       # while new_size >500000#如果图片大于500k压缩图片
                        while h>510 or new_size >500000:
                            w =int(w/2)
                            h =int(h/2)
                            dImg=sImg.resize((w,h),Image.ANTIALIAS)  #设置压缩尺寸和选项，注意尺寸要用括号
                            dImg.save(image_main_url) #也可以用srcFile原路径保存,或者更改后缀保存，save这个函数后面可以加压缩编码
                            new_size =os.path.getsize(image_main_url)
                    except Exception as e:
                        message = str(e)
                        raise ParameterError(message)
        else:
            if state =='edit' and mall_goods.goods_image_list:
                pass
            else:
                raise ParameterError('请上传商品图片')
        
        #证明价值方式
        if certificate_type:
            if certificate_type not in ["picture","web_url"]:
                raise ParameterError('选择的商品价值方式不存在')   
           # mall_goods.certificate_type =str(certificate_type)
        else:
            raise ParameterError('请选择证明商品价值方式')   
        #证明价值
        if certificate_type == "web_url":
            certificate_url_list=[]
            if certificate_url:
                certificate_url_list.append(certificate_url)
                mall_goods.certificate_image_list =certificate_url_list
            else:
                raise ParameterError('请输入原商品网站地址')   
        else:
            if certificate_image_list:
                if  state =="edit":
                    mall_goods.certificate_image_list = []
                image_tool = ImageTools()
                for certificate_image in certificate_image_list:
                    try:
                        certificate_image_url = image_tool.save(request_file=certificate_image, file_folder=ImageFolderType.mall, old_file='')
                        if certificate_image_url:
                            mall_goods.certificate_image_list.append(certificate_image_url)
                        else:
                            raise ParameterError('保存商品价值图片失败')
                    except:
                        raise ParameterError('商品价值图片上传失败')
                    #压缩图片
                    if certificate_image_url:
                        try:
                            BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                            image_main_url = BASE_ROOT+"/static/"+certificate_image_url
                            new_size =os.path.getsize(image_main_url)
                            sImg=Image.open(image_main_url)  
                            w,h=sImg.size  
                           # while new_size >500000#如果图片大于500k压缩图片
                            while h>510 or new_size >500000:
                                w =int(w/2)
                                h =int(h/2)
                                dImg=sImg.resize((w,h),Image.ANTIALIAS)  #设置压缩尺寸和选项，注意尺寸要用括号
                                dImg.save(image_main_url) #也可以用srcFile原路径保存,或者更改后缀保存，save这个函数后面可以加压缩编码
                                new_size =os.path.getsize(image_main_url)
                        except Exception as e:
                            message = str(e)
                            raise ParameterError(message)
            else:
                if  state =="edit"  and mall_goods.certificate_type == 'picture'  and mall_goods.certificate_image_list:
                    pass
                else:
                    raise ParameterError('请上传证明商品价值图片')
        #保存商品价值证明方式
        mall_goods.certificate_type =str(certificate_type)
        #商品是否显示
        if active == 'show':
            mall_goods.is_hidden =False
        else:
            mall_goods.is_hidden =True
    
         
        return mall_goods
    
    
    #特推产品
    def validation_recommend_product(self, recommend_product):
        state= self.get_parameter("product_state").strip()#编辑状态
        name= self.get_parameter("name").strip()#产品名称
        picture_list =self.request.FILES.getlist('picture','')#产品图片
        phone = self.get_parameter('phone','').strip()#联系电话
        product_type = self.get_parameter('product_type','').strip()#产品分类
        description = self.get_parameter("content").strip()#产品介绍
        active =self.get_parameter('active','').strip()#激活状态
        
        if state not in ['create','edit']:
            raise ParameterError('网络延迟管理特推产品状态不正确')
        #产品名称
        if name:
            if len(name)>30:
                raise ParameterError("输入的特推产品名称过长")
            else:
                recommend_product.name = str(name)
        else:
            raise ParameterError ('请输入特推产品名称')
        #产品图片
        product_image_list=[]
        old_image_list=recommend_product.product_image_list
        if picture_list:
            for picture_set in picture_list:
                try:
                    image_tool = ImageTools()
                    picture_set_url = image_tool.save(request_file=picture_set, file_folder=ImageFolderType.product, old_file='')
                    if picture_set_url:
                        product_image_list.append(picture_set_url)
                    else:
                        raise ParameterError('保存商品图片失败')
                except Exception as e:
                    message ='商品图片上传失败' +str(e)
                    raise ParameterError(message)
            if product_image_list:
                recommend_product.product_image_list =product_image_list
            #删除旧图片
            if old_image_list:
                for image_url in old_image_list:
                    image_tool.delete(image_url)
        else:
            pass #可以不添加图片
        
        #产品电话
        if phone:
                recommend_product.phone = str(phone)
        else:
            raise ParameterError ('请输入特推产品电话')
        #产品分类
        type_list=[]
        for type_detail in RecommendProduct().PRODUCT_TYPE:
            type_list.append(type_detail[0])
        if product_type:
             if product_type not in type_list:
                 raise ParameterError ('网络延迟，未找到对应产品分类')
             recommend_product.product_type = str(product_type)
        else:
            raise ParameterError ('请选择特推产品分类')
        #产品介绍
        if description:
            description=description.replace("\r\n"," ")
            if len(description)>5000:
                raise ParameterError ('产品介绍内容过长，最多输入5000个字符')
            recommend_product.description = description  
        #显示状态
        if active not  in ['show','hidden']:
            raise ParameterError ('请选择显示状态')
        elif active == "show":
            recommend_product.is_hidden = False  
        elif active == "hidden":
            recommend_product.is_hidden = True  
        return recommend_product
    
    #2017/12/20添加广告位
    def validation_advertising_position(self, advertising_position):
        state = self.get_parameter("advertising_position_state").strip()#状态
        name = self.get_parameter("name").strip()#类型名称
        paper_id = self.get_parameter("paper_id").strip()#编号
        picture = self.request.FILES.get("picture")#上传图片
        note = self.get_parameter("note").strip()#补充信息
        active = self.get_parameter("active").strip()#是否显示
        if state  not in ['create','edit']:
            raise ParameterError('网络延迟，创建商品类型状态不正确，请退出当前页面重试。')
        #名称
        if  name:
            if len(name)>40:
                raise ParameterError('您输入的商品类型名称过长，请压缩在20个字以内')
            advertising_position.name =  str(name)
        else:
            raise ParameterError('请输入广告位名称')
        #编号
        if paper_id :
            try:
                paper_id=int(paper_id)
            except:
                raise ParameterError("编号只能为大于零的整数")
            if paper_id <=  0:
                raise ParameterError("编号只能为大于零的整数。")
            advertising_position.paper_id =  paper_id
        else:
            raise ParameterError("请输入编号")
        
        #图片
        old_picture_url=""
        if state == 'edit':
            old_picture_url = advertising_position.picture 
        if picture :
            try:
                image_tool = ImageTools()
                picture_url = image_tool.save(request_file=picture, file_folder=ImageFolderType.mall, old_file='')
                if not picture_url:
                    raise ParameterError("生成图片地址失败")
                else:
                    advertising_position.picture = picture_url
            except ParameterError as e:
                # 初始化错误信息
                raise ParameterError("图片上传失败"+str(e))
            
        #补充信息
        if  note:
            if len(note)>1000:
                raise ParameterError('您输入的补充信息过长，请压缩在1000个字以内')
            advertising_position.note =  str(note)
        else:
            advertising_position.note = ''
        #显示状态
        if active not in ["show","hidden"]:
            ParameterError("请选择产品类型显示状态")
        else:
            if active =="show":
                advertising_position.is_hidden =  False
            else:
                advertising_position.is_hidden =  True
        #删除旧图片
        if old_picture_url:
            try:
                image_tool = ImageTools()
                image_tools.delete(old_picture_url)
            except:
                ParameterError("历史图片删除失败")
        return advertising_position
    
    #2017/12/20添加广告
    def validation_advertising(self, advertising):
        state = self.get_parameter("advertising_state").strip()#状态
        name = self.get_parameter("name").strip()#类型名称
        advertising_position_id = self.get_parameter("advertising_position").strip()#广告位id
        picture = self.request.FILES.get("picture")#上传图片
        advertising_url = self.get_parameter("advertising_url").strip()#对应地址
        active = self.get_parameter("active").strip()#是否显示
        if state  not in ['create','edit']:
            raise ParameterError('网络延迟，创建商品类型状态不正确，请退出当前页面重试。')
        #名称
        if  name:
            if len(name)>40:
                raise ParameterError('您输入的商品类型名称过长，请压缩在20个字以内')
            advertising.name =  str(name)
        else:
            raise ParameterError('请输入广告位名称')
        
        #图片
        old_picture_url=""
        if state == 'edit':
            old_picture_url = advertising.picture 
        if picture :
            try:
                image_tool = ImageTools()
                picture_url = image_tool.save(request_file=picture, file_folder=ImageFolderType.mall, old_file='')
                if not picture_url:
                    raise ParameterError("生成图片地址失败")
                else:
                    advertising.picture = picture_url
                    
                #压缩图片
                if picture_url:
                    try:
                        BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                        image_main_url = BASE_ROOT+"/static/"+picture_url
                        new_size =os.path.getsize(image_main_url)
                        sImg=Image.open(image_main_url)  
                        w,h=sImg.size  
                       # while new_size >500000#如果图片大于500k压缩图片
                        while h>510 or new_size >500000:
                            w =int(w/2)
                            h =int(h/2)
                            dImg=sImg.resize((w,h),Image.ANTIALIAS)  #设置压缩尺寸和选项，注意尺寸要用括号
                            dImg.save(image_main_url) #也可以用srcFile原路径保存,或者更改后缀保存，save这个函数后面可以加压缩编码
                            new_size =os.path.getsize(image_main_url)
                    except Exception as e:
                        message = str(e)
                        raise ParameterError(message)
            except ParameterError as e:
                # 初始化错误信息
                raise ParameterError("图片上传失败"+str(e))
        #广告位
        if advertising_position_id :
            try:
                advertising_position_set = AdvertisingPosition.objects(id = advertising_position_id).first()
                if not advertising_position_set:
                    raise ParameterError("未找到对应广告位.")
                advertising.position =advertising_position_set
            except:
                raise ParameterError("未找到对应广告位")
        else:
            raise ParameterError("请选择广告对应广告位")
        #网站地址
        if  advertising_url:
            if len(advertising_url)>1000:
                raise ParameterError('您输入的网站地址过长，请压缩在1000个字以内')
            advertising.advertising_url =  str(advertising_url)
        else:
            advertising.advertising_url =''
        #显示状态
        if active not in ["show","hidden"]:
            ParameterError("请选择产品类型显示状态")
        else:
            if active =="show":
                advertising.is_hidden =  False
            else:
                advertising.is_hidden =  True
        #删除旧图片
        if old_picture_url:
            try:
                image_tool = ImageTools()
                image_tools.delete(old_picture_url)
            except:
                ParameterError("历史图片删除失败")
        return advertising

    
    
 #验证身份证号   
def checkIdcard(idcard):
    Errors=['验证通过!','身份证号码位数不对!','身份证号码出生日期超出范围或含有非法字符!','身份证号码校验错误!','身份证地区非法!']
    area={"11":"北京","12":"天津","13":"河北","14":"山西","15":"内蒙古","21":"辽宁","22":"吉林","23":"黑龙江","31":"上海","32":"江苏","33":"浙江","34":"安徽","35":"福建","36":"江西","37":"山东","41":"河南","42":"湖北","43":"湖南","44":"广东","45":"广西","46":"海南","50":"重庆","51":"四川","52":"贵州","53":"云南","54":"西藏","61":"陕西","62":"甘肃","63":"青海","64":"宁夏","65":"新疆","71":"台湾","81":"香港","82":"澳门","91":"国外"}
    idcard=str(idcard)
    idcard=idcard.strip()
    idcard_list=list(idcard)

    #地区校验
    if(not area[(idcard)[0:2]]):
        print (Errors[4])
    #15位身份号码检测
    if(len(idcard)==15):
        if((int(idcard[6:8])+1900) % 4 == 0 or((int(idcard[6:8])+1900) % 100 == 0 and (int(idcard[6:8])+1900) % 4 == 0 )):
            erg=re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')#//测试出生日期的合法性
        else:
            ereg=re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')#//测试出生日期的合法性
        if(re.match(ereg,idcard)):
            return   'success'
        else:
            return (Errors[2])
    #18位身份号码检测
    elif(len(idcard)==18):
        #出生日期的合法性检查
        #闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
        #平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
        if(int(idcard[6:10]) % 4 == 0 or (int(idcard[6:10]) % 100 == 0 and int(idcard[6:10])%4 == 0 )):
            ereg=re.compile('[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')#//闰年出生日期的合法性正则表达式
        else:
            ereg=re.compile('[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')#//平年出生日期的合法性正则表达式
        #//测试出生日期的合法性
        if(re.match(ereg,idcard)):
            #//计算校验位
            S = (int(idcard_list[0]) + int(idcard_list[10])) * 7 + (int(idcard_list[1]) + int(idcard_list[11])) * 9 + (int(idcard_list[2]) + int(idcard_list[12])) * 10 + (int(idcard_list[3]) + int(idcard_list[13])) * 5 + (int(idcard_list[4]) + int(idcard_list[14])) * 8 + (int(idcard_list[5]) + int(idcard_list[15])) * 4 + (int(idcard_list[6]) + int(idcard_list[16])) * 2 + int(idcard_list[7]) * 1 + int(idcard_list[8]) * 6 + int(idcard_list[9]) * 3
            Y = S % 11
            M = "F"
            JYM = "10X98765432"
            M = JYM[Y]#判断校验位
            if(M == idcard_list[17]):#检测ID的校验位
                return   'success'
            else:
                return (Errors[3])
        else:
            return  (Errors[2])
    else:
        return( Errors[1])
    
 #验证车辆识别代码
def checkVIN(vin_number):
    vin_number=str(vin_number)
    vin_number=vin_number.upper()
    vin_number=vin_number.strip('')
    vin_number_list=list(vin_number)
    #
    corresponding_value_list =[ ('0' ,0) , ('1' ,1) , ('2' ,2) , ('3' ,3) , ('4' ,4) , ('5' ,5) , ('6' ,6) , ('7' ,7) , ('8' ,8) , ('9' ,9) , 
                                                         ('A' ,1) , ('B' ,2) , ('C' ,3) , ('D' ,4) , ('E' ,5) , ('F' ,6) , ('G' ,7) , ('H' ,8) ,
                                                         ('J' ,1) , ('K' ,2) , ('L' ,3) , ('M' ,4) , ('N' ,5) , ('P' ,7) , ('R' ,9) ,
                                                         ('S' ,2) , ('T' ,3) , ('U' ,4) , ('V' ,5) , ('W' ,6) , ('X' ,7) , ('Y' ,8) , ('Z' ,9) ] 
    weighted_value_list = [8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2]
    #17位车辆识别代码检测
    if(len(vin_number) !=17):
        return '请输入17位车辆识别代码'
    #字符和数字校验
    if re.match('^[0-9a-zA-Z]+$',vin_number):
        pass
    else:
        return '车辆识别代码应为数字和字母组合'
    if 'I' in vin_number_list or 'O' in vin_number_list or 'Q' in vin_number_list:
        return '车辆识别代码不包含字母”I“、”O“、”Q“。'
    sum = 0
    for i in range(0,17):
        print( i)
        corresponding_detail = vin_number_list[i]
        weighted_detail = weighted_value_list[i]
        test_state = 'test_state'
        for corresponding_value in corresponding_value_list:
            a=corresponding_value[0]
            if corresponding_value[0] == corresponding_detail :
                test_state =int(corresponding_value[1])
                break
        if test_state != 'test_state':
            sum = sum + test_state*weighted_detail
    if sum%11 == 10:
        if vin_number_list[8] =='X':
            return 'success'
        else:
            return '车辆识别代码填写错误。'
    else:
        try:
            test_vim_number =int (vin_number_list[8])
        except:
            return '车辆识别代码填写错误!'
        if sum%11 == test_vim_number:
            return 'success'
        else:
            return '车辆识别代码填写错误'
            
    
#   验证批量上传保单
def validation_create_order_list(request, file_url):
        order_create_style = request.POST.get("order_create_style",'')
        client_id = request.POST.get("order_create_client",'')
        #file_url = '/home/ziqing/workspace/yunzhibao/static/order/document/20171109/a4ee817a-c51c-11e7-a165-1c394731dff9.xlsx'
        data = {}
        data["wrong_order_id"]=''        #生成订单出错
        data["wrong_pay_state"]=''      #未支付订单
        data["wrong_order_detail"]=''      #订单信息缺少
        data["fail_reason"]='' #上传文件出单失败
        data["order_total"]=""#上传订单数
        data["client_wx_id"]=""#用户微信id
        data["client_phone"]=""#用户手机号
        wrong_pay_state_count=0#未支付订单数量
        wrong_order_id_count=0#出错订单数量
        wrong_order_detail_count=0#信息缺少未生成订单数量
        if not order_create_style:
            data["state"]="fail"
            data["fail_reason"]='请选择批量创建的订单类型'
            return data
        if client_id:
            client = Client.objects(id=client_id).first()
            if not client:
                data["state"]="fail"
                data["fail_reason"]="客户不存在"
                return data
            else:
                data["client_wx_id"]=str(client.wx_id)
                data["client_phone"]= str(client.profile.phone)
                #投保人
                if  not client.company_name:
                    data["state"]="fail"
                    data["fail_reason"]="所选用户未认证为物流公司身份，不予出单"
                    return data
        else:
            data["state"]="fail"
            data["fail_reason"]='客户不能为空'
            return data
        if not file_url:
            data["state"]="fail"
            data["fail_reason"]='网络延迟未获取上传文件信息'
            return data
        #筛选产品
        try:
            site_settings = SiteSettings.get_settings()
            paper_id=site_settings.product_code
            insurance_product_set = InsuranceProducts.objects()
            insurance_product_set = insurance_product_set.filter(paper_id=paper_id).first()
            if insurance_product_set.is_hidden == True:
                data["state"]="fail"
                data["fail_reason"]="默认产品不可用请联系管理员及时修改。"
                return data
        except:
            data["state"]="fail"
            data["fail_reason"]="默认产品不存在，请联系管理员"
            return data
        if  not insurance_product_set:
            data["state"]="fail"
            data["fail_reason"]="默认产品不存在，请联系管理员设置。"
            return data
        try:
            order_data = xlrd.open_workbook(file_url,encoding_override='utf-8')
            table = order_data.sheets()[0]          #通过索引顺序获取
        except Exception as e:
            test=str(e).__class__
            data["state"]="fail"
            data["fail_reason"]="请检查文档格式，错误提示："+ str(e)
            return data
        if table:
            #获取行数和列数
            try:
                nrows = table.nrows
                ncols = table.ncols
                order_total = int(nrows)-1
                data["order_total"]="本次共上传"+str(order_total)+"个订单"#上传订单数
            except Exception as e:
                test=str(e)
            #如果有内容
            if nrows>1 and ncols>1:
                wrong_order_id=""#生成订单出错
                wrong_pay_state =''#未支付订单
                wrong_order_detail =""#订单信息缺少
    #             for i in range(1,nrows):
    #                 test_data =table.row_values(i)
                for i in range(1,nrows):
                    row_content = []
                    for j in range(ncols):
                        try:
                            ctype = table.cell(i, j).ctype #表格的数据类型
                            cell = table.cell_value(i, j)
                        except Exception as e:
                            test=str(e)
                        if ctype == 2 and cell % 1 == 0:  # 如果是整形
                            cell = int(cell)
                        elif ctype == 3:
                            # 转成datetime对象
                            date = datetime(*xldate_as_tuple(cell, 0))
                            #cell = date.strftime('%Y/%d/%m')
                            cell =date
                        row_content.append(cell)
                    #生成订单部分
                    try:
                        data_time=row_content[0]
                        data_paper_id =row_content[1]
                        #data_insurance_name =row_content[2]
                        data_commodityName =row_content[2]
                        data_commodityCases = row_content[3]
                        data_startSiteName=row_content[4]
                        data_targetSiteName=row_content[5]
                        data_insurance_price =row_content[6]
                    except Exception as e:
                        test_message =str(e)
                        wrong_order_id_count =wrong_order_id_count+1
                        wrong_order_id =str(wrong_order_id )+"托单号为："+str(row_content[1])+"，"
                    if data_time and data_paper_id and  data_commodityName and data_commodityCases :
                        if data_startSiteName and data_targetSiteName :
                            try:
                                #订单基础信息
                                order = Ordering()
                                order.state = "init"
                                order.product_type = 'car'
                                order.client = client
                                order.transport_type = '1'
                                #默认产品部分
                                order.insurance_product = insurance_product_set
                                order.company = insurance_product_set.company
                                order.insurance_type = insurance_product_set.insurance_type
                                #投保人
                                order.client_name = str(client.company_name)
                                order.expectStartTime = data_time#托单日期
                                order.transport_id = str(data_paper_id)#运单号
                                order.insured = str(client.company_name)+"之实际货主"#被保险人姓名
                                order.commodityName = str(data_commodityName)#货物名称
                                order.commodityCases = str(data_commodityCases)#货物数量
                                order.car_startSiteName = str(data_startSiteName)#起运地
                                order.car_targetSiteName = str(data_targetSiteName)#目的地
                                if  not data_insurance_price:
                                    order.insurance_price = 100000
                                else:
    #                                 try:
                                        data_insurance_price1=float(data_insurance_price)
                                        data_insurance_price2=data_insurance_price1*100
                                        data_insurance_price3=int(data_insurance_price2)
                                        order.insurance_price =data_insurance_price3
    #                                 except:
    #                                     wrong_order_id =wrong_order_id +"托单号为："+row_content[1]+"，"
                                
                                
                                order.save()
                            except Exception as e:
                                message1=str(e)
                                wrong_order_id_count =wrong_order_id_count+1
                                wrong_order_id =str(wrong_order_id )+"托单号为："+str(row_content[1])+"，"
                            if order:
                                #付款部分
                                if order.client.balance >= order.price:
                                    try:
                                            order.pay_money()
                                            order.save()
                                    except Exception as e:
                                        message1=str(e)
                                else:
                                    #余额不足发送微信
                                    wrong_pay_state_count=wrong_pay_state_count+1
                                    wrong_pay_state =str(wrong_pay_state) +"托单号为："+str(row_content[1])+"，"
                                
                                
                        else:
                            wrong_order_detail_count=wrong_order_detail_count+1
                            wrong_order_detail =str(wrong_order_detail) +"托单号为："+str(row_content[1])+"，托单日期："+str(row_content[0]) +"，发货方为："+str(row_content[2])+";"
                    else:
                        wrong_order_detail_count=wrong_order_detail_count+1
                        wrong_order_detail =str(wrong_order_detail)  +"托单号为："+str(row_content[1])+"，托单日期："+str(row_content[0]) +"，发货方为："+str(row_content[2])+";"
            
            
            if not wrong_order_id and not wrong_pay_state and not wrong_order_detail:
                data["state"]="success"
            else:
                data["state"]="fail"
            if wrong_order_id != '':
                data["wrong_order_id"]=wrong_order_id+'的订单信息有误未生成订单'+"（共"+str(wrong_order_id_count)+'份订单）。'#生成订单出错
            if wrong_pay_state != '':
                data["wrong_pay_state"]="共有："+str(wrong_pay_state_count)+'份订单未支付。'#未支付订单
            if wrong_order_detail != '':
                data["wrong_order_detail"]=wrong_order_detail+'的订单信息缺少不能生成订单'+"（共"+str(wrong_order_detail_count) +'订单）。'#订单信息缺少
            return data
        else:
            data["state"]="fail"
            data["fail_reason"]="请检查文档格式，未解析文档"
            return data
    
    
    
    
    