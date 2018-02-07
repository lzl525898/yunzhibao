from django import template
from mongoengine.base.datastructures import BaseDict
from django.conf import settings
from bson.objectid import ObjectId
from common.models import InsuranceCompany
from common.models import Certificate, Coupon
from common.models import Client
from common.models import InsuranceProducts
from common.models import UseCoupon
from common.models import Ordering,  Cargo, CargoArea,PlatformProducts,InquiryInfo
import datetime
from django.contrib.gis.tests.layermap.tests import city_shp
register = template.Library()


WEEKDAY_MAP = {
    '1': '周一',
    '2': '周二',
    '3': '周三',
    '4': '周四',
    '5': '周五',
    '6': '周六',
    '7': '周日', }


# @register.filter(name='LPrint')
# def l_print(value):
#     return print(value)


# 格式化安全电话号
@register.filter
def safe_phone(value):
    if not isinstance(value, str):
        value = str(value)
    if len(value) > 10:
        return value[:3] + '****' + value[-4:]
    else:
        return value


@register.filter
def settings_value(name):
    if not isinstance(name, str):
        name = str(name)
    return getattr(settings, name, "")


#将数字转换为周
@register.filter
def weekday(value):
    return WEEKDAY_MAP.get(value, '无')


# 若值为空则返回默认图片
@register.filter
def default_jpg(value):
    if value is not None and value != '':
        return value
    else:
        return 'default/default.jpg'


# 获取choices中的value
# @register.filter(name='displayName')
# def display_name(value, arg):
#     # print('value.get_' + arg + '_display')
#     return eval('value.get_' + arg + '_display')()

@register.filter(name='displayName')
def display_name(value, arg):
    # print("{0}\t{1}\t{2}\t{3}".format(
    #     value.id,
    #     getattr(value, arg),
    #     eval('value.get_' + arg + '_display')(),
    #     getattr(value, 'get_' + arg + '_display')()
    # ))
    # print(getattr(value, '__get_field_display')(arg))
    try:
        key = getattr(value, arg)
        return dict(getattr(getattr(type(value), arg), 'choices')).get(key, key)
    except Exception:
        return getattr(value, arg, arg)
    # return eval('value.get_' + arg + '_display')()


@register.filter(name='intTime')
def int_time(value):
    if isinstance(value, int):
        return datetime.date.fromtimestamp(value)
    else:
        return value


# 获取choices中的value
@register.filter(name='displayWithChoices')
def display_name_choice(key, choices):
    if choices:
        if isinstance(choices[0], (list, tuple)):
            for k, v in choices:
                if k == key:
                    return v
            return key
        else:
            return key
    else:
        return key


# if checkbox is on return checked
@register.filter(name='checkOn')
def check_on(checked):
    if checked is True or checked == 'on':
        return 'checked'
    else:
        return ''


# 获取字典中的值
@register.filter(name='getValue')
def get_value(container, key='zh-cn'):
    if container is None:
        return ""
    if isinstance(container, dict):
        if key is None or key == '':
            for key in container:
                return container[key]
        else:
            if key in container:
                return container.get(key)
            else:
                for key in container:
                    return container[key]
    elif isinstance(container, list) or isinstance(container, tuple):
        if key is None or key == '':
            return container[0] if len(container) > 0 else ''
        else:
            return container[key] if len(container) > key else ''
    return ''


# 获取字典中真实的值
@register.filter(name='getRealValue')
def get_real_value(container, key):
    if container is None:
        return ""
    if isinstance(container, dict):
        if key is None or key == '':
            return ''
        else:
            if key in container:
                return container.get(key)
            else:
                return ''
    elif isinstance(container, list) or isinstance(container, tuple):
        if key is None or key == '':
            return ''
        else:
            return container[key] if len(container) > key else ''
    return ''


# 构造一个列表用于for循环
@register.filter(name='getRange')
def get_range(end, start=0, step=1):
    if isinstance(end, int):
        return range(start, end, step)
    else:
        end = round(end)
        return range(start, end, step)


@register.filter(name='getInt')
def get_int(value):
    if isinstance(value, int):
        return value
    else:
        value = round(value)
        return value


@register.filter(name='getAttrs')
def get_attrs(obj):
    result = list()
    for attr in dir(obj):
        if not attr.startswith('_'):
            value = getattr(obj, attr)
            # bool 是int的子类，使用isinstance(value, int)即可保证bool通过验证
            if isinstance(value, str) or isinstance(value, float) or isinstance(value, int):
                result.append(attr)
    return result


@register.filter(name='getAttr')
def get_attr(obj, attr):
    if hasattr(obj, attr):
        return getattr(obj, attr, attr)
    return attr


@register.filter(name='getType')
def get_type(obj, attr):
    if hasattr(obj, attr):
        value = getattr(obj, attr)
        if isinstance(value, bool):
            return 'checkbox'
        elif isinstance(value, int):
            return 'number'
        elif isinstance(value, float):
            return 'float'
        else:
            return 'text'
    return 'None'


@register.filter(name='showValue')
def show_value(value):
    if isinstance(value, bool):
        if value:
            return '是'
        else:
            return '否'
    else:
        return value


@register.filter(name='getDictAttrs')
def get_dict_attrs(obj):
    result = list()
    for attr in dir(obj):
        if not attr.startswith('_'):
            value = getattr(obj, attr)
            # BaseDict是dict的子类，使用BaseDict可以保证其他dict不会通过验证从而保证不会惨入一些奇奇怪怪的东西
            if isinstance(value, BaseDict):
                result.append(attr)
    return result


@register.filter(name='safeParameters')
def get_safe_parameters(parameters):
    if isinstance(parameters, str):
        return parameters.replace('&', '&amp;').replace("'", '&apos;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    else:
        return parameters
# 判断公司是否存在文件
# @register.filter(name='DocumentCompany')
# def document_company(company_id):
#     if company_id and isinstance(company_id, ObjectId):
#         company = InsuranceCompany.objects(id=company_id).first()
#         if company:
#             return company.name
#         return '暂无'
#     else:
#         return '暂无'


# 对比模态框中的checkbox是否选中
@register.filter(name='CompareDocumentChecked')
def compare_document_checked(insurance_document_id):
    if insurance_document_id and isinstance(insurance_document_id, ObjectId):
        company = InsuranceCompany.objects(car_documents__id=insurance_document_id).first()
        if company:
            return True
        return False
    else:
        return False


# 对比模态框中的checkbox是否选中
@register.filter(name='toString')
def to_string(value):
    return str(value)


# 默认空时候返回注册用户
@register.filter(name='DefaultIfNull')
def default_if_null(value, default):
    if value:
        return value
    else:
        return default


    # 注册用户查看用户状态
@register.filter(name='GetCertificateState')
def get_certificate_state(registered_id):
    if isinstance(registered_id, ObjectId):
        if registered_id:
            registered = Client.objects.get(id=registered_id)
            if register:
                certificate = Certificate.objects(client=registered).first()
                if certificate:
                    if certificate.state == 'init':
                        return '待审核'
                    elif certificate.state == 'success':
                        return '已审核'
                    elif certificate.state == 'fail':
                        return '已退回'
                    else:
                        return '认证状态错误'
                else:
                    return '未认证'
            else:
                return '用户不存在'
        else:
            return ''
    else:
        return ''

# 分转元 ，并且格式化
@register.filter(name='FenToYuan')
def fen_to_yuan(value):
    if isinstance(value, int):
        value = round(value/100.0, 2)
        return value
    else:
        value = round(value/100.0, 2)
        return str(value)+'数据库中分，出错'


# 格式化费率
@register.filter(name='RateFormat')
def rate_format(value):
    if isinstance(value, float):
        value = value * 100000/100000
        return "%f" % value
    else:
        value = value * 100000/100000
        return str(value)+'数据库中分，出错'



# 判断有效时间
@register.filter(name='getEffective')
def get_effective(value):
    if isinstance(value, Coupon):
        if value.end_date > datetime.datetime.now():
            return ''
        else:
            return '已过期'
    else:
        return ''


# 优惠券就算费率
@register.filter(name='CouponRateAfter')
def coupon_rate_after(value, rate):
    if isinstance(value, float):
        return value * rate
    else:
        return ''


# 优惠券就算费率
@register.filter(name='GetRateIsCheap')
def coupon_rate_after(product, client):
    if isinstance(product, InsuranceProducts) and isinstance(client, Client):
        use_coupon_set = UseCoupon.objects(client=client)
        if use_coupon_set:
            temp = 1.0
            item = None
            for use_coupon in use_coupon_set:
                if use_coupon.coupon.end_date > datetime.datetime.now():
                    if use_coupon.coupon.product == product:
                        if use_coupon.coupon.rate < temp:
                            temp = use_coupon.coupon.rate
                            item = use_coupon.coupon
            if temp and item:
                return "%f" % (product.rate * 1000000 / 1000000 * temp)
            else:
                return "%f" % product.rate
        else:
            return "%f" % product.rate
    else:
        return ''
    
# 转化2016-07为2016年07月,年检时间
@register.filter(name='dateformat')
def date_format(value):
    list = value.split("-")
    return list[0]+"年"+list[1]+"月"


# 查找包装方式
@register.filter(name='PackMethod')
def pack_method(value):
    num_pack=value
    print(num_pack)
    order = Ordering()
    pack_method_list=order.PACK_METHOD
    try:
        name = num_pack
        test =0
        for pack_method in pack_method_list:
            for pack_detail in pack_method[1]:
                if pack_detail[0]==num_pack:
                    name=pack_detail[1]
                    test=1
                    break
            if test==1:
                break
        if name==num_pack:
              name=name+"未找到订单货物的包装方式"
        return name
    except:
        return "未找到订单对应的包装方式"

# 货物名称翻译
@register.filter(name='CargoName')
def cargo_name(value):
    cargo_number=value
    print("cargo_number=="+cargo_number)
    cargo_set =Cargo.objects(cargo_number=cargo_number).first()
    print(cargo_set)
    if cargo_set:
        name=cargo_set.cargo_name
        return name
    else:
        message=cargo_number+"未找到对应货物"
        return message
    
    
# 翻译运输方式
@register.filter(name='TransportType')
def transport_type(value):
    transport_number=value
    print("transport_number=="+transport_number)
    order = Ordering()
    transport_type_list=order.TRANSPORT_TYPE
    try:
        name = ""
        test =0
        for transport_type in transport_type_list:
            if transport_type[0]==transport_number:
                name=transport_type[1]
                test=1
                break
        if test ==1:
            return name
        else:
            message = transport_number +"未找到对应运输方式"
            return message
    except:
        return "未找到订单对应的运输方式"
        
# 翻译地址编码
@register.filter(name='CityName')
def address_name(value):
    address_number = value
    try:
        print(address_number)
        name_detail = address_number.split(" ")
        count = len(name_detail)
        address_detail=""
        for i in range(count):
            prov_code = name_detail[i]
            if prov_code:
                prov_name = CargoArea.objects(code=prov_code).first().name
                address_detail = address_detail + prov_name+" "
            else:
                continue
        return address_detail.strip()
    except:
        message = address_number+"未找到订单对应编码的地址名称"
        return message

# 分转元 ，并且格式化
@register.filter(name='PriceFenToYuan')
def price_fen_to_yuan(value):
    if isinstance(value, int):
        value = value/100
        value = int(value)
        return value
    else:
        value = value/100
        return str(value)+'数据库中分，出错'

# 分转元 ，并且格式化
@register.filter(name='FenToWanYuan')
def fen_to_wan_yuan(value):
    if isinstance(value, int):
        value = int(value/1000000)
        value = str(value) + "万"
        return value
    else:
        value = int(value/1000000)
        return str(value)+'数据库中分，出错'
    
# 微信订单列表页面，产品类型翻译
@register.filter(name='WXProductType')
def wx_product_type(value):
    a=value
    platform_products=PlatformProducts()
    product_type_list = platform_products.PRODUCT_TYPE
    name = 1
    for product_type in product_type_list:
         print( product_type[0]  )
         if product_type[0] == a :
             name = product_type[1] 
             break
    if name == 1:
        return str(a)+'未找到产品类型名称'
    else:
        return str(name)


# 微信翻译地址编码
@register.filter(name='WXCityName')
def wx_address_name(value):
    address_number = value
    address_detail1 =""
    try:
        print(address_number)
        name_detail = address_number.split(" ")
        count = len(name_detail)
        address_detail=""
        for i in range(count):
            prov_code = name_detail[i]
            if prov_code:
                prov_name = CargoArea.objects(code=prov_code).first().name
                address_detail = address_detail+" " + prov_name
            else:
                continue
        a =len(address_detail)
        if a>15:
            address_detail1 = address_detail[:15]
            address_detail1 = address_detail1+"…"
        if address_detail1:
            return address_detail1
        return address_detail
    except :
        message = address_number+"未找到订单对应编码的地址名称"
        return message

# 微信第三方支付状态翻译
@register.filter(name='WXStatusType')
def wx_status_type(value):
    if value=="init":
         name ="未完成"
    elif value=="success":
         name ="成功"
    elif value=="failure":
         name = "失败"
    else:
          name = "状态错误"
    return str(name)


# 机动车保险-车辆类型翻译
@register.filter(name='CX_CarType')
def cx_car_type(value):
    car_type_name = value
    car_type_list = InquiryInfo.CAR_TYPE
    car_type_detail = ""
    for car_type in car_type_list:
        b=car_type[0]
        print(b)
        if car_type_name == car_type[0]:
            car_type_detail = car_type[1]
            break
    if car_type_detail:
        return car_type_detail
    else:
        message = str(car_type_name ) +"翻译失败请联系管理员"
        return message
    
# 机动车保险-使用性质翻译
@register.filter(name='CX_UseProperty')
def cx_use_property(value):
    use_property_name = value
    use_property_list = InquiryInfo.USE_PROPERTY 
    use_property_detail =""
    for use_property in use_property_list:
        b=use_property[0]
        print(b)
        if use_property_name == use_property[0]:
            use_property_detail = use_property[1]
            break
    if use_property_detail:
        return use_property_detail
    else:
        message = str(use_property_name ) +"翻译失败请联系管理员"
        return message
    
# 机动车保险-订单状态
@register.filter(name='WX_OrderState')
def cx_order_state(value):
    oreder_type_name = value
    oreder_type_list = InquiryInfo.ORDER_TYPE 
    use_property_detail =""
    for use_property in oreder_type_list:
        if oreder_type_name == use_property[0]:
            use_property_detail = use_property[1]
            break
    if use_property_detail:
        return use_property_detail
    else:
        message = str(oreder_type_name ) +"翻译失败请联系管理员"
        return message   
    
# # 机动车保险-城市名称
# @register.filter(name='WX_CityName')
# def cx__city_name(value):
#     oreder_city_obj = value
#     if oreder_city_obj:
#         return oreder_city_obj.name
#     else:
#         message = str(oreder_city_obj ) +"翻译失败请联系管理员"
#         return message      
    
     
# 机动车保险-车辆类型
@register.filter(name='WX_CarType')
def cx_car_type(value):
    car_type_name = value
    car_type_list = InquiryInfo.ORDER_CAR_TYPE 
    car_type_detail =""
    for car_type in car_type_list:
        if car_type_name == car_type[0]:
            car_type_detail = car_type[1]
            break
    if car_type_detail:
        return car_type_detail
    else:
        message = str(car_type_name ) +"翻译失败请联系管理员"
        return message   
    
# 机动车保险-玻璃险
@register.filter(name='WX_GlassInsurance')
def cx_glass_insurance(value):
    car_type_name = value
    car_type_detail =""
    if car_type_name == "import":
        car_type_detail = "进口"
    elif car_type_name == "china":
        car_type_detail = "国产"
    if car_type_detail:
        return car_type_detail
    else:
        message = str(car_type_name ) +"翻译失败请联系管理员"
        return message   

    
# 车辆保险用户类型单位或个人
@register.filter(name='WX_UserType')
def cx_user_type(value):
    user_type_name = value
    user_type_list = InquiryInfo.USER_CLASSIFY 
    user_type_detail =""
    for user_type in user_type_list:
        if user_type_name == user_type[0]:
            user_type_detail = user_type[1]
            break
    if user_type_detail:
        return user_type_detail
    else:
        message = str(user_type_name ) +"翻译失败请联系管理员"
        return message   
    
    
# 车辆保险详情日期类型处理
@register.filter(name='WX_DataType')
def cx_data_type(value):
    user_type_name = value
    data_detail =""
    if user_type_name:
          #data_detail= user_type_name
          data_detail= user_type_name.strftime('%Y-%m-%d')
    if data_detail:
        return data_detail
    else:
        message = str(user_type_name ) +"翻译失败请联系管理员"
        return message   
    
    # 车辆保险保额翻译 格式化
@register.filter(name='Coverage_Price')
def coverage_price(value):
    if isinstance(value, int):
        value = round(value/100.0, 2)#元
        if value/10000 ==int(value/10000):
            message = str(int(value/10000))+'万'
            return message
        elif value/1000 ==int(value/1000):
            message = str(int(value/1000))+'千'
            return message
        else:
            return str(value)+'元'
    else:
        value = round(value/100.0, 2)
        return str(value)+'数据库中分，出错'
    
# 机动车保险-使用性质翻译
@register.filter(name='String_Interception')
def String_Interception(value):
    if isinstance(value, str):
        if len(value)>8:
            return value[0:7]+'…'
        else:
            return  value
    return '不是字符串类型数据'

#二手商品价格翻译
@register.filter(name='String_Goods_Price')
def String_Goods_Price(value):
    try:
        detail = str(value)
        if len(detail)>6:
            return detail[0:5]+'…'
        else:
            return  detail
    except:
        return '不能转化为字符串格式'
    
#自由 截取字符串
@register.filter(name='CutString')
def cut_out_String(value, arg):
    try:
        count=int(arg)
    except:
        return str(value)+'过滤器中请输入数字'
    try:
        detail = str(value)
        if len(detail)>count and count>1:
            count_less = count-1
            return detail[0:count_less]+'…'
        else:
            return  detail
    except:
        return '不能转化为字符串格式'







    