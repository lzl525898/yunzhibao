import urllib.request
import json
#test
import os
#from billiard.managers import Token
from common.models import *


class MenuManager:
    site_settings = SiteSettings.get_settings()
    appid = site_settings.wechat_app_id
    secret = site_settings.wechat_app_secret
#     appid = "wxa88405ef667fd9da"
#     secret = "bf509ce0856edb5e7b5c3ae48bb0888a"
    accessUrl = url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+appid+'&secret='+secret
    del_menuUrl = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token="
    createUrl = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token="
    getMenuUri="https://api.weixin.qq.com/cgi-bin/menu/get?access_token="
    
    def get_access_token(self):
        f = urllib.request.urlopen(self.accessUrl)
        accessT = f.read().decode("utf-8")
        jsonT = json.loads(accessT)
        print(jsonT)
        return jsonT["access_token"]
    
    def del_menu(self, accessToken):
        html = urllib.request.urlopen(self.del_menuUrl + accessToken)
        result = json.loads(html.read().decode("utf-8"))
        return result["errcode"]
    
    def createmenu(self, accessToken):
        host = request.get_host()
        
        url_product_list            ='http://'+host+'/wss/insure/product_list/ '
        url_transport_list          ='http://'+host+'/wss/propaganda/transport_list'
        url_manager_list            ='http://'+host+'/wss/propaganda/manager_list'
        url_lawyer_list            ='http://'+host+'/wss/propaganda/lawyer_list'
        url_driver_list            ='http://'+host+'/wss/propaganda/driver_list'
        url_my_order            ='http://'+host+'/wss/mine/my_order/'
        url_my_account            ='http://'+host+'/wss/mine/my_account/'
        url_contact            ='http://'+host+'/wss/mine/contact/'
        url_my_car            ='http://'+host+'/wss/mine/my_car_list/'
        
        menu = {
                 "button":[
                      {
                           "type":"view",
                           "name":"保险产品",
                            "url":url_product_list
                           },
                             {
                           "name":"宣传推广",
                           "sub_button":[
                            {
                               "type":"view",
                               "name":"物流公司",
                               "url":url_transport_list
                            },
                            {
                               "type":"view",
                               "name":"物流管理系统",
                               "url":url_manager_list
                            },
                            {
                               "type":"view",
                               "name":"律师",
                               "url":url_lawyer_list
                            },
                            {
                               "type":"view",
                               "name":"货车司机",
                               "url":url_driver_list
                            }]
                            },
                             {
                           "name":"我的",
                           "sub_button":[
                            {
                               "type":"view",
                               "name":"我的订单",
                               "url":url_my_order
                            },
                            {
                               "type":"view",
                               "name":"我的账户",
                               "url":url_my_account
                            },
                           {
                               "type":"view",
                               "name":"我的车库",
                               "url":url_my_car
                            },
                            {
                               "type":"view",
                               "name":"联系客服",
                               "url":url_contact
                            }]

                      }]
            }
        # {"type":"click","name":"联系客服","key":"K3004_CONTACT"},
        # http://10.0.0.111:8005/wss/mine/suggestions/
        menu=json.dumps(menu, ensure_ascii=False)
#         url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token='+accessToken
#         req = urllib2.Request(url, menu)
#         response = urllib2.urlopen(req)
#         print (response)
        html = urllib.request.urlopen(self.createUrl + accessToken, menu.encode("utf-8"))
        result = json.loads(html.read().decode("utf-8"))
#         BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
#         path = BASE_ROOT+"/wss/wx_test.txt" 
#         a=str(id)
#         r=open(path,"a")
#         r.write("\n \n\n url_product_list:----------         "+url_product_list+'\n')
#         r.close()
        return result["errcode"]

    def getMenu(self):
        html = urllib.request.urlopen(self.getMenuUri + accessToken)
        print(html.read().decode("utf-8"))


if __name__ == "__main__":
    wx = MenuManager()
    accessToken = wx.get_access_token()
#     BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
#     path = BASE_ROOT+"/wss/wx_test.txt" 
#     r=open(path,"w")
#     r.write(accessToken)
#     r.close()
    # wx.del_menu(accessToken)   #删除菜单
    wx.createmenu(accessToken)  #创建菜单
    wx.getMenu()
    # print(accessToken)