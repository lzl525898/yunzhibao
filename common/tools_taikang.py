# -*- coding: utf8 -*-
# 文件名称：sendSMS.py
# 
# 文件作用：美联软通 http接口使用实例
# 
# 创建时间：2015-07-06
# 
# 
#Return Code										Description
#success:msgid								提交成功，发送状态请见4.1
#error:msgid								提交失败
#error:Missing username						用户名为空
#error:Missing password						密码为空
#error:Missing apikey						APIKEY为空
#error:Missing recipient					手机号码为空
#error:Missing message content				短信内容为空
#error:Account is blocked					帐号被禁用
#error:Unrecognized encoding				编码未能识别
#error:APIKEY or password error				APIKEY 或密码错误
#error:Unauthorized IP address				未授权 IP 地址
#error:Account balance is insufficient		余额不足
#error:Black keywords is:党中央				屏蔽词
import urllib
import urllib.request
from common import models
import hashlib
# from hashlib import md5
import base64


class TkHelper:
    def __init__(self, order):
        self.order = order

    def submit_order(self, phone_to, content):
        response = None
        result_str = None
        try:
            #内容,注意:发送验证或通知类信息,必须带自定义签名.如:您的验证码是:123456【您的签名】
            #content = '您的验证码是:123456【您的签名】'.decode('gbk','ignore').encode('gbk','ignore')
            content = '【GREAT】{0}'.format(content).encode('gbk', 'ignore')
            # print(content)
            url = ""
            parameters = dict()
            parameters['riskCode'] = '0613'
            parameters['startDate'] = self.order.start_date
            parameters['amount'] = self.order.insurance_price
            parameters['premium'] = self.order.price
            parameters['startSiteName'] = self.order.startSiteName
            parameters['targetSiteName'] = self.order.targetSiteName
            parameters['conveyanceLicenseNo'] = self.order.plate_numbers
            #提单号
            parameters['blNo'] = self.order.blNo
            parameters['flag'] = '1'
            parameters['itemcode'] = '03'
            parameters['itemdetailcode'] = self.order.itemdetailcode
            parameters['kindCode'] = self.order.kindCode
            parameters['coopSerialno'] = self.order.id
            parameters['insuredFlag'] = '1'
            #个人/团体物流公司选
            parameters['insuredType'] = '1'
            #投保人代码
            parameters['insuredCode'] = ''
            parameters['contactName'] = self.order.client.name
            parameters['mobile'] = self.order.client.profile.phone
            parameters['mail'] = self.order.client.profile.email
            #待收货款  实际运费
            parameters['deliveryPayment'] = self.order.id
            parameters['actualCost'] = self.order.id
            data = urllib.parse.urlencode(parameters)
            req = urllib.request.Request(url, data.encode('gbk', 'ignore'))
            response = urllib.request.urlopen(req)
            result = response.read()
            result_str = result.decode("unicode-escape")
            print(result_str)
        except Exception as e:
            print(e)
        finally:
            if response:
                response.close()
        if 'success' in result_str:
            return True
        else:
            return False

    def computeMD5hash(string):
        m = hashlib.md5()
        m.update(string.encode('utf-8'))
        return m.hexdigest()

    def stringToBase64(s):
        return base64.b64encode(s.encode('utf-8'))

    def base64ToString(b):
        return base64.b64decode(b).decode('utf-8')

#         import json
# >>> d = {"alg": "ES256"}
# >>> s = json.dumps(d)  # Turns your json dict into a str
# >>> print(s)
# {"alg": "ES256"}
# >>> type(s)



    # @staticmethod
    # def default_helper():
    #     username = 'szqhht'
    #     password = 'thhqzs123'
    #     apikey = '6adcde3ab4c86e78f36de228cad1bdd9'
    #     default_sms_helper = SmsHelper(username, password, apikey)
    #     return default_sms_helper


# if __name__ == "__main__":
#     sms_helper = SmsHelper.default_helper()
#     #手机号,多个号码间使用半角逗号分隔
#     mobile = '13936591067'
#     if sms_helper.send_sms(phone_to=mobile, content='您的验证码是{0}'.format('165455')):
#         print('发送验证码短信成功')
#     else:
#         print('发送验证码短信失败')