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


class SmsHelper:
    def __init__(self, username, password, api_key):
        #用户名
        self.username = username
        #密码
        self.password = password
        #APIKEY,请向销售或技术人员索取
        self.api_key = api_key

    def send_sms(self, phone_to, content):
        response = None
        result_str = None
        try:
            #内容,注意:发送验证或通知类信息,必须带自定义签名.如:您的验证码是:123456【您的签名】
            #content = '您的验证码是:123456【您的签名】'.decode('gbk','ignore').encode('gbk','ignore')
            content = '【运之宝】{0}'.format(content).encode('gbk', 'ignore')
            # print(content)
            url = "http://m.5c.com.cn:80/api/send/index.php"
            parameters = dict()
            parameters['username'] = self.username
            parameters['password'] = self.password
            parameters['apikey'] = self.api_key
            parameters['mobile'] = phone_to
            parameters['content'] = content
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

    @staticmethod
    def default_helper():
        username = 'yunzhibao'
        password = 'asdf1234q'
        apikey = '76d5e02113e198d2c4ce29594bfd760f'
        default_sms_helper = SmsHelper(username, password, apikey)
        return default_sms_helper


if __name__ == "__main__":
    sms_helper = SmsHelper.default_helper()
    #手机号,多个号码间使用半角逗号分隔
    mobile = '13936591067'
    if sms_helper.send_sms(phone_to=mobile, content='您的验证码是{0}'.format('165455')):
        print('发送验证码短信成功')
    else:
        print('发送验证码短信失败')