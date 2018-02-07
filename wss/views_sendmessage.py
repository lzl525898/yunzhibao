import urllib.request
import json
from common.models import *
from common.models import BaseSettings as SiteSettings
def send_wx_message(touser, content):
#     appid = "wxa88405ef667fd9da"
#     secret = "bf509ce0856edb5e7b5c3ae48bb0888a"
    
    site_settings = SiteSettings.get_settings()
      
    appid = site_settings.wechat_app_id 
    secret = site_settings.wechat_app_secret
    
    accessUrl = url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+appid+'&secret='+secret
    sendUrl =  "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token="
    
    d= {
        "touser":touser,
        "msgtype":"text",
        "text":
        {
             "content":content,
        }
    }
    #data = json.dumps(d)
    data =  json.dumps(d, ensure_ascii=False) 
    
    f = urllib.request.urlopen(accessUrl)
    accessT = f.read().decode("utf-8")
    jsonT = json.loads(accessT)
    accessToken = jsonT["access_token"]
    
    html =  urllib.request.urlopen(sendUrl+ accessToken,data.encode("utf-8"))
    result = json.loads(html.read().decode("utf-8"))
    return result["errcode"]
    