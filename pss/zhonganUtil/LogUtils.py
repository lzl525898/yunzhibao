# -*- coding: utf-8 -*-
"""
众安保险公司sdk

 作者: yzb
 创建时间: 2016-07-26 
 版本: 1.0

"""
class  LogUtils :
    
    # 是否调试模式, 线上需要关闭, true|打开, false|关闭
     DEBUG = False
     #打印日志 
     def  log(msg) :
        if (self.DEBUG == true) :
            print ( "debug_log:%s - %s\n", date ( 'Y-m-d H:i:s', time () ), msg );

  
     #打印error日志

#      def logError(msg,category = 'zhongansdk') :
#         log (msg)
#         if (class_exists ( 'Logger' ) and method_exists ( 'Logger', 'logError' )) {
#             Logger::logError ( $msg, $category );
#         }
