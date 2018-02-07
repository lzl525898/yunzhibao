__author__ = 'mlzx'
import hashlib
from django.contrib.auth.decorators import login_required
from common.decorators import AdminRequired
from common.decorators import SuperAdminRequired
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from mongoengine.django.auth import User, make_password
# from common.tools_legoo import *
from common.tools import *
from bms.tools import DocumentBmsTools,checkIdcard,checkVIN
from django.shortcuts import render_to_response, HttpResponse
import traceback
import math
from common.tools_legoo import DocumentTools, DocumentFolderType, ImageTools, ImageFolderType
from common.tools import RequestTools
from common.tools_excel_export import ExcelExportTools
# from openpyxl.reader.excel import load_workbook
# import openpyxl
from django.contrib.staticfiles.templatetags.staticfiles import static
from wss.views_sendmessage import  send_wx_message
import datetime
import time
from pss.views_zhongan import ZhongAnApi
from django.conf import settings
#2017测试
from common.models import *
#发送短信
import common.tools_m5c_sms as m5c_sms_helper

#－－－－－－－－－－－－－－－－－－－－－－－－－－     机动车订单部分      －－－－－－－－－－－－－－－－－－－－－－－－
@login_required
@AdminRequired
def jdclbx_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        pay_state = request_tool.get_parameter("pay_state")
        id_client = request_tool.get_parameter("client_sign")
        search_keyword = request.POST.get('search_keyword', '')
        get_parameter = "?pay_state={0}&search_keyword={1}&id_client={2}".format(pay_state, search_keyword, id_client)
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ])+ get_parameter )

    elif request.method == 'GET':
        #2017修改用户流程
        user_set = User.objects(is_active=True)
        client_set = Client.objects().filter(user__in=user_set)
        #client_set = Client.objects().filter(user_type__ne='registered')
        data['clients'] = client_set
        request_tool.check_message(data)
        data["get_data"] = request.GET
        order_set = InquiryInfo.objects().order_by('-create_time')
        order_set = request_tool.jdcbx_filter(order_set=order_set)
        count = order_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_order'] = paging['page_index']
        order_set = order_set[paging['start_item']:paging['end_item']]

        data['orders'] = order_set
        data['paging'] = paging
        return render_to_response('bms/order/jdclbx_list.html', data, context)
    
#  2017/09/03添加异步提交表单图片
@login_required
@AdminRequired
def jdclbx_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    pro_area_list = CargoArea.objects(level='1')
    data['pro_area_list'] = pro_area_list
    city_area_list = CargoArea.objects(level='2')
    data['city_area_list'] = city_area_list
    dist_area_list = CargoArea.objects(level='3')
    data['dist_area_list'] = dist_area_list
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    #client_set = Client.objects().filter(user_type__ne='registered')
    #2017修改用户流程
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    count1=client_set.count()
    data['clients'] = client_set
    car_type = InquiryInfo.CAR_TYPE                 #车辆类型
    use_property = InquiryInfo.USE_PROPERTY        #使用性质
    data['car_type_list'] =car_type
    data['use_property_list'] = use_property
    #微信后台联调添加字段
    cargo_area_list = CargoArea.objects()
    data['cargo_area_list'] = cargo_area_list
    message =  ''
    if request.method == 'POST':
        #data['posted_data'] = request.POST
        data1={}
        try:
            jdclbx = InquiryInfo()
            jdclbx = bms_tools.validation_jdclbx(jdclbx)
            jdclbx.save()
            #return render_to_response('bms/order/jdclbx_create.html', data, context)
            data1['jdclbx_id'] =str(jdclbx.id)
            return JsonResult(data=data1, code=CODE_SUCCESS).response()
        except CustomError as e:
            message =  e.message
            return  JsonResult(data=data1, code=CODE_ERROR, message=message).response()
        except ParameterError as e:
            message =  e.message
            return  JsonResult(data=data1, code=CODE_ERROR, message=message).response()
        except Exception as e:
            print(traceback.format_exc())
            message =  e.message
            return  JsonResult(data=data1, code=CODE_ERROR, message=message).response()
    elif request.method == 'GET':
        return render_to_response('bms/order/jdclbx_create.html', data, context)
    
@login_required
@AdminRequired
def jdclbx_create1(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    pro_area_list = CargoArea.objects(level='1')
    data['pro_area_list'] = pro_area_list
    city_area_list = CargoArea.objects(level='2')
    data['city_area_list'] = city_area_list
    dist_area_list = CargoArea.objects(level='3')
    data['dist_area_list'] = dist_area_list
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    #client_set = Client.objects().filter(user_type__ne='registered')
    #2017修改用户流程
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    count1=client_set.count()
    data['clients'] = client_set
    car_type = InquiryInfo.CAR_TYPE                 #车辆类型
    use_property = InquiryInfo.USE_PROPERTY        #使用性质
    data['car_type_list'] =car_type
    data['use_property_list'] = use_property
    #微信后台联调添加字段
    cargo_area_list = CargoArea.objects()
    data['cargo_area_list'] = cargo_area_list
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            jdclbx = InquiryInfo()
            jdclbx = bms_tools.validation_jdclbx(jdclbx)
            jdclbx.save()
            #return render_to_response('bms/order/jdclbx_create.html', data, context)
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx.id, ]))
        except CustomError as e:
            data['message'] =  e.message
            return render_to_response('bms/order/jdclbx_create.html', data, context)
        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('bms/order/jdclbx_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            # request.session['message'] = str(e)
            return render_to_response('bms/order/jdclbx_create.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/order/jdclbx_create.html', data, context)
    
    
@login_required
@AdminRequired
def jdclbx_detail(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    jdclbx_id=jdclbx_id
    message = request.session.get('jdclbx_message', '')
    request.session['jdclbx_message'] = ""
    process_price_state = request.session.get('process_price_state', '')
    data['process_price_state'] = process_price_state
    request.session['process_price_state'] = ""
    if message:
        data['message'] = message
    fail_reason = request.session.get('fail_reason', '')
    request.session['fail_reason'] = ""
    data['fail_reason'] = fail_reason
    #2017添加审核功能
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新",]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    post_data = request.session.get('post_data', '')
    request.session['post_data'] = ''
    data["posted_data"] = post_data
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()
#         a=jdclbx_set.plate_image_left
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    if jdclbx_set:
        data['jdclbx_set'] = jdclbx_set
        print(data)
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    #2017-09-11添加历史记录部分
    jdclbx_history=[]
    try:
        jdclbx_history= JdclbxHistory.objects(order=jdclbx_set).order_by('create_time')
    except:
        pass
    data["jdclbx_history"]=jdclbx_history
    
    #分解车牌号
    data["short"]=""
    data["mid"]=""
    data["end"]=""
    if jdclbx_set.plate_number:
        try:
            a=jdclbx_set.plate_number
            short = jdclbx_set.plate_number[0]
            mid = jdclbx_set.plate_number[2]
            end = jdclbx_set.plate_number[4:]
            data["short_number"]=short
            data["mid_number"]=mid
            data["end_number"]=end
        except:
            pass
    data['intermediary_price_list']=''
    if jdclbx_set.state == 'wait' or jdclbx_set.state == 'done' or jdclbx_set.state == 'paid' or jdclbx_set.state == 'init' :
        try:
            intermediary_price_list=IntermediaryPrice.objects(order=jdclbx_set).order_by('order_price_add_profit')
            #data['intermediary_price_list']=intermediary_price_list
#             company_list=[]
#             intermediary_price_set=[]
#             for intermediary_price in intermediary_price_list:
#                 a=intermediary_price.create_time
#                 b=intermediary_price.company.simple_name
#                 c=intermediary_price.insurance_intermediary.intermediary_name
#                 if intermediary_price.company not in company_list:
#                     company_list.append(intermediary_price.company)
#                     intermediary_price_set.append(intermediary_price)
        except:
            intermediary_price_list =[]
#             intermediary_price_set=[]
        data['intermediary_price_list']=intermediary_price_list  
    #2017/1/11添加手续费回显功能
    intermediary_rate_list=[]
    try:
         intermediary_rate_list=IntermediaryRate.objects(jdclbx_order = jdclbx_set)
         count=intermediary_rate_list.count()
    except:
        intermediary_rate_list=[]     
    data['intermediary_rate_list']=intermediary_rate_list
    #添加特别约定回显
    if jdclbx_set.special_agreement:
        if len(jdclbx_set.special_agreement)>40:
            data['special_agreement'] = jdclbx_set.special_agreement[0:39]+'……'
        else:
            data['special_agreement'] = jdclbx_set.special_agreement
#     #审核
#     rate_state='hide'
#     data['rate_state'] = rate_state
#     try:
#         verify_answer  = jdclbx_set.verify()
#         rate_state='unhide'
#         data['rate_state'] = rate_state
#     except Exception as e:
#         pass
    return render_to_response('bms/order/jdclbx_detail_new.html', data, context)  

@login_required
@AdminRequired
def jdclbx_edit(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    #页面回显
    pro_area_list = CargoArea.objects(level='1')
    data['pro_area_list'] = pro_area_list
    city_area_list = CargoArea.objects(level='2')
    data['city_area_list'] = city_area_list
    jdclbx_set = InquiryInfo.objects(id=jdclbx_id).first()
    data['jdclbx_set'] = jdclbx_set
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    #client_set = Client.objects().filter(user_type__ne='registered')
    #2017修改用户流程
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    count1=client_set.count()
    data['clients'] = client_set
    car_type = InquiryInfo.CAR_TYPE                 #车辆类型
    use_property = InquiryInfo.USE_PROPERTY        #使用性质
    data['car_type_list'] =car_type
    data['use_property_list'] = use_property
    #微信后台联调添加字段
    dist_area_list = CargoArea.objects(level='3')
    data['dist_area_list'] = dist_area_list
    message=""
    #2017 分解保单地址省市区联动
    data["mail_prov_set"]=""
    data["mail_city_set"] =''
    data["mail_dist"]=""
    try:
        mail_address = jdclbx_set.mail_address
        mail_address_list =mail_address.split(' ')
        mail_prov=mail_address_list[0]
        mail_prov_set = CargoArea.objects(level='1',name=mail_prov).first()
        data["mail_prov_set"]=mail_prov_set
#         mail_prov_number = mail_prov_set.code
        mail_city =mail_address_list[1]
        mail_city_set = CargoArea.objects(level='2',name=mail_city).first()
        data["mail_city_set"] =mail_city_set
       # mail_city_number = mail_city_set.code
        mail_dist =mail_address_list[2]
        data["mail_dist"]= mail_dist
    except:
        pass
    
    #分解车牌号
    data["short"]=""
    data["mid"]=""
    data["end"]=""
    if jdclbx_set.plate_number:
        try:
            a=jdclbx_set.plate_number
            short = jdclbx_set.plate_number[0]
            mid = jdclbx_set.plate_number[2]
            end = jdclbx_set.plate_number[4:]
            data["short_number"]=short
            data["mid_number"]=mid
            data["end_number"]=end
        except:
            pass
        
    #2017-0913给订单赋初值
    if jdclbx_set.state == 'paid' or jdclbx_set.state == 'done':
        try:
            count_history=JdclbxHistory.objects(order=jdclbx_set).count()
            if count_history == 0:
                jdclbx_history = JdclbxHistory()
                detail_list = jdclbx_history.ORDER_DETAIL
                jdclbx_history.order = jdclbx_set
                for field, name in detail_list:
                    setattr(jdclbx_history, field, getattr(jdclbx_set, field))
                jdclbx_history.create_time=jdclbx_set.pay_time
                jdclbx_history.save()
        except:
            pass
    
    if request.method == 'POST':
        try:
            if jdclbx_set.state == 'paid' or jdclbx_set.state == 'done':
                jdclbx = jdclbx_set
                jdclbx = bms_tools.validation_jdclbx_detail(jdclbx)
                jdclbx.save()
            else:
                jdclbx = jdclbx_set
                jdclbx = bms_tools.validation_jdclbx(jdclbx)
                jdclbx.save()
                jdclbx.state='verify'
                jdclbx.save()
                jdclbx.fail_reason=''
                jdclbx.save()
        except CustomError as e:
            data['message'] =  e.message
            return render_to_response('bms/order/jdclbx_edit.html', data, context)
        except ParameterError as e:
            data['message'] = e.message
            return render_to_response('bms/order/jdclbx_edit.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/order/jdclbx_edit.html', data, context)
        
        #添加支付订单可修改部分
        if jdclbx.state != 'paid' and jdclbx.state != 'done':
            #删除中介报价内容
            try:
                intermediary_price_list=IntermediaryPrice.objects(order=jdclbx_set)
                if intermediary_price_list:
                    for intermediary_price_detail in intermediary_price_list:
                        intermediary_price_detail.delete()
            except Exception as e:
                data['message'] = str(e)+"删除报价信息失败"
                return render_to_response('bms/order/jdclbx_edit.html', data, context)
            #删除添加中介手续费内容
            try:
                intermediary_rate_list=IntermediaryRate.objects(jdclbx_order=jdclbx_set)
                if intermediary_rate_list:
                    for intermediary_rate_detail in intermediary_rate_list:
                        intermediary_rate_detail.delete()
            except Exception as e:
                data['message'] = str(e)+"删除手续费失败"
                return render_to_response('bms/order/jdclbx_edit.html', data, context)
        
        #2017-09-11 添加数据记录部分
        if jdclbx.state == 'paid' or jdclbx.state == 'done':
            try:
                jdclbx_history = JdclbxHistory()
                detail_list = jdclbx_history.ORDER_DETAIL
                jdclbx_history.order = jdclbx
                for field, name in detail_list:
                    setattr(jdclbx_history, field, getattr(jdclbx, field))
                jdclbx_history.save()
            except Exception as e :
                request.session['jdclbx_message'] = '保存历史记录失败'+str(e)
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        #2017-09-11 添加数据记录部分结束
        
        request.session['jdclbx_message'] = "编辑成功"
        return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx.id, ]))
    elif request.method == 'GET':
        return render_to_response('bms/order/jdclbx_edit.html', data, context)  


#   验证机动车保险订单
def validation_jdclbx_plate(request, jdclbx_order):
    
    short_number = request.POST.get('short_number')      #车牌号第一位
    mid_number = request.POST.get('mid_number')    #车牌号第二位
    plate_number = request.POST.get('plate_number')    #车牌号后五位
    car_type = request.POST.get('car_type')    #车辆类型
    holder = request.POST.get('holder')    #所有人
    use_property = request.POST.get('use_property')    #车使用性质
    brand_digging = request.POST.get('brand_digging')    #品牌型号
    car_number = request.POST.get('car_number')    #车辆识别代码
    engine_number = request.POST.get('engine_number')    #发动机号
    issue_date = request.POST.get('issue_date')    #注册日期
    people_number = request.POST.get('people_number')    #核载人数(位)
    load_weight = request.POST.get('load_weight')    #核载质量(Kg)
    
    #所有人
    if holder:
        jdclbx_order.holder = holder
    else:
        raise ParameterError('请输入所有人')
    #车牌号
    if short_number and mid_number and plate_number:
        if re.match(r'^[a-z_A-Z_0-9]{5}$', plate_number):
            plate_number = plate_number.upper()
            jdclbx_order.plate_number = short_number +' ' + mid_number +' ' + plate_number
        else:
            raise ParameterError('您输入的车牌号不正确，请输入英文或数字')
    else:
        raise ParameterError('请输入车牌号')
    
    
    #2017添加验证部分
    #根据车牌号和订单货物大类筛选适合本订单的保险中介渠道
    message=''
    order_car_type = jdclbx_order.order_car_type
    if order_car_type == 'passenger_car':
            order_car_type_name ='九座以下客车'
    elif order_car_type == 'truck':  
        order_car_type_name ='货车'
    else:
        order_car_type_name = order_car_type
    intermediary_list = Intermediary.objects.filter(state = True, order_car_type__icontains=order_car_type, plate_number_list__icontains=short_number )
    test_count =intermediary_list.count()
    if test_count == 0:
        message = "暂未开通"+str(order_car_type_name) + '车牌号为' + str(short_number)+ '部分投保业务'
        raise ParameterError(message)
    else:
        intermediary_list_test=[]
        user_set = User.objects(is_active=True)
        #transport_set = transport_set.filter(user__in=user_set)
        for intermediary_detail in intermediary_list:
            try:
                intermediary_people_count = IntermediaryPeople.objects(intermediary =intermediary_detail , user__in=user_set ).count()
                if intermediary_people_count>0:
                    intermediary_list_test.append(intermediary_detail)
            except:
                pass
        if len(intermediary_list_test)>0:
            jdclbx_order.intermediary_list = intermediary_list_test
        else:
            message = "暂未开通"+str(order_car_type_name) + '车牌号为' + str(short_number)+ '部分投保业务。'
            raise ParameterError(message)
    
    
    
    #使用性质
    if use_property:
        jdclbx_order.use_property = use_property
    else:
        raise ParameterError('请选择使用性质')
    #车辆类型
    if car_type:
        jdclbx_order.car_type = car_type
    else:
        raise ParameterError('请选择车辆类型')
    #注册日期
    if issue_date:
        now = datetime.now()
        otherStyleTime = now.strftime("%Y-%m-%d ")
        if issue_date > otherStyleTime:
            raise ParameterError('注册日期不能晚于当前时间')
        jdclbx_order.issue_date = issue_date
    else:
        raise ParameterError('请输入车辆注册日期')
    #品牌型号
    if brand_digging:
        jdclbx_order.brand_digging = brand_digging
    else:
        raise ParameterError('请输入品牌型号')
    #车辆识别代码
    if car_number:
#         jdclbx_order.car_number = car_number
        car_number = car_number.replace(' ', '')
        test_answer=checkVIN(car_number)
        if test_answer == 'success':
            jdclbx_order.car_number = car_number
        else:
            raise ParameterError(test_answer)
    else:
        raise ParameterError('请输入车辆识别代码')
    #发动机号
    if engine_number:
        jdclbx_order.engine_number = engine_number
    else:
        raise ParameterError('请输入发动机号')
    #核载人数(位)
    if people_number:
        jdclbx_order.people_number = people_number
    #核载质量(Kg)
    if load_weight:
        jdclbx_order.load_weight = load_weight
    if not people_number  and not load_weight:
        raise ParameterError('请输入核载人数或核载质量')
    return jdclbx_order

#审核信息
@login_required
@AdminRequired
def jdclbx_verify(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    jdclbx_id=jdclbx_id
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    if jdclbx_set:
        data['jdclbx_set'] = jdclbx_set
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    #2017添加审核信息
    if request.method == 'POST':
        request_tool.save_log()
        request.session['post_data'] = request.POST
        certificate_type = request.POST.get('certificate', '')
        if certificate_type == 'plate':
            try:
                jdclbx_set=validation_jdclbx_plate(request,jdclbx_set )
                jdclbx_set.save()
                request.session['message'] = "行驶证信息补充完成"
            except CustomError as e:
                request.session['message'] =  e.message
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            except ParameterError as e:
                request.session['message'] = e.message
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            except Exception as e:
                request.session['message'] =str(e)
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            
        elif certificate_type =='id_card':
            applicant_name = request.POST.get('applicant_name', '')
            certificate_number = request.POST.get('certificate_number', '')
            #投保人姓名
            if applicant_name:
                jdclbx_set.applicant_name = applicant_name
            else:
                request.session['message'] ='请输入投保人姓名'
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            #身份证号
            if certificate_number:
                test_idcard_number=checkIdcard(certificate_number)
                if test_idcard_number=='success':
                    jdclbx_set.certificate_number = certificate_number
                else:
                    request.session['message'] =test_idcard_number
                    return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
                
            else:
                request.session['message'] ='请输入投保人身份证号'
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            try:
                jdclbx_set.save()
                request.session['message'] = "身份证信息补充完成"
                if jdclbx_set.insured_name == '同投保人姓名':
                    jdclbx_set.insured_name = jdclbx_set.applicant_name
                    jdclbx_set.insured_number = jdclbx_set.certificate_number
                    jdclbx_set.save()
            except Exception as e:
                request.session['message'] =str(e)
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
                
        elif certificate_type == 'business_license':
            applicant_company_name = request.POST.get('applicant_company_name', '')
            organ_number = request.POST.get('organ_number', '')
            if applicant_company_name:
                jdclbx_set.applicant_company_name = applicant_company_name
            else:
                request.session['message'] ='请输入单位名称'
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            if organ_number:
                jdclbx_set.organ = organ_number
            else:
                request.session['message'] ='请输入组织机构代码或营业执照号'
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            try:
                jdclbx_set.save()
                request.session['message'] = "营业执照信息补充完成"
                if jdclbx_set.insured_name == '同投保人姓名':
                    jdclbx_set.insured_name = jdclbx_set.applicant_company_name
                    jdclbx_set.insured_number = jdclbx_set.organ
                    jdclbx_set.save()
            except Exception as e:
                request.session['message'] =str(e)
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        #验证被保人信息
        elif certificate_type == 'bbr':
            bbr_name = request.POST.get('bbr_name', '')
            bbr_number = request.POST.get('bbr_number', '')
            if not bbr_name or not bbr_number:
                request.session['message'] ='被保人姓名和证件号为必填项'
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            jdclbx_set.insured_name = bbr_name
            if jdclbx_set.insured_classify == 'personal':
                try:
                    test_idcard_number1=checkIdcard(bbr_number)
                except:
                    request.session['message'] ='被保人证件号填写错误'
                    return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
                if test_idcard_number1 == 'success':
                    jdclbx_set.insured_number = bbr_number
                else:
                    request.session['message'] ='补充被保人信息出错：'+str(test_idcard_number1)
                    return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            else:
                jdclbx_set.insured_number = bbr_number
            try:
                jdclbx_set.save()
                request.session['message'] = "被保人信息补充完成"
            except Exception as e:
                request.session['message'] =str(e)
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
                    
        else:
            pass
        #自动处理微信段信息填写
        a=jdclbx_set.applicant_name 
        b=jdclbx_set.applicant_company_name 
        if jdclbx_set.user_classify == 'personal':
            if jdclbx_set.applicant_name == '同行驶证':
                if jdclbx_set.holder:
                    jdclbx_set.applicant_name =jdclbx_set.holder
                    try:
                        jdclbx_set.save()
                    except:
                        request.session['message'] ='保存订单投保人时信息出错'
                        return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))

        elif jdclbx_set.user_classify == 'unit':
            if jdclbx_set.applicant_company_name == '同行驶证':
                if jdclbx_set.holder:
                    jdclbx_set.applicant_company_name =jdclbx_set.holder
                    try:
                        jdclbx_set.save()
                    except:
                        request.session['message'] ='保存订单投保人时信息出错'
                        return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        else:
            request.session['message'] ='未获取本订单投保人身份，请检查订单投保人状态'
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        
        return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
    else:
        return render_to_response('bms/order/jdclbx_detail.html', data, context)  
    

#确认投保，报价结束选择投保公司
@login_required
@AdminRequired
def jdclbx_choose_company(request, intermediary_price_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    intermediary_price_id=intermediary_price_id
    #报价信息
    try:
        intermediary_price_set = IntermediaryPrice.objects(id = intermediary_price_id).first()
#         return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[1, ]))
    except:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[1, ]))

    if intermediary_price_set:
        jdclbx=intermediary_price_set.order
        #order_id = jdclbx_set.id
        #信息共享
        try:
            jdclbx.company=intermediary_price_set.company#投保公司
            jdclbx.insurance_intermediary=intermediary_price_set.insurance_intermediary#投保中介
            jdclbx.price=intermediary_price_set.order_price_add_profit#用户应缴纳保费
            jdclbx.intermediary_price=intermediary_price_set.order_price_no_process#应付给中介人员保费
            jdclbx.save()
            jdclbx.state='init'
            jdclbx.save()
        except Exception as e:
            request.session['message'] = str(e)
#             
#         jdclbx.state='init'
#         jdclbx.save()
     
    request.session['jdclbx_message'] = "投保成功"
    return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx.id, ])) 



#付款
@login_required
@AdminRequired
def jdclbx_pay(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    if not jdclbx_set:
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    
    if request.method == 'POST':
#         if jdclbx_set.client.balance < jdclbx_set.price:
#             request.session['jdclbx_message'] = '用户余额不足，请先充值。'
#             return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        try:
            jdclbx_set.pay_money()
            jdclbx_set.save()
            request.session['jdclbx_message'] = "付款成功"
#             return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        except CustomError as e:
            request.session['jdclbx_message'] = e.message
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        except ValueError as e:
            request.session['jdclbx_message'] = e.message
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        except Exception as e:
            request.session['jdclbx_message'] = e.message
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
#         #2017 添加支付统计
#         try:
#             if PaymentStatistical.objects(jdclbx_order=jdclbx_set).count()==0:
#                 payment_statistical = PaymentStatistical()
#             else:
#                 payment_statistical = PaymentStatistical.objects(jdclbx_order=jdclbx_set).first()
#             payment_statistical.client = jdclbx_set.client
#             payment_statistical.price = jdclbx_set.pay_price
#             payment_statistical.jdclbx_order = jdclbx_set
#             payment_statistical.order_type = 'jdclbx'
#             payment_statistical.state = 'xx_price'
#             payment_statistical.save()
#         except Exception as e :
#             request.session['jdclbx_message'] = '保存付款记录失败'+str(e)
#         #付款发送短信
#         try:
#             intermediary_people_list = IntermediaryPeople.objects(intermediary = jdclbx_set.insurance_intermediary)
#             if not intermediary_people_list:
#                 request.session['price_message'] = '未查到投保中介下人员信息：'+str(e)
#                 return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
#         except Exception as e:
#             request.session['price_message'] = '网络不稳定，查找当前中介下所有中介人员微信信息发送失败：'+str(e)
#             return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
#         try:
#             site_settings = SiteSettings.get_settings()
#             helper = m5c_sms_helper.SmsHelper(site_settings.meilian_username, site_settings.meilian_password, site_settings.meilian_api_key)
#             content = "{0}保费已经缴纳，请根据报价内容出具保单后，上传保单影像材料".format(jdclbx_set.plate_number)
#             for intermediary_people in intermediary_people_list:
#                 if intermediary_people.user.is_active:
#                     phone_num = intermediary_people.profile.phone
#                     helper.send_sms(phone_to=phone_num, content=content)
#         except Exception as e:
#             request.session['jdclbx_message'] = '短信发送失败'+str(e)
#             return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
#         request.session['jdclbx_message'] = "付款成功，且已发短信通知中介人员上传保单信息"
        #2017-09-11 添加数据记录部分
        try:
            jdclbx_history = JdclbxHistory()
            detail_list = jdclbx_history.ORDER_DETAIL
            jdclbx_history.order = jdclbx_set
            for field, name in detail_list:
                setattr(jdclbx_history, field, getattr(jdclbx_set, field))
            jdclbx_history.save()
        except Exception as e :
            request.session['jdclbx_message'] = '保存历史记录失败'+str(e)
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        #2017-09-11 添加数据记录部分结束
        return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
    elif request.method == 'GET':
        return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))




#验证添加的手续费比例（2017修改版）

def verify_jdclbx_process(request, jdclbx,intermediary ):
    intermediary=intermediary
    jdclbx =jdclbx
    company_process_state='0'
    for company in intermediary.intermediary_company_list:
        choose_state = 'choose_state_'+str(company.id)
        choose_state1 = request.POST.get(choose_state)    #是否可承保
        if choose_state1 !='1':
            company_process_state ='1'
            break
#     if company_process_state=='0':
#         message='保存手续费失败：'+str(intermediary.intermediary_name)+'该中介至少应有一家保险公司承保本单。'
#         raise ParameterError(message)
    for company in intermediary.intermediary_company_list:
        count=0
        try:
            count = IntermediaryRate.objects( intermediary=intermediary , company=company , jdclbx_order=jdclbx).count()
        except:
            count=0
        if count >0:
            intermediary_rate =IntermediaryRate.objects( intermediary = intermediary , company = company , jdclbx_order = jdclbx).first()
        else:
            intermediary_rate = IntermediaryRate()
        liability_name = 'liability_process_price_'+str(company.id)
        commercial_name = 'commercial_process_price_'+str(company.id)
        choose_state = 'choose_state_'+str(company.id)
        liability_process_price = request.POST.get(liability_name)    #交强险手续费
        commercial_process_price = request.POST.get(commercial_name)    #商业险手续费
        choose_state1 = request.POST.get(choose_state)    #是否可承保
        intermediary_rate.intermediary = intermediary
        intermediary_rate.jdclbx_order = jdclbx
        intermediary_rate.company = company
        if choose_state1=='1':
            #本公司不承保
            intermediary_rate.liability_process_price = 0.0
            intermediary_rate.commercial_process_price = 0.0
            intermediary_rate.company_state = False
            if company_process_state=='0':
                intermediary_rate.intermediary_state = False
            else:
                intermediary_rate.intermediary_state = True
            try:
                intermediary_rate.save()
            except Exception as e:
                 raise ParameterError(str(e))
        else:
            intermediary_rate.company_state = True
            intermediary_rate.intermediary_state = True
            #交强险验证
            try:
                liability_process_price1 = float(liability_process_price)
            except:
                message=str(intermediary.intermediary_name)+"--"+str(company.simple_name)+"--交强险手续费比例请填写数字。"
                raise ParameterError( message )
            if float(liability_process_price)<0 or float(liability_process_price)*100>int(float(liability_process_price)*100):
                message=str(intermediary.intermediary_name)+"--"+str(company.simple_name)+"--交强险手续费比例请填写大于零最多有两位小数的数字。"
                raise ParameterError( message )
            else:
                intermediary_rate.liability_process_price = float(liability_process_price)
            #商业险手续费验证
            try:
                commercial_process_price1 = float(commercial_process_price)
            except:
                message=str(intermediary.intermediary_name)+"--"+str(company.simple_name)+"--商业险手续费比例请填写数字。"
                raise ParameterError( message )
            if float(commercial_process_price)<0 or float(commercial_process_price)*100>int(float(commercial_process_price)*100):
                message=str(intermediary.intermediary_name)+"--"+str(company.simple_name)+"商业险手续费比例请填写大于零最多有两位小数的数字。" 
                raise ParameterError( message )
            else:
                intermediary_rate.commercial_process_price = float(commercial_process_price)
            try:
                intermediary_rate.save()
            except Exception as e:
                 raise ParameterError(str(e))
        
#     return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))




#添加手续费比例（2017修改版）
@login_required
@AdminRequired
def add_jdclbx_process(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    request.session['process_price_state'] = "open"
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    if not jdclbx_set:
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        jdcbx_intermediary_id = request_tool.get_parameter("jdcbx_intermediary_id")
        try:
            intermediary_set= Intermediary.objects(id=jdcbx_intermediary_id).first()
        except:
            request.session['message'] = '未找到对应中介信息数据。'
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        try:
            verify_jdclbx_process(request, jdclbx_set,intermediary_set )
        except CustomError as e:
            request.session['jdclbx_message'] = e.message
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        except ValueError as e:
            request.session['jdclbx_message'] = e.message
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        except Exception as e:
            request.session['jdclbx_message'] = e.message
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
       
    elif request.method == 'GET':
        return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))


#验证添加手续费比例-完成（2017修改版）
@login_required
@AdminRequired
def verify_process_state(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    request_tool = RequestTools(request)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    if not jdclbx_set:
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    
    jdcbx_intermediary_list = jdclbx_set.intermediary_list
    answer = 'finished'
    message=''
    for jdcbx_intermediary in jdcbx_intermediary_list:
        for company in jdcbx_intermediary.intermediary_company_list:
            try:
                intermediary_rate_detail =  IntermediaryRate.objects(jdclbx_order = jdclbx_set , intermediary = jdcbx_intermediary ,company=company).first()
                if not intermediary_rate_detail:
                    answer = 'unfinished'
                    message=str(company.simple_name)+'未填写手续费信息，如果本公司不保请勾选不保按钮'
                    break
#             except Exception as e:
#                 request.session['jdclbx_message'] = str(e)
#                 return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            except:
                answer = 'unfinished'
                message=str(company.simple_name)+'--未填写手续费信息，如果本公司不保请勾选不保按钮'
                break
        if answer == 'unfinished':
            message=str(jdcbx_intermediary.intermediary_name)+"--"+message
            break
    if answer == 'unfinished':
          request.session['jdclbx_message'] = message
    elif answer == 'finished':
        jdclbx_set.state='price'
        jdclbx_set.save()
        request.session['jdclbx_message'] = '手续费保存完成，等待中介人员报价'
        test_kb_intermediary = '0'
        jdcbx_intermediary_list = jdclbx_set.intermediary_list
        for jdcbx_intermediary in jdcbx_intermediary_list:
            for company in jdcbx_intermediary.intermediary_company_list:
                intermediary_rate_detail =  IntermediaryRate.objects(jdclbx_order = jdclbx_set , intermediary = jdcbx_intermediary ,company=company).first()
                intermediary_rate_detail.state = False#手续费不可修改
                intermediary_rate_detail.save()
                if intermediary_rate_detail.intermediary_state == True:
                    test_kb_intermediary = '1'
        #2017添加验证本单是否自动驳回
        if test_kb_intermediary ==  '0':
            jdclbx_set.state = 'fail'
            jdclbx_set.fail_reason = '本单没有中介可承保'
            request.session['jdclbx_message'] = '本单没有中介可承保,请及时联系用户，本单已驳回'
            try:
                jdclbx_set.save()
            except:
                request.session['jdclbx_message'] = '本单没有中介可承保,网络延迟订单状态未改变'
        ##########################
        
        #2017中介不可保删除对应手续费信息
        jdcbx_intermediary_list = jdclbx_set.intermediary_list
        for jdcbx_intermediary in jdcbx_intermediary_list:
            intermediary_rate_detail =  IntermediaryRate.objects(jdclbx_order = jdclbx_set , intermediary = jdcbx_intermediary).first()
            if intermediary_rate_detail.intermediary_state == False:
                intermediary_rate_list1 =  IntermediaryRate.objects(jdclbx_order = jdclbx_set , intermediary = jdcbx_intermediary )
                for intermediary_rate_detail1 in intermediary_rate_list1:
                    intermediary_rate_detail1.delete()
                #去除保险公司可看权限
                try:
                   # insurance_product.documents.remove(insurance_document)
                    jdclbx_set.intermediary_list.remove(jdcbx_intermediary)
                    jdclbx_set.save()
                except:
                    request.session['jdclbx_message'] = '去除不可保中介信息失败'
        
        ########################
        ##########20170821添加给中介发信息
        if jdclbx_set.state=='price':
            #付款发送短信
            message_intermediary=''
            message_intermediary_people=''
            jdcbx_intermediary_list = jdclbx_set.intermediary_list
            if jdcbx_intermediary_list:
                for jdcbx_intermediary in jdcbx_intermediary_list:
                    try:
                        intermediary_people_list = IntermediaryPeople.objects(intermediary = jdcbx_intermediary)
                        if not intermediary_people_list:
                            message_intermediary=message_intermediary+'-' + jdcbx_intermediary.intermediary_name
                    except Exception as e:
                        print(e)
                        message_intermediary=message_intermediary+'-' + jdcbx_intermediary.intermediary_name

                    try:
                        site_settings = SiteSettings.get_settings()
                        helper = m5c_sms_helper.SmsHelper(site_settings.meilian_username, site_settings.meilian_password, site_settings.meilian_api_key)
                        content = "订单号为{0}，车牌号为{1}的订单已审核，请根据订单内容上传报价信息".format(jdclbx_set.paper_id,jdclbx_set.plate_number)
                        for intermediary_people in intermediary_people_list:
                            if intermediary_people.user.is_active:
                                phone_num = str(intermediary_people.profile.phone)
                                helper.send_sms(phone_to=phone_num, content=content)
                    except Exception as e:
                        message_intermediary_people=message_intermediary_people+'手机号为'+phone_num+'，'
                    print(3)
            if len(message_intermediary)>1 or len(message_intermediary_people)>1:
                request.session['jdclbx_message'] = '中介渠道：'+message_intermediary+ '没有找到对应中介人员。'+message_intermediary_people+'的中介人员发送短信失败'
        ############结束
    else:
        request.session['jdclbx_message'] = '网络延迟，请稍后再试'
    
    return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))



#删除订单
@login_required
@AdminRequired
def jdclbx_delete(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()
        data['jdclbx_set'] = jdclbx_set
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    if not jdclbx_set:
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    
    if request.method == 'POST':
        #删除中介报价内容
        try:
            intermediary_price_list=IntermediaryPrice.objects(order=jdclbx_set)
            if intermediary_price_list:
                for intermediary_price_detail in intermediary_price_list:
                    intermediary_price_detail.delete()
        except Exception as e:
            data['message'] = str(e)+"删除报价信息失败"
            return render_to_response('bms/order/jdclbx_detail.html', data, context)
        #删除添加中介手续费内容
        try:
            intermediary_rate_list=IntermediaryRate.objects(jdclbx_order=jdclbx_set)
            if intermediary_rate_list:
                for intermediary_rate_detail in intermediary_rate_list:
                    intermediary_rate_detail.delete()
        except Exception as e:
            data['message'] = str(e)+"删除手续费失败"
            return render_to_response('bms/order/jdclbx_detail.html', data, context)
#         if jdclbx_set.client.balance < jdclbx_set.price:
#             request.session['jdclbx_message'] = '用户余额不足，请先充值。'
#             return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        try:
#             jdclbx_set.pay_money()
            jdclbx_set.delete()
            request.session['jdclbx_message'] = "删除成功"
            return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[1, ]))
        except CustomError as e:
            request.session['jdclbx_message'] = e.message
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        except ValueError as e:
            request.session['jdclbx_message'] = e.message
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        except Exception as e:
            request.session['jdclbx_message'] = e.message
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
    elif request.method == 'GET':
        return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))


#驳回订单
@login_required
@AdminRequired
def jdclbx_fail(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    if not jdclbx_set:
        return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ]))
    
    if request.method == 'POST':
        try:
            fail_reason = request.POST.get('fail_reason')    #驳回原因
            request.session['fail_reason'] = fail_reason
            if not fail_reason :
                request.session['jdclbx_message'] = '请输入驳回原因'
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            if len(fail_reason)>100:
                request.session['jdclbx_message'] = '请简短描述驳回原因。驳回原因最多100个字符'
                return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
            jdclbx_set.fail_reason=fail_reason
            jdclbx_set.state = 'fail'
            jdclbx_set.save()
            jdclbx_set.intermediary_list = []
            jdclbx_set.save()
#             return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        except Exception as e:
            data['message'] = str(e)
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        #删除中介报价内容
        try:
            intermediary_price_list=IntermediaryPrice.objects(order=jdclbx_set)
            if intermediary_price_list:
                for intermediary_price_detail in intermediary_price_list:
                    intermediary_price_detail.delete()
        except Exception as e:
            request.session['jdclbx_message'] = str(e)+"删除报价信息失败"
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        #删除添加中介手续费内容
        try:
            intermediary_rate_list=IntermediaryRate.objects(jdclbx_order=jdclbx_set)
            if intermediary_rate_list:
                for intermediary_rate_detail in intermediary_rate_list:
                    intermediary_rate_detail.delete()
        except Exception as e:
            request.session['jdclbx_message'] = str(e)+"删除手续费失败"
            return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        
        return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))
        

    elif request.method == 'GET':
        return HttpResponseRedirect(reverse('bms:jdclbx_detail', args=[jdclbx_id, ]))


#2017/08/28导出保单
@login_required
@AdminRequired
def jdclbx_export(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.save_log()
    pay_state = request_tool.get_parameter("pay_state")
    id_client = request_tool.get_parameter("client_sign")
    search_keyword = request.POST.get('search_keyword', '')
    get_parameter = "?pay_state={0}&search_keyword={1}&id_client={2}".format(pay_state, search_keyword, id_client)
    try:
        order_set = InquiryInfo.objects()
        order_set = request_tool.jdcbx_filter(order_set=order_set)
        if order_set:
            export_tools = ExcelExportTools()
            file_url = export_tools.export1(order_set, InquiryInfo.INSURANCE_FIELD_TUPLE)
            print(file_url)
            url = static('/static/'+file_url)
            # request_tool.set_message('导出成功')
            return HttpResponseRedirect(url)
        else:
            request_tool.set_message('没有找到要导入的订单')
            return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[1, ]) + get_parameter)
    except CustomError as e:
        request_tool.set_message(e.message)
    except Exception as e:
        print(traceback.format_exc())
        request_tool.set_message(str(e))
    return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[1, ]) + get_parameter)

