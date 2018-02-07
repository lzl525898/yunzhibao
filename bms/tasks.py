from wss.views_sendmessage import  send_wx_message
from common import tools_string
from celery import Celery
from InsuranceSite.celery import youlinapp
import time
import datetime
from common.models import *
@youlinapp.task    
def TimingTaskWithOut():
    print("time task!!!")
    #优惠券即将过期通知用户
    coupon_record_set = UseCoupon.objects()
    for  coupon_record in coupon_record_set:
            import datetime
            d1 = datetime.datetime.now()
            d2 = coupon_record.coupon.end_date
            print((d2-d1).days)
            if (d2-d1).days == 5:
                content = "您的运之宝账户优惠券还有5天到期，请在我的账户-优惠券查看详情，联系客服获取更多优惠券，运之宝客服15910731868"
               # touser = "oYXlSwfedYTw0OtzfRy2SYpPrNE8"
                touser = coupon_record.client.wx_id
                send_wx_message(touser,content)
                
                
                
    car_d1 = datetime.datetime.now()          
    car_list = CarCertificate.objects()
    print("liability_date_stop——time task!!!")
    for  car in car_list:  
         if car.state =="success":
            #强险过期通知管理员
            car_d2 = car.liability_date_stop        
            phone = car.client.profile.phone
            if (car_d2-car_d1).days == 30:
                content_liability ="手机号为"+str(phone)+"的用户的交强险还差30天到期，请联系用户续交保险费用！"
                string_tools = tools_string.StringTools()
                touser = string_tools.get_string("administrator_wx_id")
                send_wx_message(touser,content_liability) 
            #商险过期通知管理员
            car_d3 = car.commercial_date_stop
            if (car_d3-car_d1).days == 30:
                 content_commercial ="手机号为"+str(phone)+"的用户的商业保险还差30天到期，请联系用户续交保险费用！"
                 string_tools = tools_string.StringTools()
                 touser = string_tools.get_string("administrator_wx_id")
                 send_wx_message(touser,content_commercial) 
                 
             #年检过期通知用户    
#             car_d4_str = car.plate_expiration_periods +str("-01")   
#             car_d4 = datetime.datetime.strptime(car_d4_str,'%Y-%m-%d')
#             if (car_d4-car_d1).days == 30:         
#                   content_plate_expiration ="尊敬的用户您好，您的年检还有30天即将到期，请及时进行年检！"      
#                   touser_yh = car.client.wx_id
#                   send_wx_message(touser_yh,content_plate_expiration) 
                        
        