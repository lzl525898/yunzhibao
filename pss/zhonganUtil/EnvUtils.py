# coding=utf-8
"""
众安保险公司sdk

 作者: yzb
 创建时间: 2016-07-26 
 版本: 1.0

"""
from pss.zhonganUtil.LogUtils import LogUtils
class EnvUtils:
    
    #网关地址
    _url = ''
    #众安公钥
    _publicKey = ''
    
    # 构造函数
    def  __init__(self,envCode = "iTest") :
        #LogUtils::log ( "没有指定envCode变量，将按iTest执行" );
        if (envCode == 'uat') :
             super(EnvUtils, self).__init__()
             self._url = "http://opengw.uat.zhongan.com/Gateway.do"
             self._publicKey = b'''-----BEGIN PUBLIC KEY----- 
                                            MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDsNVusWhi5ZezrQFBGxZQkg303
                                            fp6sVVl8pZZolfmI4gc5KL/OjthrziPZTrvF5RMuOXFpPXvwmQnR9FfdiDIt7ci5
                                            fMnG+IwtH7WtE1jYoXugsobFVI9ZD82MvgB/i6M+ZnIBerM//5nfTDiA9f0Hf2Bd
                                            fYHMOp/6OFePNkb3uQIDAQAB
                                            -----END PUBLIC KEY-----'''

        elif (envCode == 'prd') :
            super(EnvUtils, self).__init__()
            self._url  = "http://opengw.zhongan.com/Gateway.do"
            self._publicKey  = b'''-----BEGIN PUBLIC KEY----- 
                                                 MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDFNndmLlsi8NYQpvZNK/b6kSjN
                                                 99lwWnWbAHxfBcBYQHx5mZBR8XkkIajSiYo29f7zmM0eAI8OSo6FY16bSt23RzTh
                                                 d+MvDBQC6axDCgGag5992AVGItU8LtWPBrM6XRbtN3+rjIteKhNDOUbEvp60S9/8
                                                 uoEfnqekd/nEG9I4mQIDAQAB 
                                                 -----END PUBLIC KEY-----'''
        else :
            super(EnvUtils, self).__init__()
            self._url  = "http://120.27.165.135:8080/Gateway.do"
            self._publicKey = b'''-----BEGIN PUBLIC KEY----- 
                                               MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIgHnOn7LLILlKETd6BFRJ0Gqg
                                               S2Y3mn1wMQmyh9zEyWlz5p1zrahRahbXAfCfSqshSNfqOmAQzSHRVjCqjsAw1jyq
                                               rXaPdKBmr90DIpIxmIyKXv4GGAkPyJ/6FTFY99uhpiq0qadD/uSzQsefWo0aTvP/
                                               65zi3eof7TcZ32oWpwIDAQAB
                                            -----END PUBLIC KEY-----'''

    


