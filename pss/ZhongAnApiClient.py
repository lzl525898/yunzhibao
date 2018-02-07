# -*- coding: utf-8 -*-
"""
众安保险公司sdk

 作者: yzb
 创建时间: 2016-07-26 
 版本: 1.0

"""
__author__ = 'mlzx'
from pss.zhonganUtil.DateUtils import DateUtils
from pss.zhonganUtil.EnvUtils import EnvUtils
from pss.zhonganUtil.SignatureUtils import SignatureUtils
from pss.zhonganUtil.HttpUtils import HttpUtils
import json
class ZhongAnApiClient(object):
     _env = ''
     _appKey = ''
     _privateKey=''
     _url = ''
     _zaPublicKey = ''
     _charset=''
     _signType= '' 
     _version = ''
     _format = ''
     _timestamp = ''
     _serviceName = ''
     
     #构造函数
     def __init__(self,env, appKey, privateKey, serviceName, version, charset = "UTF-8", signType = "RSA", format = "json"):
        super(ZhongAnApiClient, self).__init__()
        self._env = env
        self._appKey = appKey
        self._privateKey = privateKey
        self._serviceName = serviceName
        self._charset = charset
        self._signType = signType
        self._version = version
        self._format = format
     
    #调用服务
    # @param bizParams 业务参数            
     def call(self, bizParams):
        self.initParam()
        signatureUtils =  SignatureUtils ()
        if (self._env == 'prd') :
            zaPublicKey ="MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDFNndmLlsi8NYQpvZNK/b6kSjN99lwWnWbAHxfBcBYQHx5mZBR8XkkIajSiYo29f7zmM0eAI8OSo6FY16bSt23RzThd+MvDBQC6axDCgGag5992AVGItU8LtWPBrM6XRbtN3+rjIteKhNDOUbEvp60S9/8uoEfnqekd/nEG9I4mQIDAQAB"
        else :
            zaPublicKey = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIgHnOn7LLILlKETd6BFRJ0GqgS2Y3mn1wMQmyh9zEyWlz5p1zrahRahbXAfCfSqshSNfqOmAQzSHRVjCqjsAw1jyqrXaPdKBmr90DIpIxmIyKXv4GGAkPyJ/6FTFY99uhpiq0qadD/uSzQsefWo0aTvP/65zi3eof7TcZ32oWpwIDAQAB"
        #加密
        if bizParams:
            bizContent = signatureUtils.encrypt(bizParams,zaPublicKey)
            print(bizContent)
        else:
             bizContent = ''
        allParams= {}
        allParams['serviceName'] = self._serviceName
        allParams['appKey'] = self._appKey
        allParams['format'] = self._format
        allParams['signType'] = self._signType
        allParams['charset'] = self._charset
        allParams['version'] = self._version
        allParams['timestamp'] = self._timestamp
        allParams['bizContent'] = bizContent
        #加签
        signRequest = signatureUtils.sign(allParams,self._privateKey)
        allParams ['sign'] = signRequest
        #获取数据
        httpUtils =  HttpUtils ()
        result = httpUtils.doPost(self._url, allParams)
        result_dict =  eval(result)
        signResponse =   result_dict.pop('sign')
        #验签
        signCheckRst = signatureUtils.checkSign(result_dict, signResponse, self._zaPublicKey )
        if (signCheckRst != 1) :
            raise Exception ( "本地验签失败" )
        #解密
        if  result_dict ["bizContent"]:
            decryptedData = signatureUtils.decrypt ( result_dict ["bizContent"], self._privateKey )
            result_dict ["bizContent"] = decryptedData 
            print( result_dict ["bizContent"])
        else:
            result_dict ["bizContent"] =  False
        return result_dict
        
     def initParam(self):
        self._timestamp = DateUtils.withMicrosecond ()
        envUtils =  EnvUtils (self._env)
        self._url = envUtils._url
        self._zaPublicKey = envUtils._publicKey
