# coding=utf-8
"""
众安保险公司sdk

 作者: yzb
 创建时间: 2016-07-26 
 版本: 1.0

"""
import json
import base64  
import rsa 
import rsa.bigfile
import collections
import string 
import os
import urllib.request
from InsuranceSite.settings import BASE_DIR

import jpype
import os.path

class SignatureUtils:
#         
#         
    def  __init__(self) :
            super(SignatureUtils, self).__init__()

    """
    对参数进行加密
     @param $params 待加密参数            
     @param $publicKey 对应环境的众安公钥  
    """
    def encrypt(self,params,publicKey) :
         #publicKey = rsa.PublicKey.load_pkcs1_openssl_pem(publicKey)
         #key = publicKey
         #key ="MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIgHnOn7LLILlKETd6BFRJ0GqgS2Y3mn1wMQmyh9zEyWlz5p1zrahRahbXAfCfSqshSNfqOmAQzSHRVjCqjsAw1jyqrXaPdKBmr90DIpIxmIyKXv4GGAkPyJ/6FTFY99uhpiq0qadD/uSzQsefWo0aTvP/65zi3eof7TcZ32oWpwIDAQAB"
         #publicKey ="MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDFNndmLlsi8NYQpvZNK/b6kSjN99lwWnWbAHxfBcBYQHx5mZBR8XkkIajSiYo29f7zmM0eAI8OSo6FY16bSt23RzThd+MvDBQC6axDCgGag5992AVGItU8LtWPBrM6XRbtN3+rjIteKhNDOUbEvp60S9/8uoEfnqekd/nEG9I4mQIDAQAB"
         jvmPath = jpype.getDefaultJVMPath() 
         jarpath = os.path.join(os.path.abspath('.'), BASE_DIR+'/pss/zhonganjar/')
         if  not jpype.isJVMStarted():  
                            jpype.startJVM(jvmPath,"-ea", "-Djava.class.path=%s" % (jarpath + 'commons-lang-2.6.jar'),"-Djava.class.path=%s" % (jarpath + 'commons-lang-2.6.jar'),"-Djava.class.path=%s" % (jarpath + 'zaOpenapiSdk.jar'))
         jpype.attachThreadToJVM()           
         JDClass =jpype.JClass("com.zhongan.openapi.security.signature.SignatureUtils")
         try:
                encryptmessage =JDClass.rsaEncrypt(params,publicKey,"")
                return encryptmessage
         except Exception as e:
               BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
               path = BASE_ROOT+"/pss/EncryptException_log.txt" 
               r=open(path,"w")
               r.write(str(e))
               r.close()   


#分段解密好用的            
#             parameters = self.sort(params)
#             message = parameters.encode('utf-8')
#             key = rsa.PublicKey.load_pkcs1_openssl_pem(publicKey)
#             if len(message) > 117:
#                         tmp=[]
#                         for i in range(int(len(message)/117+1)):
#                             t = message[i * 117:(i + 1) * 117]
#                             g = rsa.encrypt(t, key)
#                             b = base64.b64encode(g).decode('utf8')
#                             tmp.append(b)
#                         encryptmessage =''.join(tmp)
#                         return encryptmessage
#             else:
#                    g = rsa.encrypt(message, key)
#                    b = base64.b64encode(g)
#                    encryptmessage =  b.decode('utf8')
#                    return encryptmessage



#最初的  
# #             filterParam = sorted(self.filterParam(params).items(), key=lambda e:e[0], reverse=False)
#             parameters = self.sort(self.filterParam(params))
#             message = parameters.encode('utf-8')
#             key = rsa.PublicKey.load_pkcs1_openssl_pem(publicKey)
#             d = rsa.encrypt(message,key)
# #             key = load_privatekey(FILETYPE_PEM, open("private.pem").read())  
# #             d =  sign(key, rawData, 'sha1')  #d为经过SHA1算法进行摘要、使用私钥进行签名之后的数据  
#             b = base64.b64encode(d)  #将d转换为BASE64的格式  
#             return b.decode('utf8')

    """
    对参数进行加签
    @param params 待加签参数
    @param privateKey 自己的私钥 
    """
    def sign(self,params,privatekey):   
         parameters = self.sort(params)      
         #privatekey = "MIICeQIBADANBgkqhkiG9w0BAQEFAASCAmMwggJfAgEAAoGBANI2WVxhzKaN3Dq0F7koLWGlWgOfDQaVwacPF0180KJW/Vh1oRVauRbwCw2ARuaDdOv+p2AAxjVfcccYV5dCliLFChBVFZo7IgwnK4z9XBQm2gHQC+YXHX7N+SMPjzWFgkqz8UP54ioBz4T4J3CGOjE3Jt2qTHVIR9mVMWr4reIPAgMBAAECgYEAob/oKsmmK1Jk71a8GmDr6oLNLJQp9bMt+1oFWD5+WywMbRC2DjRsz1WNa6oU5DKquRyNtbVizpbOeaAlZeJ6moky2x8s9KjqSQ/EVZVNYYP+/gyUDY+XP+LFbJfug+jjpsUaC415kcUWgCz/XywiQbn9bXY1ogGix4jt4H8a0SECQQDxWm0UK4L82C4LvjqU8OUDJkecGGpG8TlYYYEkoCxArv+sAPDMBsVC3ENeGteJPY8nkmoNSypLHdi6yJ+/eYLtAkEA3vghD3K7XmCuhPN/j343jz2yjLgTxCCT3x3rpH8CAJQaHA7csew1/NJfx38qCavDr8eV2fLQQxg1jJbCgdKtawJBALtBHEY86BkCJN+JjOwH5rbF2WNbcgFuoL5YkBj5iLv6ynUKGclCK4QPXtlBXB6nu0zJhSyhN8Ql+QQaKg8l2JUCQQDRaVojmC5CRaujUs7Lhk/ISLoZUAnAephnRUK8DE1lHbQoBg1hTeimuy8Zv2VMD/aKcXlcaaEQYvxoPnAQXj5hAkEAib4P01m8piRU/bDdwgHxWhhxkpaIdWpZmlUybwITMSSxVpB06+SKSCBVpvlzIDWPg7C/G2IP5TSzDkvlpOYwmQ=="
         #privatekey ="MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAMXdFU2BPeIv5myGaOpPr2GxMIyPR8bFShCTsMkyokWmEIJ3eRgIbLu1orhJj4sP7Ils2PAKMFkXKJLBBD2HjM1sHvrhh0v2SUweOtP2Y8GXS/68gCKAHzfd8+LVBrjYJ4XwIM4JgCgHZdtgvQvvDExtgAyaH/wTgS15sXDj56c9AgMBAAECgYBhlXHmMbGVlk4sg/XGadpzcfIhwKCDtdWba1urPx+s/gPydH3yjmUiBqjj/tOeoBHmjRpI+J1zsuo9xpgSyIF2B3f//ABJYHIlhU7kSpyNtPikI2OPKHl5vug6hZcH1nEMo3Tm/QjL5FHA1smjoIt2RcyXlHCH6AuC58vzglfceQJBAPo39SDyCj62nR7u+5hcY02xu48XgWlB5P5ioLPdlMT/2mFsLxHLv9/NdGfEMH2xujHaiRscsPnaBjkEv3nkEy8CQQDKb3IycXIu+7UBUhLe3pugR5Td/H84ykQHEvc4g2e79hSbuuwIWtpC9HFcFT2CsM0OFQVFIWNEtlpP+EYnscFTAkA3RdcrYOwscFCC/c2sGXSCPCmvcUTQCJNaMlVHhkIPxmjqLmizaKvI92yoY2lGytTToG+7AnqBpszLGaZmeaBXAkAp2E2nxbGPqrIourlx3lwXDpTkKix2JcFYIQB/axJHVT+/TS07MOSLEJJaMX3MhRVuAsRbHOKzMmqKu0xtKh5HAkEApGnv1hHwrUppUy6xO09AaqitQbr3PewbucGQ3a9WezbUBkRFCrJe7B8Yhjl9Fq52WGFaOvX4ldEDl+stfj3yrQ=="
         jvmPath = jpype.getDefaultJVMPath() 
         jarpath = os.path.join(os.path.abspath('.'), BASE_DIR+'/pss/zhonganjar/')
         try:
                if  not jpype.isJVMStarted():                     
                         jpype.startJVM(jvmPath,"-ea", "-Djava.class.path=%s" % (jarpath + 'commons-lang-2.6.jar'),"-Djava.class.path=%s" % (jarpath + 'commons-lang-2.6.jar'),"-Djava.class.path=%s" % (jarpath + 'zaOpenapiSdk.jar'))  
                jpype.attachThreadToJVM()           
                JDClass =jpype.JClass("com.zhongan.openapi.security.signature.SignatureUtils")
                signmessage =JDClass.rsaSign(parameters,privatekey,"")
                return signmessage
         except Exception as e:
               BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
               path = BASE_ROOT+"/pss/SignException_log.txt" 
               r=open(path,"w")
               r.write(str(e))
               r.close()   
#最初的好用
#             parameters = self.sort(params)
#             signdata = parameters.encode('utf-8')
#             with open(BASE_DIR+privateKey,'rb') as f:
#                 keydata = f.read()
#             privatekey = rsa.PrivateKey.load_pkcs1(keydata)
#             signature = rsa.sign(signdata, privatekey, 'SHA-1')
#             signmessage = base64.b64encode(signature).decode('utf-8')
#             return signmessage #将d转换为BASE64的格式  

    """
    返回值验签
    @param params 返回值键值对（除去sign）
    @param sign 返回值中的签名
    @param publicKey 众安公钥
    """
    def checkSign(self,params, sign, publicKey) :
        params = self.filterParam(params)
        parameters = self.sort(params).encode('utf-8')
        signature = base64.b64decode(sign) 
        key = rsa.PublicKey.load_pkcs1_openssl_pem(publicKey)
        checkSign = rsa.verify(parameters, signature, key)
        return checkSign
 
    
    """
    对参数进行解密
    @param $encryptedData 待解密参数  
    @param $privateKey 自己的私钥  
    """
    def  decrypt(self,encryptedData, privatekey) :          
#          with open(BASE_DIR+privateKey,'rb') as f:
#                 keydata = f.read()
#          privatekey = rsa.PrivateKey.load_pkcs1(keydata)
         #privatekey = "MIICeQIBADANBgkqhkiG9w0BAQEFAASCAmMwggJfAgEAAoGBANI2WVxhzKaN3Dq0F7koLWGlWgOfDQaVwacPF0180KJW/Vh1oRVauRbwCw2ARuaDdOv+p2AAxjVfcccYV5dCliLFChBVFZo7IgwnK4z9XBQm2gHQC+YXHX7N+SMPjzWFgkqz8UP54ioBz4T4J3CGOjE3Jt2qTHVIR9mVMWr4reIPAgMBAAECgYEAob/oKsmmK1Jk71a8GmDr6oLNLJQp9bMt+1oFWD5+WywMbRC2DjRsz1WNa6oU5DKquRyNtbVizpbOeaAlZeJ6moky2x8s9KjqSQ/EVZVNYYP+/gyUDY+XP+LFbJfug+jjpsUaC415kcUWgCz/XywiQbn9bXY1ogGix4jt4H8a0SECQQDxWm0UK4L82C4LvjqU8OUDJkecGGpG8TlYYYEkoCxArv+sAPDMBsVC3ENeGteJPY8nkmoNSypLHdi6yJ+/eYLtAkEA3vghD3K7XmCuhPN/j343jz2yjLgTxCCT3x3rpH8CAJQaHA7csew1/NJfx38qCavDr8eV2fLQQxg1jJbCgdKtawJBALtBHEY86BkCJN+JjOwH5rbF2WNbcgFuoL5YkBj5iLv6ynUKGclCK4QPXtlBXB6nu0zJhSyhN8Ql+QQaKg8l2JUCQQDRaVojmC5CRaujUs7Lhk/ISLoZUAnAephnRUK8DE1lHbQoBg1hTeimuy8Zv2VMD/aKcXlcaaEQYvxoPnAQXj5hAkEAib4P01m8piRU/bDdwgHxWhhxkpaIdWpZmlUybwITMSSxVpB06+SKSCBVpvlzIDWPg7C/G2IP5TSzDkvlpOYwmQ=="
         #privatekey ="MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAMXdFU2BPeIv5myGaOpPr2GxMIyPR8bFShCTsMkyokWmEIJ3eRgIbLu1orhJj4sP7Ils2PAKMFkXKJLBBD2HjM1sHvrhh0v2SUweOtP2Y8GXS/68gCKAHzfd8+LVBrjYJ4XwIM4JgCgHZdtgvQvvDExtgAyaH/wTgS15sXDj56c9AgMBAAECgYBhlXHmMbGVlk4sg/XGadpzcfIhwKCDtdWba1urPx+s/gPydH3yjmUiBqjj/tOeoBHmjRpI+J1zsuo9xpgSyIF2B3f//ABJYHIlhU7kSpyNtPikI2OPKHl5vug6hZcH1nEMo3Tm/QjL5FHA1smjoIt2RcyXlHCH6AuC58vzglfceQJBAPo39SDyCj62nR7u+5hcY02xu48XgWlB5P5ioLPdlMT/2mFsLxHLv9/NdGfEMH2xujHaiRscsPnaBjkEv3nkEy8CQQDKb3IycXIu+7UBUhLe3pugR5Td/H84ykQHEvc4g2e79hSbuuwIWtpC9HFcFT2CsM0OFQVFIWNEtlpP+EYnscFTAkA3RdcrYOwscFCC/c2sGXSCPCmvcUTQCJNaMlVHhkIPxmjqLmizaKvI92yoY2lGytTToG+7AnqBpszLGaZmeaBXAkAp2E2nxbGPqrIourlx3lwXDpTkKix2JcFYIQB/axJHVT+/TS07MOSLEJJaMX3MhRVuAsRbHOKzMmqKu0xtKh5HAkEApGnv1hHwrUppUy6xO09AaqitQbr3PewbucGQ3a9WezbUBkRFCrJe7B8Yhjl9Fq52WGFaOvX4ldEDl+stfj3yrQ=="
         jvmPath = jpype.getDefaultJVMPath() 
         jarpath = os.path.join(os.path.abspath('.'), BASE_DIR+'/pss/zhonganjar/')
         if  not jpype.isJVMStarted():         
               jpype.startJVM(jvmPath,"-ea", "-Djava.class.path=%s" % (jarpath + 'commons-lang-2.6.jar'),"-Djava.class.path=%s" % (jarpath + 'commons-lang-2.6.jar'),"-Djava.class.path=%s" % (jarpath + 'zaOpenapiSdk.jar'))    
         jpype.attachThreadToJVM()           
         JDClass =jpype. JClass("com.zhongan.openapi.security.signature.SignatureUtils")
         try:
               decryptmessagell =JDClass.rsaDecrypt(encryptedData,privatekey,"")
               return decryptmessagell
         except Exception as e:
               BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
               path = BASE_ROOT+"/pss/DecryptException_log.txt" 
               r=open(path,"w")
               r.write(str(e))
               r.close()   
         
#big file
#         BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
#         path = BASE_ROOT+"/yunzhibao_test.txt" 
#         r=open(path,"w")
#         r.write(encryptedData)
#         r.close()
#         outFile = open("/home/gyd/workspace/yunzhibao/pss/yunzhibao_test.txt", 'rb')
#         infile = open("/home/gyd/workspace/yunzhibao/pss/zhongkefangde_test.txt", 'wb')
#         with open(BASE_DIR+privateKey,'rb') as f:
#                 keydata = f.read()
#         privatekey = rsa.PrivateKey.load_pkcs1(keydata)
#         rsa.bigfile.decrypt_bigfile(outFile, infile, privatekey)

# 分段    
#          encryptedData = base64.b64decode(encryptedData)
#          with open(BASE_DIR+privateKey,'rb') as f:
#                  keydata = f.read()
#          privatekey = rsa.PrivateKey.load_pkcs1(keydata)
#          if len(privateKey)>1000:
#              step = 256
#          else:
#              step = 128
#          #tmp=[]
#          tmps=""
#          #for i in range(int(len(encryptedData)/step+1)):
#          for i in range(3):
#                              t = encryptedData[i * step:(i + 1) * step]               
#                              messageencrypted = rsa.decrypt(t, privatekey) 
#                              gyd = messageencrypted.decode('utf8')                                        
# #                              b = messageencrypted.decode('utf8')
# #                              tmp.append(b)
#                               
#                              b= str(messageencrypted).replace('b\'',"")[:-1]
#                              tmps+=b
#                               
#          tmps = "b\'"+tmps+"\'"
#          encryptmessage = tmps.encode("utf8") 
#  
# #         encryptmessage =''.join(tmp)
#          return encryptmessage
                
    
#最初的   
#         encryptedData = base64.b64decode(encryptedData)
#         with open(BASE_DIR+privateKey,'rb') as f:
#                 keydata = f.read()
#         privatekey = rsa.PrivateKey.load_pkcs1(keydata)
#         message = rsa.decrypt(encryptedData, privatekey)
#         return message.decode('utf8')


    """
    保证只传有值的参数
    @param unknown $param  
    """
    def filterParam(self , params) :
        result = {}
        for ( key,value) in params.items():
            # 没有值的
            if ((value== '') and  value != 0) :
                continue
            if (isinstance(value,dict)) :
                result [key] = value
            else:
                 if value:
                      result [key] = value
                 else:
                     result [key] = ''
        return result
    
    """
    排序，生成字符串
    @param unknown $param  
    """
    def sort(self,params):
        if hasattr(params, "items"):
            keys = list(params.keys())  # sudoz: Py3
            keys.sort()
            parameters = "{%s}" % (
                                     str().join(
                                             '"%s":"%s",' % (key, params[key]) for key
                                             in keys))
            return  parameters[:-2]+"}"