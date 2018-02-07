# coding=utf-8
"""
众安保险公司sdk

 作者: yzb
 创建时间: 2016-07-26 
 版本: 1.0

"""
import time
import datetime
class DateUtils:
#
#      获取当前时间戳：yyyyMMddhhmmssSSS
#       @return string
#      
    def withMicrosecond() :
        datetimeNow = datetime.datetime.now()
        nowTime = datetimeNow.strftime('%Y%m%d%H%M%S')+datetimeNow.strftime('%f')[:3]
        return nowTime
    