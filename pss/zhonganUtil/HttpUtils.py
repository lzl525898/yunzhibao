# -*- coding: utf-8 -*-
"""
众安保险公司sdk

 作者: yzb
 创建时间: 2016-07-26 
 版本: 1.0

"""
import urllib

class HttpUtils:
    #请求头
        headers = { 
        'contentType' : "application/x-www-form-urlencoded;charset=utf-8"
         }
        def doPost(self,url,values): 
            ''' 
            post请求 
            @param 参数URL 
            @param 字典类型的参数 
            ''' 
            try:
                    params=urllib.parse.urlencode(values).encode(encoding='UTF8')
                    req = urllib.request.Request(url, params,self.headers)
                    r = urllib.request.urlopen(req)
                    #print(res.status, res.reason)  
                    if( r.status != 200 ):  
                        print( r.reason)
                        exit()  
                    res=r.read().decode('utf8') 
                    return res
            except urllib.error.HTTPError as e:
                    print(e.code)
                    print(e.read().decode("utf8"))
