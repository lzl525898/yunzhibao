__author__ = 'mlzx'
from django.conf import settings
from wss.tools_wechat import WeChatTools, OpenidRequired, EventType
from common.tools import RequestTools
from common import tools_string
from django.http import HttpResponse
import traceback
from xml.etree import ElementTree
from common.tools_string import Match
from common.models import Client, Lawyer, Claim,CargoArea
from uuid import uuid1
import re, uuid, datetime, base64, os
from common.interface_helper import *
from common.tools import ConvertTools
from common.models import *

import urllib.request
from common.tools_legoo import DocumentTools, DocumentFolderType, ImageTools, ImageFolderType
from common.driver_dict import *
import time
from datetime import timedelta, date
# import datetime
import operator
#压缩图片
from PIL import Image
import os

# 用于需要登录的交互式命令
class LoginRequired(OpenidRequired):
    def _get_openid(self, args, kwargs):
        print("自动登录装饰类：获取openid：{0}".format(args[0].open_id))
        return args[0].open_id

    def _get_user(self, openid):
        print("自动登录装饰类：获取用户数量")
        # Client
        count = Client.objects(wx_id=openid).count()
        # Claim
        count += Claim.objects(wx_id=openid).count()
        # Lawyer
        count += Lawyer.objects(wx_id=openid).count()
        return count

    def _get_request(self, args, kwargs):
        print("自动登录装饰类：获取request")
        return args[0].request


# 用于仅使用于普通用户的交互式命令
class ClientRequired(OpenidRequired):
    def _get_openid(self, args, kwargs):
        return args[0].open_id

    def _get_user(self, openid):
        # Client
        count = Client.objects(wx_id=openid).count()
        return count

    def _get_request(self, args, kwargs):
        return args[0].request


# 用于仅使用于理赔人员的交互式命令
class ClaimRequired(OpenidRequired):
    def _get_openid(self, args, kwargs):
        return args[0].open_id

    def _get_user(self, openid):
        # Claim
        count = Claim.objects(wx_id=openid).count()
        return count

    def _get_request(self, args, kwargs):
        return args[0].request


# 用于仅使用于律师的交互式命令
class LawyerRequired(OpenidRequired):
    def _get_openid(self, args, kwargs):
        return args[0].open_id

    def _get_user(self, openid):
        count = Lawyer.objects(wx_id=openid).count()
        return count

    def _get_request(self, args, kwargs):
        return args[0].request


class WssTools(RequestTools):
    we_chat_tools = WeChatTools()
    string_tools = tools_string.StringTools()
    text_match = Match(0.6)
    platform_id = ""
    open_id = ""
    xml = None

    def check_signature(self):
        print("检测消息真实性")
        signature = self.request.GET.get('signature', None)   # 加密签名
        timestamp = self.request.GET.get('timestamp', None)   # 时间戳
        nonce = self.request.GET.get('nonce', None)           # 随机数
        return self.we_chat_tools.check_signature(signature=signature, timestamp=timestamp, nonce=nonce)

    def check_signature_request(self):
        #print(nonce)
        echostr = self.request.GET.get('echostr', None)   # 随即字符串
        if self.check_signature():
            # 若确认此次GET请求来自微信服务器，原样返回echostr参数内容，则介入生效，成为开发者成功，否则接入失败
            print("check success")
            return HttpResponse(echostr)
        else:
            print("非法请求")
            return HttpResponse("非法请求")

    def response_message(self):
        self.xml = ElementTree.fromstring(self.request.body)
        message_type = self.xml.find("MsgType").text
        self.platform_id = self.xml.find("ToUserName").text
        self.open_id = self.xml.find("FromUserName").text
        if not self.we_chat_tools.check_event(self.xml, self.request.body):
            print("重复的请求")
            return HttpResponse("Repeat request")
        # 通过消息类型，用对应的方法处理
        try:
            if message_type == "event":#事件消息
                return self.event_receiver()
            elif message_type == "text":#文字消息
                return self.message_receiver()
            elif message_type == "voice":#语音消息
                return self.voice_receiver()
            else:
                print("无效请求，MsgType：" + message_type)
                return HttpResponse("invalid request")
        except Exception as ex:
            print(traceback.format_exc())
            return self.we_chat_tools.text_response(to_user_name=self.open_id, from_user_name=self.platform_id, text=str(ex))

    # 事件处理
    # request.body的格式
    # <xml>
    # <ToUserName><![CDATA[toUser]]></ToUserName>
    # <FromUserName><![CDATA[FromUser]]></FromUserName>
    # <CreateTime>123456789</CreateTime>
    # <MsgType><![CDATA[event]]></MsgType>
    # <Event><![CDATA[subscribe]]></Event>
    # </xml>
    #  #

    def event_receiver(self):
        event = self.xml.find("Event").text

        # print("接收到事件："+event)
        if event == "subscribe":        # 关注事件
            return self.we_chat_tools.text_response(from_user_name=self.platform_id, to_user_name=self.open_id, text=self.string_tools.get_string("wechat_welcome"))
        elif event == "unsubscribe":        # 取消关注事件
            return self.we_chat_tools.text_response(from_user_name=self.platform_id, to_user_name=self.open_id, text=self.string_tools.get_string("wechat_unsubscribe"))
        elif event == "CLICK":      # 菜单拉取消息事件
            key = self.xml.find("EventKey").text
            return self.message_handler(key)
        elif event == "VIEW":       # 菜单链接跳转事件
            key = self.xml.find("EventKey").text
            return HttpResponse("success")
        elif event == "location":       # 地理位置推送事件
            label = self.xml.find("Label").text
            return self.we_chat_tools.text_response(from_user_name=self.platform_id, to_user_name=self.open_id, text=label)
        return self.we_chat_tools.text_response(from_user_name=self.platform_id, to_user_name=self.open_id, text="接收到事件"+event)

    # 文字消息处理
    # #
    def message_receiver(self):
        print("文字消息处理方法")
        content = self.xml.find("Content").text
        return self.message_handler(content)

    # 语音识别处理
    #  #
    def voice_receiver(self):
        try:
            media_id = self.xml.find("MediaId").text
            # print("MediaID:" + media_id)
            recognition = self.xml.find("Recognition").text
            return self.message_handler(message=recognition, event_type=EventType.voice)
        except Exception as ex:
            print("语音识别异常:" + str(ex))
            return self.we_chat_tools.text_response(from_user_name=self.platform_id, to_user_name=self.open_id, text="暂未开通")

    # 消息处理
    def message_handler(self, message, event_type=EventType.text):
        if message is not None:
            small_message = message.lower()         # 将Message转为小写使大小写不敏感
            print("接受到文字消息{0}".format(small_message))
            if small_message[0] == 'k':        # Message足够长并且首字母为k
                if len(small_message) >= self.we_chat_tools.KEY_LENGTH:
                    key = small_message[0:self.we_chat_tools.KEY_LENGTH]

                    if key == 'k0001':
                        # 绑定信息
                        return MessageHandler.bind(self)
                    elif key == 'k0002':
                        # 解绑信息
                        return MessageHandler.unbind(self)
                    elif key == 'k0003':
                        # 自动登录信息
                        print("消息为自动登录消息")
                        return MessageHandler.auto_login(self)
                    elif key == 'k3004':
                        # 联系客服
                        return MessageHandler.contact(self)
                    else:   # 没有匹配选项，返回帮助信息
                        return self.we_chat_tools.text_response(from_user_name=self.platform_id, to_user_name=self.open_id,
                                                                text=self.string_tools.get_string('wechat_text_helper'))
                else:
                    # print("is too short")
                    return self.we_chat_tools.text_response(from_user_name=self.platform_id, to_user_name=self.open_id,
                                                            text=self.string_tools.get_string('wechat_text_helper'))
            else:
                # print("go to text handler")
                return self.text_handler(message=small_message, event_type=event_type)
        # 如果没有成功匹配返回帮助信息
        if event_type == EventType.voice:
            return self.we_chat_tools.text_response(from_user_name=self.platform_id, to_user_name=self.open_id,
                                                    text=self.string_tools.get_string('wechat_voice_helper'))
        else:
            return self.we_chat_tools.text_response(from_user_name=self.platform_id, to_user_name=self.open_id,
                                                    text=self.string_tools.get_string('wechat_text_helper'))

    def text_handler(self, message, event_type):
        print("接收到消息:{0}".format(message))
        # if self.text_match.match(message, KEY_ATTENDANCE_TODAY.text):
        #     return get_today_attendance(from_user_name=open_id, to_user_name=platform_id)
        # elif text_match.match(message,KEY_EGGS.text):
        #     return text_response(from_user_name=platform_id,to_user_name=open_id,text="""<a href="%s">点击砸蛋</a>""" % URL_EGGS )
        # print("return help text")
        if event_type == EventType.voice:
            return self.we_chat_tools.text_response(from_user_name=self.platform_id, to_user_name=self.open_id,
                                                    text=self.string_tools.get_string('wechat_voice_helper'))
        else:
            return self.we_chat_tools.text_response(from_user_name=self.platform_id, to_user_name=self.open_id,
                                                    text=self.string_tools.get_string('wechat_text_helper'))


class MessageHandler:
    @staticmethod
    @LoginRequired
    def bind(wss_tool):
        return wss_tool.we_chat_tools.text_response(from_user_name=wss_tool.platform_id, to_user_name=wss_tool.open_id, text=wss_tool.string_tools.get_string('wechat_text_helper'))

    @staticmethod
    def unbind(wss_tool):
        return wss_tool.we_chat_tools.text_response(from_user_name=wss_tool.platform_id, to_user_name=wss_tool.open_id, text=wss_tool.string_tools.get_string('wechat_text_helper'))

    @staticmethod
    @LoginRequired
    def auto_login(wss_tool):
        return wss_tool.we_chat_tools.text_response(from_user_name=wss_tool.platform_id, to_user_name=wss_tool.open_id, text=wss_tool.string_tools.get_string('wechat_text_helper'))

    # 联系客服
    @staticmethod
    def contact(wss_tool):
        return wss_tool.we_chat_tools.text_response(from_user_name=wss_tool.platform_id, to_user_name=wss_tool.open_id, text=wss_tool.string_tools.get_string('wechat_contact'))





class ImageDataProcess():
    def __init__(self, type):
        self.type = type

    def split_image(self, image_data):
        try:
            split_point = image_data.find('base64') + 7
            # spliter = image_data[0:split_point]
            # print(spliter)
            images = image_data[split_point:]

            return images
        except:
            return []

    def save_image_file(self, images):
        now = datetime.datetime.now()
        format_date = now.strftime('%Y%m%d')
        # print(format_date)

        image_urls = ''
        # for image in images:
        raw_image = base64.b64decode(images)

        #防止文件过大
        MAX_FILE_SIZE = 5*1024*1024 #图片的最大尺寸，5M
        if len(raw_image) > MAX_FILE_SIZE:
            print("警告：文件尺寸过大，当前文件尺寸：{0}M".format(len(raw_image)/1024/1024))

        #生成文件的UUID
        file_uuid = str(uuid.uuid1())

        file_path = "{0}/static/pic/{1}/{2}/{3}".format(settings.BASE_DIR, self.type, format_date, file_uuid)
        base_dir = "{0}/static/pic/{1}".format(settings.BASE_DIR, self.type)
        file_dir = "{0}/static/pic/{1}/{2}".format(settings.BASE_DIR, self.type, format_date)
        file_url = 'pic/{0}/{1}/{2}'.format(self.type, format_date, file_uuid)

        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)

        file = open(file_path, 'wb')

        file.write(raw_image)
        file.close()
        # image_urls.append(file_url)

        return file_url


    #   验证认证
class DocumentWssTools(RequestTools):
    # print("开始正式验证：")
    # def validation_certificate(self, certificate):

    #   验证订单
    def validation_order(self, order):

        insure_type = self.get_parameter("insure_type", "")
        print('类型'+insure_type)
        client = Client.objects(user=self.request.user).first()
        if client:
            if ConvertTools.validate_choices(insure_type, InsuranceProducts.PRODUCT_TYPE):
                order.product_type = insure_type
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
                if startSiteName_prov and startSiteName_city:
                    order.startSiteName = startSiteName_prov + ' '+startSiteName_city
                else:
                    raise ParameterError('起运地不能为空')

                #目的地
                targetSiteName_prov = self.get_parameter('targetSiteName_prov').strip()
                targetSiteName_city = self.get_parameter('targetSiteName_city').strip()
                if targetSiteName_prov and targetSiteName_city:
                    order.targetSiteName = targetSiteName_prov + " " + targetSiteName_city
                else:
                    raise ParameterError('目的地不能为空')
                
                if order.targetSiteName == order.startSiteName :
                    raise ParameterError('起运地和目的地不能为同一地点')

                order.expectStartTime = datetime.now()


                if insure_type == 'car':
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
                elif insure_type == 'batch':

                    order.insurance_product = client.product_batch
                    order.company = client.product_batch.company
                    order.product_type = client.product_batch.product_type
                    print('订单类型'+str(order.product_type))
                    order.insurance_type = client.product_batch.insurance_type
                    order.insurance_rate = client.product_batch.rate


                    batch_plate_number = self.get_parameter('batch_plate_number').strip()
                    short = self.get_parameter('short').strip()
                    letter = self.get_parameter('letter').strip()
                    if batch_plate_number and short and letter:
                        if len(batch_plate_number) <= 10:
                            order.plate_number = short + letter + batch_plate_number
                        else:
                            raise ParameterError('您输入的车牌号不正确')
                    else:
                        raise ParameterError('车牌号不能为空')

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

                    if not position_list and not batch_image_list and not batch_file:
                        raise ParameterError("保险清单内容，二选一")


                elif insure_type == 'ticket':

                    order.insurance_product = client.product_ticket
                    order.company = client.product_ticket.company
                    order.product_type = client.product_ticket.product_type
                    order.insurance_type = client.product_ticket.insurance_type
                    order.insurance_rate = client.product_ticket.rate

                    ticket_transport_id = self.get_parameter('ticket_transport_id').strip()
                    if ticket_transport_id:
                        order.transport_id = ticket_transport_id

                    ticket_plate_number = self.get_parameter('ticket_plate_number').strip()
                    if ticket_plate_number:
                        if len(ticket_plate_number) <= 10:
                            order.plate_number = ticket_plate_number
                        else:
                            raise ParameterError('您输入的车牌号不正确')

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
                                raise ParameterError('货物数量请输入数字')
                        if ticket_commodityCases>0:
                            order.commodityCases = str(ticket_commodityCases)
                        else:
                            raise ParameterError('货物数量请输入大于零的数字')
                    else:
                        raise ParameterError('货物数量不能为空')
                else:
                    raise ParameterError('非法的产品类型')

                #保额
                insurance_price = None
                if order.product_type == 'car' or order.product_type == 'ticket':
                    insurance_price = self.get_parameter('insurance_price').strip()
                if order.product_type == 'batch':
                    insurance_price = self.get_parameter('batch_insurance_price').strip()
                if insurance_price:
                    insurance_price = int(float(insurance_price) * 100)
                    if insurance_price:
                        if order.product_type == 'car':
                            if insurance_price > 200000000:
                                raise ParameterError('货物价值上限2000000元')
                            elif insurance_price <= 100000:
                                insurance_price = 100000
                            else:
                                insurance_price = insurance_price
                        elif order.product_type == 'batch':
                            if insurance_price > 200000000:
                                raise ParameterError('货物价值上限2000000元')
                            else:
                                insurance_price = insurance_price
                        elif order.product_type == 'ticket':
                            if insurance_price > 200000000:
                                raise ParameterError('货物价值超过200万元，请与客服联系，线下处理')
                            elif insurance_price <= 200000:
                                insurance_price = 200000
                            else:
                                insurance_price = insurance_price
                        else:
                            raise ParameterError("投保的产品不存在")
                        order.insurance_price = insurance_price
                    else:
                        raise ParameterError('保额最多填写俩位小数')
                else:
                    raise ParameterError('保额不能为空')
            else:
                raise ParameterError('用户不存在')

        return order




    #   验证订单
    def validation_order_batch(self, order):
#         insure_type = self.get_parameter("insure_type", "")
  #      client = Client.objects(id='574e37d79a8f2b0e2a811ff2').first()
        product_id = self.get_parameter("product_id", "")
        insurance_product_set = InsuranceProducts.objects()
        insurance_product_set = insurance_product_set.filter(Q(id= product_id )).first()
        insure_type = insurance_product_set.product_type
        client = Client.objects(user=self.request.user).first()

        if client:
            if ConvertTools.validate_choices(insure_type, InsuranceProducts.PRODUCT_TYPE):
                order.product_type = insure_type
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
                if startSiteName_prov and startSiteName_city and startSiteName_dist:
                    order.startSiteName = startSiteName_prov + ' '+startSiteName_city +' '+startSiteName_dist
                else:
                    raise ParameterError('起运地不能为空')

                #目的地
                targetSiteName_prov = self.get_parameter('targetSiteName_prov').strip()
                targetSiteName_city = self.get_parameter('targetSiteName_city').strip()
                targetSiteName_dist = self.get_parameter('targetSiteName_dist').strip()
                if targetSiteName_prov and targetSiteName_city and targetSiteName_dist:
                    order.targetSiteName = targetSiteName_prov + " " + targetSiteName_city +" "+targetSiteName_dist
                else:
                    raise ParameterError('目的地不能为空')
                #运输方式
                transport_type = self.get_parameter('transport_type_id').strip()
                if transport_type:
                    order.transport_type=transport_type
                else:
                    order.transport_type="1"
                

                order.expectStartTime = datetime.now()


                if insure_type == 'car':
                    order.insurance_product = insurance_product_set
                    order.company = insurance_product_set.company
                    order.product_type = insurance_product_set.product_type
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
                        try:
                            car_commodityCases=int(car_commodityCases)
                        except:
                            try:
                                car_commodityCases=float(car_commodityCases)
                            except:
                                raise ParameterError('货物数量请输入数字')
                        if car_commodityCases>0:
                            order.commodityCases = str(car_commodityCases)
                        else:
                            raise ParameterError('货物数量请输入大于零的数字')
#                         order.commodityCases = car_commodityCases
                    else:
                        raise ParameterError('货物数量不能为空')
                elif insure_type == 'batch':
                    order.insurance_product = insurance_product_set
                    order.company = insurance_product_set.company
                    order.product_type = insurance_product_set.product_type

#                     order.insurance_product = client.product_batch
#                     order.company = client.product_batch.company
#                     order.product_type = client.product_batch.product_type
                    print('订单类型'+str(order.product_type))
                    order.insurance_type = insurance_product_set.insurance_type
                    order.insurance_rate = insurance_product_set.rate


                    batch_plate_number = self.get_parameter('batch_plate_number').strip()
                    short = self.get_parameter('short').strip()
                    letter = self.get_parameter('letter').strip()
                    if batch_plate_number and short and letter:
                        if len(batch_plate_number) <= 10:
                            order.plate_number = short + letter + batch_plate_number
                        else:
                            raise ParameterError('您输入的车牌号不正确')
                    else:
                        raise ParameterError('车牌号不能为空')

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

                    if not position_list and not batch_image_list and not batch_file:
                        raise ParameterError("保险清单内容，二选一")


                elif insure_type == 'ticket':
                    order.insurance_product = insurance_product_set
                    order.company = insurance_product_set.company
                    order.product_type = insurance_product_set.product_type
                    order.insurance_type = insurance_product_set.insurance_type
#                     order.insurance_rate = client.product_ticket.rate
             
                    #车牌号
                    batch_plate_number = self.get_parameter('batch_plate_number').strip()
                    short = self.get_parameter('short').strip()
                    letter = self.get_parameter('letter').strip()
                    if batch_plate_number and short and letter:
                        if len(batch_plate_number) <= 10:
                            order.plate_number = short + letter + batch_plate_number
                        else:
                            raise ParameterError('您输入的车牌号不正确')
                    else:
                        raise ParameterError('车牌号不能为空')
                    #投保货物类型
                    good_type=self.get_parameter("good_type_id").strip()
                    if good_type:
                        order.good_type = good_type
                        #可投保货物详情
                        cargo_number=self.get_parameter("wx_cargo_number").strip()
                        if cargo_number:
                            product_cargo_set=ProductCargo.objects()
                            product_cargo_set=product_cargo_set.filter(product= insurance_product_set ,state = good_type )
                            cargo_set=Cargo.objects()
                            cargo_set=cargo_set.filter(cargo_number= cargo_number ).first()
                            for product_cargo in product_cargo_set:
                                if product_cargo.cargo == cargo_set:
                                    order.cargo=cargo_set
                                    break
                            if not order.cargo:
                                raise ParameterError('货物编码与投保货物类型不匹配')
                        else:
                            raise ParameterError('货物编码未填写')
                    else:
                        raise ParameterError('投保货物类型未填写')


                    ticket_transport_id = self.get_parameter('ticket_transport_id').strip()
                    if ticket_transport_id:
                        order.transport_id = ticket_transport_id

                    ticket_plate_number = self.get_parameter('ticket_plate_number').strip()
                    if ticket_plate_number:
                        if len(ticket_plate_number) <= 10:
                            order.plate_number = ticket_plate_number
                        else:
                            raise ParameterError('您输入的车牌号不正确')

                    if not ticket_transport_id and not ticket_plate_number:
                        raise ParameterError('车牌号和运单号至少填写一个')
                    
                    #包装方式
                    wx_pack_detail = self.get_parameter('wx_pack_detail_id').strip()
                    if wx_pack_detail:
                        order.pack_method = wx_pack_detail
                    else:
                        raise ParameterError('货物包装方式未选择')

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
                                raise ParameterError('货物数量请输入数字')
                        if ticket_commodityCases>0:
                            order.commodityCases = str(ticket_commodityCases)
                        else:
                            raise ParameterError('货物数量请输入大于零的数字')
                    else:
                        raise ParameterError('货物数量不能为空')
                else:
                    raise ParameterError('非法的产品类型')

                #保额
                insurance_price = None
                if order.product_type == 'car' or order.product_type == 'ticket':
                    insurance_price = self.get_parameter('insurance_price').strip()
                if order.product_type == 'batch':
                    insurance_price = self.get_parameter('batch_insurance_price').strip()
                if insurance_price:
                    try:
                        insurance_price = int(float(insurance_price) * 100)
                    except:
                        raise ParameterError('货物价值请输入数字，如:2000')
                    if insurance_price:
                        if order.product_type == 'car':
                            if insurance_price > 200000000:
                                raise ParameterError('货物价值上限2000000元')
                            elif insurance_price <= 100000:
                                insurance_price = 100000
                            else:
                                insurance_price = insurance_price
                        elif order.product_type == 'batch':
                            if insurance_price > 200000000:
                                raise ParameterError('货物价值上限2000000元')
                            else:
                                insurance_price = insurance_price
                        elif order.product_type == 'ticket':
                            if insurance_price > 200000000:
                                raise ParameterError('货物价值超过200万元，请与客服联系，线下处理')
                            elif insurance_price <= 200000:
                                insurance_price = 200000
                            else:
                                insurance_price = insurance_price
                        else:
                            raise ParameterError("投保的产品不存在")
                        order.insurance_price = insurance_price
                    else:
                        raise ParameterError('保额最多填写俩位小数')
                else:
                    raise ParameterError('保额不能为空')
            else:
                raise ParameterError('用户不存在')

        return order

















        # idp = ImageDataProcess('certificate')
        # national_image = self.request.POST.get('national_image_hidden', '')
        # if national_image:
        #     national_image = idp.split_image(national_image)
        #     national_image_url = idp.save_image_file(national_image)
        #     if national_image_url:
        #         certificate.national_image = national_image_url
        #         print("正面图片:"+certificate.national_image)
        #     else:
        #         raise ParameterError('保存身份证正面图片失败')
        # else:
        #     raise ParameterError('请选择添加身份证正面图片')
        #
        # national_image_down = self.request.POST.get('national_image_down_hidden', '')
        # if national_image_down:
        #     national_image_down = idp.split_image(national_image_down)
        #     national_image_down_url = idp.save_image_file(national_image_down)
        #     if national_image_down_url:
        #         certificate.national_image_down = national_image_down_url
        #         print("背面图片:"+certificate.national_image_down)
        #     else:
        #         raise ParameterError('保存身份证背面图片失败')
        # else:
        #     raise ParameterError('请选择添加身份证背面图片')
        #
        # user_type = self.get_parameter("user_type").strip()
        # if user_type:
        #     certificate.user_type = user_type
        #     print("认证目标:"+certificate.user_type)
        # else:
        #     raise ParameterError('认证目标不能为空')
        #
        # user_classify = self.get_parameter("user_classify").strip()
        # if user_classify:
        #     certificate.user_classify = user_classify
        #     print("认证类型:"+certificate.user_classify)
        #
        # if user_type == 'transport':
        #     business_license_image = self.request.POST.get('business_license_image_hidden', '')
        #     if business_license_image:
        #         business_license_image = idp.split_image(business_license_image)
        #         business_license_image_url = idp.save_image_file(business_license_image)
        #         if business_license_image_url:
        #             certificate.business_license_image = business_license_image_url
        #             print("营业执照正本图:"+certificate.business_license_image)
        #         else:
        #             raise ParameterError('保存营业执照正本图片失败')
        #     else:
        #         raise ParameterError('请选择添加营业执照正本图片')
        #
        #     organ_image = self.request.POST.get('organ_image_hidden', '')
        #     if organ_image:
        #         organ_image = idp.split_image(organ_image)
        #         organ_image_url = idp.save_image_file(organ_image)
        #         if organ_image_url:
        #             certificate.organ_image = organ_image_url
        #             print("组织机构代:"+certificate.organ_image)
        #         else:
        #             raise ParameterError('保存组织机构代码证失败')
        #
        #     operating_permit_image = self.request.POST.get('operating_permit_image_hidden', '')
        #     if operating_permit_image:
        #         operating_permit_image = idp.split_image(operating_permit_image)
        #         operating_permit_image_url = idp.save_image_file(operating_permit_image)
        #         if operating_permit_image_url:
        #             certificate.operating_permit_image = operating_permit_image_url
        #             print("道路运输经营:"+certificate.operating_permit_image)
        #         else:
        #             raise ParameterError('保存道路运输经营许可证失败')
        #     else:
        #         raise ParameterError('请选择添加道路运输经营许可证')
        #
        # elif user_type == 'driver':
        #     driver_image = self.request.POST.get('driver_image_hidden', '')
        #     if driver_image:
        #         driver_image = idp.split_image(driver_image)
        #         driver_image_url = idp.save_image_file(driver_image)
        #         if driver_image_url:
        #             certificate.driver_image = driver_image_url
        #             print("驾驶证:"+certificate.driver_image)
        #         else:
        #             raise ParameterError('保存驾驶证失败')
        #     else:
        #         raise ParameterError('请选择添加驾驶证')
        #
        #     plate_image = self.request.POST.get('plate_image_hidden', '')
        #     if plate_image:
        #         plate_image = idp.split_image(plate_image)
        #         plate_image_url = idp.save_image_file(plate_image)
        #         if plate_image_url:
        #             certificate.plate_image = plate_image_url
        #             print("行驶证:"+certificate.plate_image)
        #         else:
        #             raise ParameterError('保存行驶证失败')
        #     else:
        #         raise ParameterError('请选择添加行驶证')
        #
        #     transportation_image = self.request.POST.get('transportation_image_hidden', '')
        #     if transportation_image:
        #         transportation_image = idp.split_image(transportation_image)
        #         transportation_image_url = idp.save_image_file(transportation_image)
        #         if transportation_image_url:
        #             certificate.transportation_image = transportation_image_url
        #             print("道路运输:"+certificate.transportation_image)
        #         else:
        #             raise ParameterError('保存营运证失败')
        #     else:
        #         raise ParameterError('请选择添加营运证')
        # elif user_type == 'boss':
        #     if user_classify == 'units':
        #         business_license_image_boss = self.request.POST.get('business_license_image_boss_hidden', '')
        #         if business_license_image_boss:
        #             business_license_image_boss = idp.split_image(business_license_image_boss)
        #             business_license_image_boss_url = idp.save_image_file(business_license_image_boss)
        #             if business_license_image_boss_url:
        #                 certificate.business_license_image = business_license_image_boss_url
        #                 print("营业执照图:"+certificate.business_license_image)
        #             else:
        #                 raise ParameterError('保存营业执照图片失败')
        #         else:
        #             raise ParameterError('请选择添加营业执照图片')
        #
        #         organ_image = self.request.POST.get('organ_image_boss_hidden', '')
        #         if organ_image:
        #             organ_image = idp.split_image(organ_image)
        #             organ_image_url = idp.save_image_file(organ_image)
        #             if organ_image_url:
        #                 certificate.organ_image = organ_image_url
        #                 print("组织机构代码:"+certificate.organ_image)
        #             else:
        #                 raise ParameterError('保存组织机构代码证失败')
        # else:
        #     raise ParameterError('认证类型不正确')
        return certificate
    
    #   验证车辆
    def validation_create_car(self, create_car):
        plate_expiration_periods = self.get_parameter('id_plate_expiration_periods', '')     #行驶证校验有效至
        plate_images = self.request.FILES.getlist('id_plate_image_left', '')     #行驶证正页及副页照片
        commercial_image = self.request.FILES.get('id_commercial_image', '')    #商业险
        liability_image = self.request.FILES.get('id_liability_image', '')     #交强险
        start_date       = self.request.POST.get('start_date', '')  #选择起保年份
        short = self.request.POST.get('short', '') #微信端车牌
#         letter = self.request.POST.get('letter', '') 
        batch_plate_number = self.request.POST.get('batch_plate_number', '') 
        edit_hidden = self.get_parameter("edit_hidden").strip()
        
        if short  and batch_plate_number: #微信
            if re.match(r'^[a-z_A-Z_0-9]{5}$', batch_plate_number):
                create_car.plate_number = short+batch_plate_number.upper()
            else:
                raise ParameterError('牌照后5位必须由数字和字母组成')
        else:
                raise ParameterError('车牌不能为空')
        if plate_expiration_periods:
            create_car.plate_expiration_periods = plate_expiration_periods
        else:
            raise ParameterError('请选择行驶证校验时间')
        #行驶证
        image_tool = ImageTools()
        if edit_hidden:
            if plate_images:
                if  len(plate_images) == 2:
                        position = 0
                        imglist = create_car.plate_image_left
                        for batch_image in plate_images:
                                batch_image_url = image_tool.save(request_file=batch_image, file_folder=ImageFolderType.car, old_file=imglist[position])
                                if batch_image_url:
                                    create_car.plate_image_left[position]=batch_image_url
                                    position +=1
                                else:
                                    raise ParameterError('保存行驶证失败')
                else:
                         raise ParameterError('请上传行驶证正页与副页两张照片')
        else:
                if plate_images and len(plate_images) == 2:
                    for batch_image in plate_images:
                        batch_image_url = image_tool.save(request_file=batch_image, file_folder=ImageFolderType.car, old_file='')
                        if batch_image_url:
                            create_car.plate_image_left.append(batch_image_url)
                        else:
                            raise ParameterError('保存行驶证失败')
                else:
                    raise ParameterError('请上传行驶证正页与副页两张照片')
                

        #起保年份
        if start_date:
            create_car.start_date = start_date
        else:
             raise ParameterError('请选择起保年份')
        
           #交强险 
        if edit_hidden:
            if liability_image:
                liability_image_url = image_tool.save(request_file=liability_image, file_folder=ImageFolderType.car, old_file=create_car.liability_image)
                if liability_image_url :
                    create_car.liability_image  = liability_image_url 
                else:
                    raise ParameterError('保存交强险照片失败')
        else:
            if liability_image:
                    liability_image_url = image_tool.save(request_file=liability_image, file_folder=ImageFolderType.car, old_file='')
                    if liability_image_url :
                        create_car.liability_image  = liability_image_url 
                    else:
                        raise ParameterError('保存交强险照片失败')



        
        #商业险
        if edit_hidden:
            if commercial_image:
                    commercial_image_url = image_tool.save(request_file=commercial_image, file_folder=ImageFolderType.car, old_file=create_car.commercial_image)
                    if commercial_image_url :
                        create_car.commercial_image  = commercial_image_url 
                    else:
                        raise ParameterError('保存商业险照片图片失败')
        else:
             if commercial_image:
                    commercial_image_url = image_tool.save(request_file=commercial_image, file_folder=ImageFolderType.car, old_file='')
                    if commercial_image_url :
                        create_car.commercial_image  = commercial_image_url 
                    else:
                        raise ParameterError('保存商业险照片图片失败')
        return create_car
    
    def  validation_edit_car(self, car_list):
        plate_expiration_periods = self.get_parameter('njDate', '')     #行驶证校验有效至/年检时间
#         short = self.get_parameter('short', '') 
#         letter = self.get_parameter('letter', '') 
#         batch_plate_number = self.get_parameter('batch_plate_number', '') 
        jqDate = self.get_parameter('jqDate', '')   #商业
        jqDateend = self.get_parameter('jqDateend', '')   #商业
        syDate = self.get_parameter('syDate', '') #交强险
        syDateend = self.get_parameter('syDateend', '') #交强险

        
#         if short and letter and batch_plate_number: #微信
#             if len(batch_plate_number)==5 :
#                 if batch_plate_number.isalnum() or batch_plate_number.isnum():
#                     number = ProvinceCode[int(short)]+Letter[int(letter)]+batch_plate_number.upper()
#                     car_list.plate_number = number
#                 else:
#                     raise ParameterError('牌照后5位必须为数字和字母组合')
#             else:
#                 raise ParameterError('车牌号由七位组成')
#         else:
#                 raise ParameterError('车牌不能为空')
            
        if plate_expiration_periods:
            car_list.plate_expiration_periods = plate_expiration_periods
        else:
            raise ParameterError('请选择行驶证年检时间')

        if jqDate:
            car_list.liability_date_start = jqDate
        else:
            raise ParameterError('请选择交强险开始时间')
        
        if jqDateend:
            car_list.liability_date_stop = jqDateend
        else:
            raise ParameterError('请选择交强险到期时间')
        
        start = time.mktime(time.strptime(jqDate,'%Y-%m-%d'))
        end =  time.mktime(time.strptime(jqDateend,'%Y-%m-%d'))
        if start > end :
            raise ParameterError('交强险开始时间不能大于结束时间')
        if syDate:
            car_list.commercial_date_start = syDate
        else:
            raise ParameterError('请选择商业险开始时间')
        
        if syDateend:
            car_list.commercial_date_stop = syDateend
        else:
            raise ParameterError('请选择商业险到期时间')
        starts = time.mktime(time.strptime(syDate,'%Y-%m-%d'))
        ends =  time.mktime(time.strptime(syDateend,'%Y-%m-%d'))
        if starts > ends :
            raise ParameterError('商业险开始时间不能大于结束时间')
        return car_list
    
      
    def wss_validation_order(self, order):

        product_type = self.get_parameter("product_type", "")

        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()

        order_type = self.get_parameter("order_type", "")

        client = Client.objects(user=self.request.user).first()
        if client:
            if ConvertTools.validate_choices(product_type, InsuranceProducts.PRODUCT_TYPE):
                order.product_type = product_type
                order.client = client
                order.state = 'wait'
                
                #投保人姓名
                client_name = self.get_parameter('client_name').strip()
                if client_name:
                    order.client_name = client_name
                else:
                    if client.company_name:
                        order.client_name = client.company_name
                    elif client.name:
                        order.client_name = client.name
                    else:
                        raise ParameterError('请输入投保人姓名')
                    
                #投保人身份证号
#                 client_id_card = self.get_parameter('client_id_card').strip()
#                 if client_id_card:
#                     order.client_id_card = client_id_card
#                 else:
#                     if client.national_id:
#                         order.client_id_card = client.national_id
#                     else:
#                         raise ParameterError('请输入投保人证件号，个人输入身份证号，单位输入组织机构代码证号')
#                     
                #被投保人身份
                client_type=self.get_parameter("wx_client_type").strip()
                client_detail=''
                if client_type:
                    if client_type== '货主':
                        client_detail='person'
                    if client_type == '物流公司':
                        client_detail='company'
                    order.client_type = client_detail
                else:
                    raise ParameterError('被保险人身份不能为空')
                
                
                #是否同投保人
                ismatchtbr1 = self.get_parameter('ismatchtbr1', '').strip()#是否同行驶证
                if ismatchtbr1 == 'on':
                    order.insured = order.client_name
#                     order.insured_id_card = order.client_id_card
                else:
                    #被保人姓名
                    insured = self.get_parameter('insured').strip()
                    if insured:
                        order.insured = insured
                    else:
                        if client.company_name:
                            order.insured = client.company_name
                        elif client.name:
                            order.insured = client.name
                        else:
                            raise ParameterError('请输入被保险人姓名')
                        
                    #被投保人身份证号
#                     insured_id_card = self.get_parameter('insured_id_card').strip()
#                     if insured_id_card:
#                         order.insured_id_card = insured_id_card
#                     else:
#                         if order.client_id_card:
#                             order.insured_id_card = order.client_id_card
#                         else:
#                             raise ParameterError('请输入被保险人证件号，个人输入身份证号，单位输入组织机构代码证号。')   
#             
                #起运地
                startSiteName_prov = self.get_parameter('startSiteName_prov').strip()
                if startSiteName_prov:
                    areas = startSiteName_prov.split(" ")
                    try:
                        start_cargoshen = CargoArea.objects(Q(name__contains=areas[0]) )
                    except:
                        raise ParameterError('未查找到当前起运地地址')
                    for start_cargoshenobj in start_cargoshen:
                            if start_cargoshenobj.level =='1':
                               startSiteName_prov_code = start_cargoshenobj.code 
                    i = 1
                    s_list = [] 
                    for area in areas:
                        k = i
                        if i==1:
                            try:
                                cargoAreaObj = CargoArea.objects.get(level =str(k) ,name=area)
                            except:
                                raise ParameterError('未查找到当前起运地地址2')
                        else:
                            try:
                                cargoAreaObj = CargoArea.objects.get(level =str(k) ,name=area,parentcode=s_list[k-2])
                            except:
                                raise ParameterError('未查找到当前起运地地址3')
                        i+=1
                        s_list.append(cargoAreaObj['code']) 
                    order.startSiteName = " ".join(s_list)  
                else:
                    raise ParameterError('起运地不能为空')


                #目的地
                targetSiteName_prov = self.get_parameter('targetSiteName_prov').strip()
                if targetSiteName_prov:
                    targetAreas = targetSiteName_prov.split(" ")
                    target_cargoshen = CargoArea.objects(Q(name__contains=targetAreas[0]) )
                    for target_cargoshenobj in target_cargoshen:
                            if target_cargoshenobj.level =='1':
                               targetSiteName_prov_code = target_cargoshenobj.code 
                    j = 1
                    t_list=[] 
                    for area in targetAreas:
                        k=j
                        if j==1:
                            cargoAreaObj = CargoArea.objects.get(level =str(k) ,name=area)
                        else:
                            cargoAreaObj = CargoArea.objects.get(level =str(k) ,name=area,parentcode=t_list[k-2])
                        j+=1
                        t_list.append(cargoAreaObj['code']) 
                    order.targetSiteName = " ".join(t_list)  
                else:
                    raise ParameterError('目的地不能为空')
                #微信段不能投保一个地方
                if order.targetSiteName == order.startSiteName :
                    raise ParameterError('起运地和目的地不能为同一地点')
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
                    order.transport_type=str(1)                 
                    #货物价值
                    batch_insurance_price =  self.get_parameter('batch_insurance_price').strip()
                    if batch_insurance_price:
                         new_batch_insurance_price =int(batch_insurance_price.rstrip("万"))*10000
                         order.insurance_price = int(new_batch_insurance_price*100)
                    else:
                         raise ParameterError('货物价值不能为空')

#下面一行是原来代码
#                     insuranceProducts = InsuranceProducts.objects(product_type=product_type,is_hidden=False)
                    insuranceProducts=[]
                    insuranceProduct_list = InsuranceProducts.objects(product_type=product_type,is_hidden=False)
                    for insuranceProduct_set in insuranceProduct_list:
                        if client_detail  in insuranceProduct_set.user_type_list:
                            insuranceProducts.append(insuranceProduct_set)
                    
#测试结束
                    productbatchsite = []
                    resultbatch = []
                    if insuranceProducts:
                           for insuranceProductsobj in insuranceProducts:
                                         if startSiteName_prov_code in insuranceProductsobj.no_insurable_route or targetSiteName_prov_code  in insuranceProductsobj.no_insurable_route:
                                                             continue
                                         else:
                                                             productbatchsite.append(insuranceProductsobj)
                           if  productbatchsite:
                                      for productbatchsiteobj in productbatchsite:
                                               if new_batch_insurance_price>productbatchsiteobj.insurance_price_max/100 or new_batch_insurance_price <productbatchsiteobj.insurance_price_min/100:
                                                                    continue
                                               else:
                                                                resultbatch.append(productbatchsiteobj)
                           else:
                                  raise ParameterError('此路线没有对应的产品')
                            
                           if resultbatch:
                               pass
#                                   resultbatch.sort(key = operator.attrgetter("priority"))  
#                                   order.insurance_product = resultbatch[0]
#                                   order.company = resultbatch[0].company
#                                   order.product_type = resultbatch[0].product_type
#                                   order.insurance_type = resultbatch[0].insurance_type
#                                   order.insurance_rate = resultbatch[0].rate
                           else:
                                 raise ParameterError('抱歉，根据您填写的条件，没有筛选出可以承保的产品！')
                                  
                                            
                    else:
                            raise ParameterError('无此产品类型的产品')
                     
                    #车牌号
                    batch_plate_number = self.get_parameter('batch_plate_number').strip()
                    short = self.get_parameter('short').strip()
#                     letter = self.get_parameter('letter').strip()
                    if order_type == "edit":
                            if batch_plate_number and short:
                                if len(batch_plate_number) <= 10:
                                    if re.match(r'^[a-z_A-Z_0-9]{5}$', batch_plate_number):
                                            batch_plate_number = batch_plate_number.upper()
                                            order.plate_number = short +  batch_plate_number
                                    else:
                                       raise ParameterError('您输入的车牌号不正确，请输入五位英文或数字')
                                else:
                                    raise ParameterError('您输入的车牌号不正确')
                    else:
                            if batch_plate_number and short:
                                if len(batch_plate_number) <= 10:
                                    if re.match(r'^[a-z_A-Z_0-9]{5}$', batch_plate_number):
                                            batch_plate_number = batch_plate_number.upper()
                                            order.plate_number = short + batch_plate_number
                                    else:
                                       raise ParameterError('您输入的车牌号不正确，请输入英文或数字')
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
                                    raise ParameterError("保险清单内容，二选一")
                    else:       
                                if not position_list and not batch_image_list and not batch_file:
                                    raise ParameterError("保险清单内容，二选一")
                elif product_type == 'ticket':
                    
                     #货物类型
                     wx_cargo_detail = self.get_parameter('wx_cargo_detail').strip()
                     if not  wx_cargo_detail:
                           raise ParameterError('货物类型不能为空')
                       
                      #包装方式
                     wx_pack_detail_id = self.get_parameter('wx_pack_detail_id').strip()
                     if wx_pack_detail_id:
                          wx_pack = wx_pack_detail_id.split(" ")
                          pack_method_list=order.PACK_METHOD
                          flag = False
                          for pack_method in pack_method_list:
                              for pack in pack_method[1]:
                                  if wx_pack[1]  == pack[1]:
                                      order.pack_method = pack[0]
                                      flag = True
                                      break  
                              if flag ==  True: 
                                  break         
                     else:
                           raise ParameterError('包装方式不能为空')   
                       
                       
                    #运输方式
                     transport_type = self.get_parameter('transport_type_id').strip()
                     if transport_type:
                            #运输方式翻译
                            try:
                                transport_type_list1=order.TRANSPORT_TYPE
                                number = ""
                                test =0
                                for transport_type_set in transport_type_list1:
                                    if transport_type_set[1]==transport_type:
                                        number=transport_type_set[0]
                                        test=1
                                        break
                                if test ==1:
                                    order.transport_type=str(number)
                                else:
                                    message='传值过程中运输方式翻译失败，请查看运输编号'+str(transport_type)
                                    raise ParameterError(message)
            #                         extraInfo_detail["transportType"]="汽运"#.encode("utf8")
                            except:
                                message='传值过程中运输方式翻译失败，请查看运输编号'+str(transport_type)
                                raise ParameterError(message)
                     else:
                        order.transport_type="1"
                       
                       
                     #货物价值
                     insurance_price = self.get_parameter('insurance_price').strip()
                     if insurance_price and insurance_price.isdigit():
                            try:
                                order.insurance_price = int(float(insurance_price)*100)
                            except:
                                raise ParameterError('货物价值请输入数字')            
                     else:
                         raise ParameterError('货物价值不能为空，且只能输入数字')
                                         
                   #运单号
                     ticket_transport_id = self.get_parameter('ticket_transport_id').strip()
                     if ticket_transport_id:
                         if len(ticket_transport_id)>20:
                             raise ParameterError('运单号不能超过20位')
                         #zh_pattern = re.compile(u'[\u4e00-\u9fa5]+').search(ticket_transport_id)
                         test2=re.match(r'^[a-zA-Z0-9 a - z A - Z 0 - 9 \u4e00-\u9fa5]+$', str(ticket_transport_id))
                         if re.match(r'^[a-z_A-Z_0-9_\u4e00-\u9fa5]+$', ticket_transport_id):
                             order.transport_id = ticket_transport_id
                         else:
                             raise ParameterError('运单号不能输入特殊字符')
                     #货物名称
                     ticket_commodityName = self.get_parameter('ticket_commodityName').strip()
                     if ticket_commodityName:
                        order.commodityName = ticket_commodityName
                     else:
                        raise ParameterError('货物名称不能为空')
                     #货物数量
                     ticket_commodityCases = self.get_parameter('ticket_commodityCases').strip()
                     if ticket_commodityCases:
                        try:
                            ticket_commodityCases=int(ticket_commodityCases)
                        except:
                            try:
                                ticket_commodityCases=float(ticket_commodityCases)
                            except:
                                raise ParameterError('货物数量请输入数字')
                        if ticket_commodityCases>0:
                            order.commodityCases = str(ticket_commodityCases)
                        else:
                            raise ParameterError('货物数量请输入大于零的数字')
                     else:
                        raise ParameterError('货物数量不能为空')
                     #车牌号
                     batch_plate_number = self.get_parameter('batch_plate_number').strip()
                     short = self.get_parameter('short').strip()
#                      letter = self.get_parameter('letter').strip()

                     if batch_plate_number and short:
                                if len(batch_plate_number) <= 10:
                                    if re.match(r'^[a-z_A-Z_0-9]{5}$', batch_plate_number):
                                            batch_plate_number = batch_plate_number.upper()
                                            order.plate_number = short + batch_plate_number
                                    else:
                                       raise ParameterError('您输入的车牌号不正确，请输入英文或数字') 
                                else:
                                            raise ParameterError('您输入的车牌号不正确')


                     if not ticket_transport_id and  not batch_plate_number:
                        raise ParameterError('车牌号和运单号至少填写一个！')
                     #过滤
                     resultlist5 = []
                     productCargosite = []#根据货物类型和起运地目的地筛选出可保产品
                     productCargo= []#根据可保范围筛选出产品
                     cargo =Cargo.objects(cargo_name=wx_cargo_detail).first()
                     if  cargo:          
                                     order.cargo = cargo                                              
                                     productCargoall= ProductCargo.objects(cargo=cargo)  
                                     if productCargoall:
                                         for productCargoallobj in productCargoall:
                                                      if startSiteName_prov_code in productCargoallobj.product.no_insurable_route or targetSiteName_prov_code  in productCargoallobj.product.no_insurable_route:
                                                             continue
                                                      else:
                                                             productCargosite.append(productCargoallobj)  
                                     else:
                                          raise ParameterError('此货物类型没有可保产品')
                                     if productCargosite:
                                                     for productCargositeobj in productCargosite:
                                                           if float(insurance_price)>productCargositeobj.product.insurance_price_max/100 or float (insurance_price)<productCargositeobj.product.insurance_price_min/100:
                                                                    continue
                                                           else:
                                                               if  productCargositeobj.product.is_hidden == False:
                                                                        productCargo.append(productCargositeobj)
                                     else:
                                          raise ParameterError('此路线没有可保产品')
                                                                                                                  
                                     if productCargo:             
                                             if    len(productCargo)==1:
                                                  test_a=0
                                                  for  rate  in   productCargo[0].product.product_rate_list:
                                                                     if rate.good_type == productCargo[0].state:
                                                                         test_a=1
                                                  if test_a == 0:
                                                      raise ParameterError('4001-A,无符合条件的产品。')
                                                                         
#                                                                                  order.insurance_company_rate = rate.insurance_rate
#                                                                                  order.insurance_company_price = int(rate.insurance_rate* 10000000 / 10000000 *float(insurance_price)*100)
#                                                                                  order.old_price =int(rate.products_rate* 10000000 / 10000000 *float(insurance_price)*100)
#                                                                                  order.insurance_product =  productCargo[0].product
#                                                                                  order.insurance_rate = rate.products_rate
#                                                                                  order.commission_ratio =rate.commission_ratio
#                                                                                  order.good_type = rate.good_type
#                                                                                  order.company =  productCargo[0].product.company
#                                                                                  order.product_type = productCargo[0].product.product_type
#                                                                                  #2017/06/12修正微信端下单未保存险种类型的错误
#                                                                                  order.insurance_type = productCargo[0].product.insurance_type
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
#********************************2017/6/9添加测试字段***************************
                                                          insurance_product_list=[]
                                                          if resultlist5:
                                                              for insuranceProduct_set in resultlist5:
                                                                  if client_detail  in insuranceProduct_set.product.user_type_list:
                                                                      insurance_product_list.append(insuranceProduct_set)
                                                              if len(insurance_product_list)>0:
                                                                  resultlist5=insurance_product_list
                                                              else:
                                                                  raise ParameterError('无符合条件的产品。')
                                                            
                                                         
#**********************************测试结束*********************************************                                                                                                                           
                                                          resultlist5.sort(key = operator.attrgetter("product.priority"))                     
                                                          if resultlist5:
                                                              pass
#                                                                  for  rate  in   resultlist5[0].product.product_rate_list:
#                                                                      if rate.good_type == resultlist5[0].state:
#                                                                              order.insurance_company_rate = rate.insurance_rate
#                                                                              order.insurance_company_price = int(rate.insurance_rate* 10000000 / 10000000 *float(insurance_price)*100)
#                                                                              order.old_price = int(rate.products_rate* 10000000 / 10000000 *float(insurance_price)*100)
#                                                                              order.insurance_product =   resultlist5[0].product
#                                                                              order.insurance_rate = rate.products_rate
#                                                                              order.commission_ratio =rate.commission_ratio
#                                                                              order.good_type = rate.good_type
#                                                                              order.company =  resultlist5[0].product.company
#                                                                              order.product_type = resultlist5[0].product.product_type
#                                                                              #2017/06/12修正微信端下单未保存险种类型的错误
#                                                                              order.insurance_type = resultlist5[0].product.insurance_type
                                                          else:
                                                             raise ParameterError('无符合条件的产品')
                                             else:
                                                 raise ParameterError('无此货物类型的产品')                                       
                                     else:
                                           raise ParameterError('抱歉，根据您填写的条件，没有筛选出可以承保的产品！')
                     else:
                         raise ParameterError('无此货物类型对应的产品')
    
                else:
                    raise ParameterError('非法的产品类型')
            else:
                raise ParameterError('用户不存在')

        return order
    
    #2017/6/21添加计算筛选出产品的价格信息
    def count_coupon(self, order,insurance_product):
        use_coupon_set = UseCoupon.objects(client=order.client)#优惠卷
        insurance_price= order.insurance_price#货物价值
        #old_price
        if order.product_type=='batch' or order.product_type=='car'  :
            insurance_rate=insurance_product.rate
        else:
            productCargo_detail= ProductCargo.objects(cargo=order.cargo,product =insurance_product ) .first()
            a=insurance_product.product_rate_list
            for product_rate in insurance_product.product_rate_list: 
                a=productCargo_detail.state
                b=product_rate.good_type
                if product_rate.good_type==productCargo_detail.state:
                    insurance_rate=product_rate.products_rate
                    break
        old_price = math.ceil(insurance_rate*1000000000 * float(insurance_price)/1000000000)
        #2017/6/7汇聚宝对接添加部分end         
        pay_price = 0
        self.insurance_rate = insurance_rate
        if use_coupon_set:
            temp = 1.0
            item = None
            for use_coupon in use_coupon_set:
                if use_coupon.coupon.product == insurance_product:
                    if use_coupon.coupon.rate < temp:
                        if use_coupon.coupon.end_date > datetime.now():
                            temp = use_coupon.coupon.rate
                            item = use_coupon.coupon
            if temp and item:
                pay_price = round(old_price* 1000000 / 1000000 * temp )
            else:
                pay_price = round(old_price* 1000000 / 1000000 * temp )
        else:
            pay_price = round(old_price * 1000000 / 1000000 )
        #2017/6/7汇聚宝对接添加部分
        if  pay_price<insurance_product.lowest_price:
            pay_price=insurance_product.lowest_price

        price = pay_price
        old_price = old_price
        return price
    
    #2017/6/21筛选订单可保产品
    def wss_validation_insurable_products(self, order):
        product_type = order.product_type
        client_detail = order.client_type
        client = order.client
        order_type = self.get_parameter("order_type", "")
        #货物价值
        insurance_price = order.insurance_price
         #起运地
        areas = order.startSiteName.split(" ")
        startSiteName_prov_code=areas[0]
         #目的地
        targetAreas  = order.targetSiteName.split(" ")
        targetSiteName_prov_code=targetAreas[0]
        if client:
            if ConvertTools.validate_choices(product_type, InsuranceProducts.PRODUCT_TYPE):
                order.product_type = product_type
                order.client = client
                order.state = 'wait'
                #不同产品类型处理
                if product_type == 'car':
                    pass
                elif product_type == 'batch':                   
                    #货物价值
                    batch_insurance_price =  order.insurance_price
                    insuranceProducts=[]
                    insuranceProduct_list = InsuranceProducts.objects(product_type=product_type,is_hidden=False)
                    for insuranceProduct_set in insuranceProduct_list:
                        if client_detail  in insuranceProduct_set.user_type_list:
                            insuranceProducts.append(insuranceProduct_set)
                            
                    productbatchsite = []
                    resultbatch = []
                    if insuranceProducts:
                           for insuranceProductsobj in insuranceProducts:
                                         if startSiteName_prov_code in insuranceProductsobj.no_insurable_route or targetSiteName_prov_code  in insuranceProductsobj.no_insurable_route:
                                                             continue
                                         else:
                                                             productbatchsite.append(insuranceProductsobj)
                           if  productbatchsite:
                                      for productbatchsiteobj in productbatchsite:
                                               if batch_insurance_price>productbatchsiteobj.insurance_price_max or batch_insurance_price <productbatchsiteobj.insurance_price_min:
                                                                    continue
                                               else:
                                                                resultbatch.append(productbatchsiteobj)
                           else:
                                  raise ParameterError('此路线没有对应的产品')
                            
                           if resultbatch:
                               resultbatch.sort(key = operator.attrgetter("priority"))  
                               insurable_products_list=[]
                               for product_set in resultbatch:
                                  data={}
                                  data['product']=product_set
                                  price=self.count_coupon(order, product_set)
                                  data['price']=self.count_coupon(order, product_set)
                                  insurable_products_list.append(data)
                               pass
#                                   resultbatch.sort(key = operator.attrgetter("priority"))  
#                                   order.insurance_product = resultbatch[0]
#                                   order.company = resultbatch[0].company
#                                   order.product_type = resultbatch[0].product_type
#                                   order.insurance_type = resultbatch[0].insurance_type
#                                   order.insurance_rate = resultbatch[0].rate
                           else:
                                 raise ParameterError('抱歉，根据您填写的条件，没有筛选出可以承保的产品！')
                    else:
                            raise ParameterError('无此产品类型的产品')

                elif product_type == 'ticket':
#                      #货物价值
#                      insurance_price = order.insurance_price
#                      #起运地
#                      areas = order.startSiteName.split(" ")
#                      startSiteName_prov_code=areas[0]
#                      #目的地
#                      targetAreas  = order.targetSiteName.split(" ")
#                      targetSiteName_prov_code=targetAreas[0]

                     
                     #过滤
                     resultlist5 = []
                     productCargosite = []
                     productCargo= []
                     cargo =order.cargo
                     if  cargo:                                            
                                     productCargoall= ProductCargo.objects(cargo=cargo)  
                                     if productCargoall:
                                         for productCargoallobj in productCargoall:
                                                      if startSiteName_prov_code in productCargoallobj.product.no_insurable_route or targetSiteName_prov_code  in productCargoallobj.product.no_insurable_route:
                                                             continue
                                                      else:
                                                             productCargosite.append(productCargoallobj)  
                                     else:
                                          raise ParameterError('此货物类型没有可保产品')
                                     if productCargosite:
                                                     for productCargositeobj in productCargosite:
                                                           if float(insurance_price)>productCargositeobj.product.insurance_price_max or float (insurance_price)<productCargositeobj.product.insurance_price_min:
                                                                    continue
                                                           else:
                                                               if  productCargositeobj.product.is_hidden == False:
                                                                        productCargo.append(productCargositeobj)
                                     else:
                                          raise ParameterError('此路线没有可保产品')
                                     test= len(productCargo)                                                                                   
                                     if productCargo:
                                             insurable_products_list=[]       
                                             test= len(productCargo)      
                                             if    len(productCargo)==1:
                                                  for  rate  in   productCargo[0].product.product_rate_list:
                                                                     if rate.good_type == productCargo[0].state:
                                                                         data={}
                                                                         data['product']=productCargo[0].product
                                                                         price=self.count_coupon(order, productCargo[0].product)
                                                                         data['price']=self.count_coupon(order, productCargo[0].product)
                                                                         insurable_products_list.append(data)
                                                                         

#                                                                                  order.insurance_company_rate = rate.insurance_rate
#                                                                                  order.insurance_company_price = int(rate.insurance_rate* 10000000 / 10000000 *float(insurance_price)*100)
#                                                                                  order.old_price =int(rate.products_rate* 10000000 / 10000000 *float(insurance_price)*100)
#                                                                                  order.insurance_product =  productCargo[0].product
#                                                                                  order.insurance_rate = rate.products_rate
#                                                                                  order.commission_ratio =rate.commission_ratio
#                                                                                  order.good_type = rate.good_type
#                                                                                  order.company =  productCargo[0].product.company
#                                                                                  order.product_type = productCargo[0].product.product_type
#                                                                                  #2017/06/12修正微信端下单未保存险种类型的错误
#                                                                                  order.insurance_type = productCargo[0].product.insurance_type
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
#********************************2017/6/9添加测试字段***************************
                                                          insurance_product_list=[]
                                                          if resultlist5:
                                                              for insuranceProduct_set in resultlist5:
                                                                  if client_detail  in insuranceProduct_set.product.user_type_list:
                                                                      insurance_product_list.append(insuranceProduct_set)
                                                              if len(insurance_product_list)>0:
                                                                  resultlist5=insurance_product_list
                                                              else:
                                                                  raise ParameterError('无符合条件的产品。')
                                                            
                                                         
#**********************************测试结束*********************************************                                                                                                                           
                                                          resultlist5.sort(key = operator.attrgetter("product.priority"))                     
                                                          if resultlist5:
                                                              insurable_products_list=[]
                                                              for product_set in resultlist5:
                                                                  data={}
                                                                  data['product']=product_set.product
                                                                  price=self.count_coupon(order, product_set.product)
                                                                  data['price']=self.count_coupon(order, product_set.product)
                                                                  insurable_products_list.append(data)
#                                                                  for  rate  in   resultlist5[0].product.product_rate_list:
#                                                                      if rate.good_type == resultlist5[0].state:
#                                                                              order.insurance_company_rate = rate.insurance_rate
#                                                                              order.insurance_company_price = int(rate.insurance_rate* 10000000 / 10000000 *float(insurance_price)*100)
#                                                                              order.old_price = int(rate.products_rate* 10000000 / 10000000 *float(insurance_price)*100)
#                                                                              order.insurance_product =   resultlist5[0].product
#                                                                              order.insurance_rate = rate.products_rate
#                                                                              order.commission_ratio =rate.commission_ratio
#                                                                              order.good_type = rate.good_type
#                                                                              order.company =  resultlist5[0].product.company
#                                                                              order.product_type = resultlist5[0].product.product_type
#                                                                              #2017/06/12修正微信端下单未保存险种类型的错误
#                                                                              order.insurance_type = resultlist5[0].product.insurance_type
                                                          else:
                                                             raise ParameterError('无符合条件的产品')
                                             else:
                                                 raise ParameterError('无此货物类型的产品')                                       
                                     else:
                                           raise ParameterError('抱歉，根据您填写的条件，没有筛选出可以承保的产品！')
                     else:
                         raise ParameterError('无此货物类型对应的产品')
    
                else:
                    raise ParameterError('非法的产品类型')
            else:
                raise ParameterError('用户不存在')

        return insurable_products_list
       
    def wss_validation_order1(self, order):

        product_type = self.get_parameter("product_type", "")

        client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()

        order_type = self.get_parameter("order_type", "")

        #client = Client.objects(user=self.request.user).first()
        if client:
            if ConvertTools.validate_choices(product_type, InsuranceProducts.PRODUCT_TYPE):
                order.product_type = product_type
                order.client = client
                
                #投保人姓名
                client_name = self.get_parameter('client_name').strip()
                if client_name:
                    order.client_name = client_name
                else:
                    if client.company_name:
                        order.client_name = client.company_name
                    elif client.name:
                        order.client_name = client.name
                    else:
                        raise ParameterError('请输入投保人姓名')
                    
                #投保人身份证号
                client_id_card = self.get_parameter('client_id_card').strip()
                if client_id_card:
                    order.client_id_card = client_id_card
                else:
                    if client.national_id:
                        order.client_id_card = client.national_id
                    else:
                        raise ParameterError('请输入投保人证件号，个人输入身份证号，单位输入组织机构代码证号')
                    
                #投保人身份
                client_type=self.get_parameter("wx_client_type").strip()
                client_detail=''
                if client_type:
                    if client_type== '货主':
                        client_detail='person'
                    if client_type == '物流公司':
                        client_detail='company'
                    order.client_type = client_detail
                else:
                    raise ParameterError('投保人身份不能为空')
                
                
                #是否同投保人
                ismatchtbr1 = self.get_parameter('ismatchtbr1', '').strip()#是否同行驶证
                if ismatchtbr1 == 'on':
                    order.insured = order.client_name
                    order.insured_id_card = order.client_id_card
                else:
                    #被保人姓名
                    insured = self.get_parameter('insured').strip()
                    if insured:
                        order.insured = insured
                    else:
                        if client.company_name:
                            order.insured = client.company_name
                        elif client.name:
                            order.insured = client.name
                        else:
                            raise ParameterError('请输入被保险人姓名')
                        
                    #被投保人身份证号
                    insured_id_card = self.get_parameter('insured_id_card').strip()
                    if insured_id_card:
                        order.insured_id_card = insured_id_card
                    else:
                        if order.client_id_card:
                            order.insured_id_card = order.client_id_card
                        else:
                            raise ParameterError('请输入被保险人证件号，个人输入身份证号，单位输入组织机构代码证号。')   
            
                #起运地
                startSiteName_prov = self.get_parameter('startSiteName_prov').strip()
                if startSiteName_prov:
                    areas = startSiteName_prov.split(" ")
                    start_cargoshen = CargoArea.objects(Q(name__contains=areas[0]) )
                    for start_cargoshenobj in start_cargoshen:
                            if start_cargoshenobj.level =='1':
                               startSiteName_prov_code = start_cargoshenobj.code 
                    i = 1
                    s_list = [] 
                    for area in areas:
                        k = i
                        if i==1:
                            cargoAreaObj = CargoArea.objects.get(level =str(k) ,name=area)
                        else:
                            cargoAreaObj = CargoArea.objects.get(level =str(k) ,name=area,parentcode=s_list[k-2])
                        i+=1
                        s_list.append(cargoAreaObj['code']) 
                    order.startSiteName = " ".join(s_list)  
                else:
                    raise ParameterError('起运地不能为空')


                #目的地
                targetSiteName_prov = self.get_parameter('targetSiteName_prov').strip()
                if targetSiteName_prov:
                    targetAreas = targetSiteName_prov.split(" ")
                    target_cargoshen = CargoArea.objects(Q(name__contains=targetAreas[0]) )
                    for target_cargoshenobj in target_cargoshen:
                            if target_cargoshenobj.level =='1':
                               targetSiteName_prov_code = target_cargoshenobj.code 
                    j = 1
                    t_list=[] 
                    for area in targetAreas:
                        k=j
                        if j==1:
                            cargoAreaObj = CargoArea.objects.get(level =str(k) ,name=area)
                        else:
                            cargoAreaObj = CargoArea.objects.get(level =str(k) ,name=area,parentcode=t_list[k-2])
                        j+=1
                        t_list.append(cargoAreaObj['code']) 
                    order.targetSiteName = " ".join(t_list)  
                else:
                    raise ParameterError('目的地不能为空')
                
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
                         new_batch_insurance_price =int(batch_insurance_price.rstrip("万"))*10000
                         order.insurance_price = int(new_batch_insurance_price*100)
                    else:
                         raise ParameterError('货物价值不能为空')
#2016.12.27 暂时取消众安车次
#                     if new_batch_insurance_price < 3000000:
#                             insuranceProducts = InsuranceProducts.objects(product_type=product_type,is_hidden=False)
#                             for insuranceProductsobjzhongan in insuranceProducts:
#                                  if  insuranceProductsobjzhongan.company.paper_id == settings.ZHONGAN_COMPANY_CODE:  
#                                           order.insurance_product = insuranceProductsobjzhongan
#                                           order.company = insuranceProductsobjzhongan.company
#                                           order.product_type = insuranceProductsobjzhongan.product_type
#                                           order.insurance_type = insuranceProductsobjzhongan.insurance_type
#                                           order.insurance_rate = insuranceProductsobjzhongan.rate
#                                             #包装类型
#                                           order.pack_method = '1001'
#                                             #投保货物类型
#                                           common_good='CB001-1'
#                                           if common_good:
#                                                 order_cargo =Cargo.objects(cargo_number=common_good).first()
#                                                 order.cargo = order_cargo
#                                           else:
#                                                 raise ParameterError('车次保险未选择具体货物')
#                                             #运单号
#                                           order.transport_id = "整车"
#                                             #默认货物名称
#                                           order.commodityName = '零担货物'
#                                             #货物总数量
#                                           batch_commodityCases = self.get_parameter('batch_commodityCases').strip()
#                                           if batch_commodityCases:
#                                                 try:
#                                                     batch_commodityCases1=float(batch_commodityCases)
#                                                     batch_commodityCases2=int(batch_commodityCases)
#                                                     if batch_commodityCases1 !=batch_commodityCases2:
#                                                         raise ParameterError('请输入整数') 
#                                                     else:
#                                                         order.commodityCases = str(batch_commodityCases2)
#                                                 except:
#                                                    raise ParameterError('请输入数字') 
#                                           else:
#                                                 raise ParameterError('货物总数量不能为空')
#                                           break
#                     else:        
#屏蔽货物件数    
#                     batch_commodityCases = self.get_parameter('batch_commodityCases').strip()
#                     if batch_commodityCases:
#                           try:
#                               batch_commodityCases1=float(batch_commodityCases)
#                               batch_commodityCases2=int(batch_commodityCases)
#                               if batch_commodityCases1 !=batch_commodityCases2:
#                                   raise ParameterError('请输入整数') 
#                               else:
#                                   order.commodityCases = str(batch_commodityCases2)
#                           except:
#                              raise ParameterError('请输入数字') 
#                     else:
#                           raise ParameterError('货物总数量不能为空')


#下面一行是原来代码
#                     insuranceProducts = InsuranceProducts.objects(product_type=product_type,is_hidden=False)
                    insuranceProducts=[]
                    insuranceProduct_list = InsuranceProducts.objects(product_type=product_type,is_hidden=False)
                    for insuranceProduct_set in insuranceProduct_list:
                        if client_detail  in insuranceProduct_set.user_type_list:
                            insuranceProducts.append(insuranceProduct_set)
                    
#测试结束
                    productbatchsite = []
                    resultbatch = []
                    if insuranceProducts:
                           for insuranceProductsobj in insuranceProducts:
                                         if startSiteName_prov_code in insuranceProductsobj.no_insurable_route or targetSiteName_prov_code  in insuranceProductsobj.no_insurable_route:
                                                             continue
                                         else:
                                                             productbatchsite.append(insuranceProductsobj)
                           if  productbatchsite:
                                      for productbatchsiteobj in productbatchsite:
                                               if new_batch_insurance_price>productbatchsiteobj.insurance_price_max/100 or new_batch_insurance_price <productbatchsiteobj.insurance_price_min/100:
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
                                 raise ParameterError('抱歉，根据您填写的条件，没有筛选出可以承保的产品！')
                                  
                                            
                    else:
                            raise ParameterError('无此产品类型的产品')
                     
                    #车牌号
                    batch_plate_number = self.get_parameter('batch_plate_number').strip()
                    short = self.get_parameter('short').strip()
#                     letter = self.get_parameter('letter').strip()
                    if order_type == "edit":
                            if batch_plate_number and short:
                                if len(batch_plate_number) <= 10:
                                    if re.match(r'^[a-z_A-Z_0-9]{5}$', batch_plate_number):
                                            batch_plate_number = batch_plate_number.upper()
                                            order.plate_number = short +  batch_plate_number
                                    else:
                                       raise ParameterError('您输入的车牌号不正确，请输入五位英文或数字')
                                else:
                                    raise ParameterError('您输入的车牌号不正确')
                    else:
                            if batch_plate_number and short:
                                if len(batch_plate_number) <= 10:
                                    if re.match(r'^[a-z_A-Z_0-9]{5}$', batch_plate_number):
                                            batch_plate_number = batch_plate_number.upper()
                                            order.plate_number = short + batch_plate_number
                                    else:
                                       raise ParameterError('您输入的车牌号不正确，请输入英文或数字')
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
#                     if order_type == "edit":
#                                 #order.batch_image_list = []
#                                 if batch_image_list:       
#                                         image_tool = ImageTools()
#                                         for batch_image in batch_image_list:
#                                             batch_image_url = image_tool.save(request_file=batch_image, file_folder=ImageFolderType.batch, old_file='')
#                                             if batch_image_url:
#                                                 order.batch_image_list.append(batch_image_url)
#                                             else:
#                                                 raise ParameterError('保存清单图片失败')
                                
                                
                                
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
                                    raise ParameterError("保险清单内容，二选一")
                    else:       
                                if not position_list and not batch_image_list and not batch_file:
                                    raise ParameterError("保险清单内容，二选一")
                elif product_type == 'ticket':
                    
                     #货物类型
                     wx_cargo_detail = self.get_parameter('wx_cargo_detail').strip()
                     if not  wx_cargo_detail:
                           raise ParameterError('货物类型不能为空')
                       
                      #包装方式
                     wx_pack_detail_id = self.get_parameter('wx_pack_detail_id').strip()
                     if wx_pack_detail_id:
                          wx_pack = wx_pack_detail_id.split(" ")
                          pack_method_list=order.PACK_METHOD
                          flag = False
                          for pack_method in pack_method_list:
                              for pack in pack_method[1]:
                                  if wx_pack[1]  == pack[1]:
                                      order.pack_method = pack[0]
                                      flag = True
                                      break  
                              if flag ==  True: 
                                  break         
                     else:
                           raise ParameterError('包装方式不能为空')   
                       
                       
                    #运输方式
                     transport_type = self.get_parameter('transport_type_id').strip()
                     if transport_type:
                            #运输方式翻译
                            try:
                                transport_type_list1=order.TRANSPORT_TYPE
                                number = ""
                                test =0
                                for transport_type_set in transport_type_list1:
                                    if transport_type_set[1]==transport_type:
                                        number=transport_type_set[0]
                                        test=1
                                        break
                                if test ==1:
                                    order.transport_type=str(number)
                                else:
                                    message='传值过程中运输方式翻译失败，请查看运输编号'+str(transport_type)
                                    raise ParameterError(message)
            #                         extraInfo_detail["transportType"]="汽运"#.encode("utf8")
                            except:
                                message='传值过程中运输方式翻译失败，请查看运输编号'+str(transport_type)
                                raise ParameterError(message)
                     else:
                        order.transport_type="1"
                       
                       
                     #货物价值
                     insurance_price = self.get_parameter('insurance_price').strip()
                     if insurance_price and insurance_price.isdigit():
                            try:
                                order.insurance_price = int(float(insurance_price)*100)
                            except:
                                raise ParameterError('货物价值请输入数字')            
                     else:
                         raise ParameterError('货物价值不能为空，且只能输入数字')
                                         
                   #运单号
                     ticket_transport_id = self.get_parameter('ticket_transport_id').strip()
                     if ticket_transport_id:
                        order.transport_id = ticket_transport_id
                     #货物名称
                     ticket_commodityName = self.get_parameter('ticket_commodityName').strip()
                     if ticket_commodityName:
                        order.commodityName = ticket_commodityName
                     else:
                        raise ParameterError('货物名称不能为空')
                     #货物数量
                     ticket_commodityCases = self.get_parameter('ticket_commodityCases').strip()
                     if ticket_commodityCases:
                        try:
                            ticket_commodityCases=int(ticket_commodityCases)
                        except:
                            try:
                                ticket_commodityCases=float(ticket_commodityCases)
                            except:
                                raise ParameterError('货物数量请输入数字')
                        if ticket_commodityCases>0:
                            order.commodityCases = str(ticket_commodityCases)
                        else:
                            raise ParameterError('货物数量请输入大于零的数字')
                     else:
                        raise ParameterError('货物数量不能为空')
                     #车牌号
                     batch_plate_number = self.get_parameter('batch_plate_number').strip()
                     short = self.get_parameter('short').strip()
#                      letter = self.get_parameter('letter').strip()

                     if batch_plate_number and short:
                                if len(batch_plate_number) <= 10:
                                    if re.match(r'^[a-z_A-Z_0-9]{5}$', batch_plate_number):
                                            batch_plate_number = batch_plate_number.upper()
                                            order.plate_number = short + batch_plate_number
                                    else:
                                       raise ParameterError('您输入的车牌号不正确，请输入英文或数字') 
                                else:
                                            raise ParameterError('您输入的车牌号不正确')


                     if not ticket_transport_id and  not batch_plate_number:
                        raise ParameterError('车牌号和运单号至少填写一个！')
                     #过滤
                     resultlist5 = []
                     productCargosite = []
                     productCargo= []
                     cargo =Cargo.objects(cargo_name=wx_cargo_detail).first()
                     if  cargo:          
                                     order.cargo = cargo                                              
                                     productCargoall= ProductCargo.objects(cargo=cargo)  
                                     if productCargoall:
                                         for productCargoallobj in productCargoall:
                                                      if startSiteName_prov_code in productCargoallobj.product.no_insurable_route or targetSiteName_prov_code  in productCargoallobj.product.no_insurable_route:
                                                             continue
                                                      else:
                                                             productCargosite.append(productCargoallobj)  
                                     else:
                                          raise ParameterError('此货物类型没有可保产品')
                                     if productCargosite:
                                                     for productCargositeobj in productCargosite:
                                                           if float(insurance_price)>productCargositeobj.product.insurance_price_max/100 or float (insurance_price)<productCargositeobj.product.insurance_price_min/100:
                                                                    continue
                                                           else:
                                                               if  productCargositeobj.product.is_hidden == False:
                                                                        productCargo.append(productCargositeobj)
                                     else:
                                          raise ParameterError('此路线没有可保产品')
                                                                                                                  
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
                                                                                                                     order.product_type = productCargo[0].product.product_type
                                                                                                         else:
                                                                                                                      order.insurance_company_rate = rate.insurance_rate
                                                                                                                      order.insurance_company_price =  int(rate.insurance_rate* 10000000 / 10000000 *float(insurance_price)*100)
                                                                                                                      order.old_price = int(rate.products_rate* 10000000 / 10000000 *float(insurance_price)*100)
                                                                                                                      order.insurance_product =  productCargo[0].product
                                                                                                                      order.insurance_rate = rate.products_rate
                                                                                                                      order.commission_ratio =rate.commission_ratio
                                                                                                                      order.good_type = rate.good_type
                                                                                                                      order.company =  productCargo[0].product.company
                                                                                                                      order.product_type = productCargo[0].product.product_type
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
                                                                                 order.product_type = productCargo[0].product.product_type
                                                                                 #2017/06/12修正微信端下单未保存险种类型的错误
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
#********************************2017/6/9添加测试字段***************************
                                                          insurance_product_list=[]
                                                          if resultlist5:
                                                              for insuranceProduct_set in resultlist5:
                                                                  if client_detail  in insuranceProduct_set.product.user_type_list:
                                                                      insurance_product_list.append(insuranceProduct_set)
                                                              if len(insurance_product_list)>0:
                                                                  resultlist5=insurance_product_list
                                                              else:
                                                                  raise ParameterError('无符合条件的产品。')
                                                            
                                                         
#**********************************测试结束*********************************************                                                                                                                           
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
                                                                             order.product_type = resultlist5[0].product.product_type
                                                                             #2017/06/12修正微信端下单未保存险种类型的错误
                                                                             order.insurance_type = resultlist5[0].product.insurance_type
                                                          else:
                                                             raise ParameterError('无符合条件的产品')
                                             else:
                                                 raise ParameterError('无此货物类型的产品')                                       
                                     else:
                                           raise ParameterError('抱歉，根据您填写的条件，没有筛选出可以承保的产品！')
                     else:
                         raise ParameterError('无此货物类型对应的产品')
    
                else:
                    raise ParameterError('非法的产品类型')
            else:
                raise ParameterError('用户不存在')

        return order
    
    
    #验证是否存在可包保险中介（弃用2017/2/22）
    def validation_jdclbx_intermediary(self, short_number,order_car_type):
        if order_car_type == 'truck':
             car_type = '货车'
        elif order_car_type == 'passenger_car':
            car_type = '九座以下客车'
        else:
           return '未获取到车辆类型' 
        
        intermediary_list = Intermediary.objects.filter(state = True, order_car_type__icontains=order_car_type, plate_number_list__icontains=short_number )
        test_count =intermediary_list.count()
         
        if test_count == 0:
            message = "暂未开通"+str(car_type) + '车牌号为' + str(short_number)+ '部分投保业务'
            return message
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
                message = "暂未开通"+str(car_type) + '车牌号为' + str(short_number)+ '部分投保业务。'
                return message
        
        
        return 'success'
    
    
    
    #   验证车险订单
    def validation_jdclbx_order(self, jdclbx_order):
        jdclbx_state = self.get_parameter('jdclbx_state').strip()       #订单状态
        if jdclbx_state == 'create':
            order_car_type = self.get_parameter('order_car_type', '').strip()#货物大类
            plate_number = self.get_parameter('plate_number', '').strip()#车牌号
            city_code = self.get_parameter('city_code', '').strip()#城市
        elif jdclbx_state == 'edit':
            #获取编辑车牌号信息
            car_type = self.get_parameter('car_type', '').strip()#车辆类型
            home_city = self.get_parameter('wx_home_city', '').strip()#
            short = self.get_parameter('short', '').strip()#
            wx_plate_number = self.get_parameter('wx_plate_number', '').strip()#
            #车辆类型审核
            car_type_list = InquiryInfo.ORDER_CAR_TYPE   #车辆类型
            order_car_type = ''
            if car_type:  
                for car_type_obj in car_type_list:
                    if car_type_obj[1]==car_type:
                        order_car_type = car_type_obj[0]
                        break  
            #车牌号
            wx_jianche = []
            wx_jianche =  short.split(' ')
            short_number = wx_jianche[0]
            if  wx_plate_number:
                if re.match(r'^[a-z_A-Z_0-9]{5}$', wx_plate_number):
                    wx_plate_number = wx_plate_number.upper()
                    plate_number = str(short)+' '+str(wx_plate_number)
                else:
                     raise ParameterError('您输入的车牌号不正确，请输入五位由英文或数字组合的字符串')
            else:
                raise ParameterError('请填写车牌号')
#             test_intermediary = self.validation_jdclbx_intermediary( short_number,order_car_type)
#             if test_intermediary != 'success':
#                 raise ParameterError(str(test_intermediary))
            #城市
            if home_city:  
                home_citylist = []
                home_citylist = home_city.split(' ')
                try:
                    cargoshi = CargoArea.objects(name__contains=home_citylist[1],level ="2").first()
                    city_code = cargoshi.code

                except:
                    raise ParameterError('未获取到修改后的车辆所在城市信息。')
            else:
                   raise ParameterError('未获取到修改后的车辆所在城市信息') 
            
        else:
            raise ParameterError('未获取到订单状态信息')
        if not order_car_type or not plate_number or not city_code:
             raise ParameterError( '网络延迟，未获取到车牌号、车辆所在城市或投保车辆类型') 
         ##投保车辆大类选择
        if order_car_type:
            jdclbx_order.order_car_type = order_car_type
        else:
            raise ParameterError('未获取到投保车辆大类信息')
         ##车牌号
        if plate_number:
            jdclbx_order.plate_number = plate_number
        else:
            raise ParameterError('未获取到车牌号信息')
        #车辆城市编码
        if city_code:
            try:
                city_set = CargoArea.objects(code=city_code).first()
            except:
                raise ParameterError('网络不稳定，未找到对应城市信息')
            jdclbx_order.city = city_set
        else:
            raise ParameterError('未获取到车辆城市')
        
        
        #验证是否有可保中介
        #2017添加不审核信息不是必填项
        if order_car_type == 'passenger_car':
                order_car_type_name ='九座以下客车'
        elif order_car_type == 'truck':  
            order_car_type_name ='货车'
        else:
            order_car_type_name = order_car_type
        short_number1=plate_number.split(' ')[0]
        intermediary_list = Intermediary.objects.filter(state = True, order_car_type__icontains=order_car_type, plate_number_list__icontains=short_number1 )
        test_count =intermediary_list.count()
        if test_count == 0:
            message = "暂未开通"+str(order_car_type_name) + '车牌号为' + str(short_number1)+ '部分投保业务'
            raise ParameterError(message)
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
            if len(intermediary_list_test)>0:
                jdclbx_order.intermediary_list = intermediary_list_test
            else:
                message = "暂未开通"+str(order_car_type_name) + '车牌号为' + str(short_number1)+ '部分投保业务。'
                raise ParameterError(message)
        
        #基本信息-车辆信息
        #车辆信息部分
        id_plate_image_left =self.request.FILES.get('driving_license', '')    #行驶证正页
        id_plate_image_right = self.request.FILES.get('driving_license_down', '')     #行驶证附页
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
        
        if jdclbx_state == 'edit':
             jdclbx_order.car_number=''
             jdclbx_order.brand_digging=''
             jdclbx_order.engine_number=''
             jdclbx_order.people_number=''
             jdclbx_order.load_weight=''
            
        #基本信息-投保人
        ismatchxsz = self.get_parameter('ismatchxsz', '').strip()#是否同行驶证
        #投保人身份
        user_classify = self.get_parameter('user_classify', '').strip()#投保人身份
        applicant_phone = self.get_parameter('applicant_phone', '').strip()#手机号码
        #投保人身份-单位
        applicant_company_name = self.get_parameter('applicant_company_name', '').strip()#单位名词
        business_license_image = self.request.FILES.get('national_image_yingye', '')#营业执照
        #个人
        wx_applicant_name = self.get_parameter('wx_applicant_name', '').strip()#投保人姓名
        id_card_up = self.request.FILES.get('carded_image', '')#身份证正面
        id_card_down = self.request.FILES.get('carded_image_down', '')#身份证背面
        #个人
        if user_classify == "个人":
            jdclbx_order.user_classify ="personal"
            if ismatchxsz != 'on':
                if not wx_applicant_name:
                    raise ParameterError('请输入投保人姓名')
                else:
                    jdclbx_order.applicant_name = wx_applicant_name
            else:
                jdclbx_order.applicant_name = '同行驶证'
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
                    if id_card_down_url:
                        jdclbx_order.id_card_down=id_card_down_url
                    else:
                        raise ParameterError('身份证背面图片上传失败')
                except:
                    raise ParameterError('保存身份证背面失败')
            else:
                if jdclbx_state == 'create':
                    raise ParameterError('请上传身份证背面图片')
            if jdclbx_state == 'edit':
                #清空单位信息
                jdclbx_order.applicant_company_name=''
                jdclbx_order.business_license_image=''
                jdclbx_order.organ=''
                jdclbx_order.certificate_number = ''
            
        if user_classify == "单位":
            jdclbx_order.user_classify ="unit"
            if ismatchxsz != 'on':
                if not applicant_company_name:
                    raise ParameterError('请输入投保人姓名')
                else:
                    jdclbx_order.applicant_company_name = applicant_company_name
            else:
                jdclbx_order.applicant_company_name = '同行驶证'
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
            if jdclbx_state == 'edit':
                #清空个人信息
                jdclbx_order.id_card_up=''
                jdclbx_order.id_card_down=''
                jdclbx_order.applicant_name = ''
                jdclbx_order.certificate_number = ''
                jdclbx_order.organ=''
            #投保人手机号
        if applicant_phone:
            if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', applicant_phone):
                raise ParameterError( '请输入正确的投保人手机号码')
            jdclbx_order.applicant_phone = applicant_phone
        else:
             raise ParameterError('请输入投保人手机号')
        #基本信息-被保人
        ismatchtbr = self.get_parameter('ismatchtbr', '').strip()#是否同行驶证
        if ismatchtbr == 'on':
            if jdclbx_order.user_classify == 'unit':
                jdclbx_order.insured_name =  '同投保人姓名'
                jdclbx_order.insured_phone = jdclbx_order.applicant_phone
                jdclbx_order.insured_license_image = jdclbx_order.business_license_image#营业执照
                jdclbx_order.insured_number = ''#组织机构证件号码
                jdclbx_order.insured_classify = jdclbx_order.user_classify#被保险人身份状态
                jdclbx_order.insured_card_up = ''
                jdclbx_order.insured_card_down = ''
            elif jdclbx_order.user_classify == 'personal':
                jdclbx_order.insured_name =  '同投保人姓名'
                jdclbx_order.insured_phone = jdclbx_order.applicant_phone
                jdclbx_order.insured_classify = jdclbx_order.user_classify#被保险人身份状态
                jdclbx_order.insured_number = ''#被保险人身份证号码
                jdclbx_order.insured_card_up = jdclbx_order.id_card_up#身份证正页
                jdclbx_order.insured_card_down = jdclbx_order.id_card_down#身份证背面
                jdclbx_order.insured_license_image = ''
            else:
                raise ParameterError('投保人状态出错，请选择手工录入方式')
        else:
            insured_name = self.get_parameter('insured_name', '').strip()#被保人姓名
            insured_phone = self.get_parameter('insured_phone', '').strip()#被保人手机号
            insured_classify = self.get_parameter('bbx_user_classify', '').strip()#被保人用户类别
            #单位
            insured_business_license_image = self.request.FILES.get('bbx_national_image_yingye', '')#被保人营业执照
            #个人
            insured_card_up = self.request.FILES.get('bbx_carded_image', '')#被保人身份证正页
            insured_card_down = self.request.FILES.get('bbx_carded_image_down', '')#被保人身份证背面
            
            
            #投保人姓名
            if insured_name:
                jdclbx_order.insured_name = insured_name
            else:
                raise ParameterError('请输入被投保人姓名')
            #被保人手机号
            if insured_phone:
                 if not re.match(r'^(13[0-9]|15[012356789]|17[3678]|18[0-9]|14[57])[0-9]{8}$', insured_phone):
                     raise ParameterError( '请输入正确的被投保人手机号码')
                 jdclbx_order.insured_phone = insured_phone
            else:
                 raise ParameterError('请输入被投保人手机号')
            #单位
            if insured_classify =='单位':
                jdclbx_order.insured_classify = 'unit'
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
                if jdclbx_state == 'edit':
                    #清空个人信息
                    jdclbx_order.insured_card_up=''
                    jdclbx_order.insured_card_down=''
                    jdclbx_order.insured_number=''
            #个人
            elif insured_classify == '个人':
                jdclbx_order.insured_classify = 'personal'
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
                if jdclbx_state == 'edit':
                    #清空单位信息
                    jdclbx_order.insured_license_image=''
                    jdclbx_order.insured_number=''
            else:
                raise ParameterError('请选择被保人身份，单位或个人')
        #保单地址
        policy_address = self.get_parameter('policy_address', '').strip()#被保人保单快递地址
        detailed_address = self.get_parameter('detailed_address', '').strip()#被保人详细地址
        if city_code != '1101':
            #邮寄地址前缀
            if policy_address:
                  jdclbx_order.mail_address = policy_address
            else:
                raise ParameterError('保单快递地址不能为空')
            #详细地址
            if detailed_address:
                  jdclbx_order.policy_address = detailed_address
            else:
                raise ParameterError('保单详细地址不能为空！')
        else:
            jdclbx_order.mail_address = ''
            jdclbx_order.policy_address = ''
         #选择险种
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
        special_agreement = self.get_parameter('special_agreement').strip()       #划痕险   
        #交强险
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
            jdclbx_order.third_insurance  = int(third_insurance.rstrip("万"))*10000*100
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
        else:
            raise ParameterError('请选择玻璃险保险状态，不投保，国产或进口')
        #司机险
        if driver_insurance == "不投保":
            jdclbx_order.driver_insurance= 0
        else:
            jdclbx_order.driver_insurance=  int(driver_insurance.rstrip("万"))*1000000
        #乘客险
        if passenger_insurance == "不投保":
            jdclbx_order.passenger_insurance= 0
        else:
            jdclbx_order.passenger_insurance=  int(passenger_insurance.rstrip("万"))*1000000
        #盗抢险
        if theft_insurance=="on":
            jdclbx_order.theft_insurance = True
        else:
            jdclbx_order.theft_insurance = False
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
        elif '千'in scratch_insurance:
            jdclbx_order.scratch_insurance = int(scratch_insurance.rstrip("千"))*1000*100
        elif '万'in scratch_insurance:
            jdclbx_order.scratch_insurance = int(scratch_insurance.rstrip("万"))*10000*100
        else:
            raise ParameterError('请选择划痕险保险状态')
        test_state=0
        test_commercial = 0
        if  not vehicle_vessel_tax_state and third_insurance == "不投保" and not damage_insurance and glass_insurance== "不投保" :
            if  driver_insurance == "不投保" and not theft_insurance and passenger_insurance == "不投保"  :
                if  not iop_insurance and not autoignition_insurance and not wading_insurance and  scratch_insurance  == "不投保":
                    test_commercial = 1
                    if not liability_state :
                        test_state = 1
        if test_state == 1:
            raise ParameterError('商业险和交强险至少选择一种')
        #特别约定
        if special_agreement:
            if len(special_agreement)>150:
                raise ParameterError('请简短描述特别约定内容，包括标点一共不可超过150字')
            jdclbx_order.special_agreement = special_agreement
        else:
            jdclbx_order.special_agreement = ''
        
        #商业险和交强险保险起期
        liability_expectStartTime = self.get_parameter('liability_expectStartTime').strip() 
        commercial_expectStartTime = self.get_parameter('commercial_expectStartTime').strip() 
        if liability_state=="on":
            if liability_expectStartTime:
                now = datetime.now()
                d1 = datetime.now()
                d3 = d1 + timedelta(days =90)
                otherStyleTime = now.strftime("%Y-%m-%d ")
                Closing_date = d3.strftime("%Y-%m-%d ")
                #2017/10/23放开提前时间限制
#                 if otherStyleTime > liability_expectStartTime:
#                     raise ParameterError('交强险保险起期不能早于当前时间')
                if liability_expectStartTime > Closing_date:
                    raise ParameterError('交强险保险起期只能在当前日期顺延90天的时间内')
                jdclbx_order.liability_expectStartTime = liability_expectStartTime
            else:
                raise ParameterError('请选择交强险保险起期')
        #商业险保险起期
        if test_commercial == 0:
            if commercial_expectStartTime:
                now = datetime.now()
                otherStyleTime = now.strftime("%Y-%m-%d ")
                d1 = datetime.now()
                d3 = d1 + timedelta(days =90)
                Closing_date = d3.strftime("%Y-%m-%d ")
                #2017/10/23放开提前时间限制
#                 if otherStyleTime > commercial_expectStartTime:
#                     raise ParameterError('商业险保险起期不能早于当前时间')
                if commercial_expectStartTime > Closing_date:
                    raise ParameterError('商业险保险起期只能在当前日期顺延90天的时间内')
                jdclbx_order.commercial_expectStartTime = commercial_expectStartTime
            else:
                raise ParameterError('请选择商业险保险起期')
        return jdclbx_order

    
    #验证众安保险添加的内容
    def wss_validation_za_order(self, order):
        product_type = str(order.product_type)
        #单票保险验证资料
        tb_client_type = self.get_parameter("tb_client_type", "")#单票保险用户身份
        holderCertNo = self.get_parameter("holderCertNo", "")#单票保险投保人证件号
        taxpayerRegNum = self.get_parameter("taxpayerRegNum", "")#单票保险纳税人识别号 
        #车次保险验证资料
        tb_holderCertType = self.get_parameter("tb_holderCertType", "")#投保人证件类型
        bb_insureCertType = self.get_parameter("bb_insureCertType", "")#被保人证件类型
        bb_insureCertNo = self.get_parameter("bb_insureCertNo", "")#被保人证件号
        trailerNo = self.get_parameter("trailerNo", "")#挂车牌号
        if product_type == "ticket":
            if not tb_client_type:
                raise ParameterError('请选择投保人身份')
            if tb_client_type == "公司":
                order.tb_client_type = "company"
                if not taxpayerRegNum:
                    raise ParameterError('请填写纳税人识别号 ')
                else:
                    if len(holderCertNo) > 20 :
                        raise ParameterError('填写的纳税人识别号号码过长 ')
                    order.taxpayerRegNum =str(taxpayerRegNum)
            elif tb_client_type == "个人":
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
            if tb_client_type == "公司":
                order.tb_client_type = "company"
            elif tb_client_type == "个人":
                order.tb_client_type = "person"
            else:
                raise ParameterError('请选择投保人身份状态不正确,请退出当前页面重新进入')
            #投保人纳税人识别号
            if len(holderCertNo) > 20 :
                raise ParameterError('填写的纳税人识别号号码过长 ')
            order.taxpayerRegNum =str(taxpayerRegNum)
            
            #投保人证件类型
            if tb_holderCertType == "统一社会信用代码":
                order.tb_holderCertType = "TY"
            elif tb_holderCertType == "组织机构代码":
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
            if bb_insureCertType == "统一社会信用代码":
                order.bb_insureCertType = "TY"
            elif bb_insureCertType == "组织机构代码":
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
    
    
    #验证发布二手商品
    def wss_validation_goods(self, mall_goods):
        #用户
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        client = Client.objects(user=self.request.user).first()
        state= self.get_parameter("mall_goods_state").strip()#编辑状态
        goods_name= self.get_parameter("goods_name").strip()#商品名称
        goods_brand_digging= self.get_parameter("goods_brand_digging").strip()#品牌型号
        goods_count= self.get_parameter("goods_count").strip()#商品数量
        original_cost= self.get_parameter("original_cost").strip()#商品原价
        unit_price= self.get_parameter("unit_price").strip()#商品单价
        present_situation= self.get_parameter("present_situation").strip()#商品状态
        other_notes= self.get_parameter("other_notes").strip()#商品状态补充信息
        goods_type= self.get_parameter("goods_type").strip()#商品分类
        
        #地址
        startSiteName_prov = self.get_parameter('startSiteName_prov').strip()#省
        policy_address = self.get_parameter('policy_address').strip()
        #地址结束
        contact_phone= self.get_parameter("contact_phone").strip()#联系方式-电话
        contact_landline= self.get_parameter("contact_landline").strip()#联系方式-座机
        contact_qq= self.get_parameter("contact_qq").strip()#联系方式-QQ
        contact_wx= self.get_parameter("contact_wx").strip()#联系方式-WX
        goods_describe= self.get_parameter("goods_describe").strip()#商品描述
        picture_list = self.request.FILES.getlist('picture', '')#商品照片
        certificate_type= self.get_parameter("certificate_type").strip()#商品证明方式
        certificate_url= self.get_parameter("certificate_url").strip()#商品证明地址
        certificate_image_list = self.request.FILES.getlist('certificate_image', '')#商品价值证明照片
        #发布状态
        #if state == 'create':
        mall_goods.state = 'publish'
        #编辑状态
        if state not in ['create','edit']:
            raise ParameterError('网络问题，未获取商品创建状态')
        #用户
        if client:
                mall_goods.client = client
        else:
            raise ParameterError('网络延迟，未找到所属用户')
        #联系人
        contact_people=''
        if client.company_name:
            contact_people=str(client.company_name)
        elif client.name:
            contact_people=str(contact_people)
        if contact_people:
            mall_goods.contact_people =str(contact_people)
        #商品名称
        if goods_name:
            if len(goods_name)>100:
                raise ParameterError('请名称最多输入100个字符')
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
                goods_type_set = GoodsType.objects(name=goods_type).first()
                if not goods_type_set:
                    raise ParameterError('请选择商品分类。')
            except:
                raise ParameterError('网络延迟，未找到对应商品分类，请退出重试')
            mall_goods.goods_type =goods_type_set
        else:
            raise ParameterError('请选择商品分类')
        #原价
        if original_cost:
            if len(original_cost)>100:
                raise ParameterError('原价最多输入100个字符')
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
            test_state='0'
            for present_situation_set in mall_goods.PRESENT_SITUATION:
                test_detail =present_situation_set[1]
                if  present_situation_set[1] == present_situation:
                    test_state='1'
                    if present_situation_set[0]=='':
                        raise ParameterError('请输入商品状态。')
                    mall_goods.goods_present_situation =str(present_situation_set[0])
                    break
            if test_state=='0':
                raise ParameterError('未找到输入的商品状态，请退出后重试')
        else:
            raise ParameterError('请输入商品状态')
        
        #商品状态补充信息
        if present_situation == '其他':
            if other_notes:
                mall_goods.other_notes =str(other_notes)
            else:
                raise ParameterError('请输入商品状态补充信息')
        #单价
        if unit_price:
            if len(unit_price)>100:
                raise ParameterError('单价最多输入100个字符')
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
            if len(goods_count)>100:
                raise ParameterError('数量最多输入100个字符')
            mall_goods.goods_count =str(goods_count)
        else:
            raise ParameterError('请输入商品数量')
        
        
       
        
        
        #地址部分
        if startSiteName_prov:
            #地址分解
            try:
                mail_address = startSiteName_prov
                mail_address_list =mail_address.split(' ')
                mail_prov=mail_address_list[0]
                mail_prov_set = CargoArea.objects(level='1',name=mail_prov).first()
                mail_prov_number = mail_prov_set.code
                
                mail_city =mail_address_list[1]
                mail_city_set = CargoArea.objects(level='2',name=mail_city).first()
                mail_city_number = mail_city_set.code
                
                if mail_address_list[2]:
                    mail_dis=mail_address_list[2]
                    mail_dis_set = CargoArea.objects(level='3',name=mail_dis).first()
                    mail_dis_number = mail_dis_set.code
                
                if mail_prov_number and mail_city_number:
                    mail_address_number = mail_prov_number +' ' + mail_city_number
                if mail_dis_number:
                    mail_address_number = mail_address_number +' ' + mail_dis_number
                mall_goods.mail_address =str(mail_address_number)
            except  Exception as e:
                message = str(e)
                raise ParameterError('网络延迟，商品地址分解失败')
        else:
            raise ParameterError('请选择商品地址')
        
        if policy_address:
            mall_goods.policy_address =str(policy_address)
        else:
            raise ParameterError('请选择商品详细地址')
        
        #联系方式-电话
        if not contact_phone and not contact_landline and not contact_qq and not contact_wx :
            raise ParameterError('手机，座机，QQ，微信 四种联系方式至少添加一种')
        if contact_phone:
            if len(contact_phone)>80:
                raise ParameterError('输入的手机号码过长')
            mall_goods.contact_phone =str(contact_phone)
        else:
            mall_goods.contact_phone =''
        #联系方式-座机
        if contact_landline:
            if len(contact_landline)>80:
                raise ParameterError('输入的座机号码过长')
            mall_goods.contact_landline =str(contact_landline)
        else:
            mall_goods.contact_landline =''
        #联系方式-QQ
        if contact_qq:
            if len(contact_qq)>80:
                raise ParameterError('输入的QQ号码过长')
            mall_goods.contact_qq =str(contact_qq)
        else:
            mall_goods.contact_qq =''
        #联系方式-WX
        if contact_wx:
            if len(contact_wx)>80:
                raise ParameterError('输入的微信号码过长')
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
        
        return mall_goods
        
        
        
        
        
        
        
        
        
    