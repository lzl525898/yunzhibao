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
from common.tools_legoo import *
from common.tools import *
from common.tools import RequestTools
from bms.tools import DocumentBmsTools
from django.shortcuts import render_to_response, HttpResponse
import traceback

from wss.views_sendmessage import  send_wx_message
from common import tools_string
import os

from datetime import timedelta
# import datetime
from common.driver_dict import *
#－－－－－－－－－－－－－－－－－－－－－－－－－－     车辆统计      －－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def car_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_car'] = search_keyword
        request.session['page_index_car'] = 1
        return HttpResponseRedirect(reverse('bms:car_list', args=[1, ]))

    elif request.method == 'GET':
        
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_car', '')
        car_list = CarCertificate.objects()
        if search_keyword=='待审核':
            car_list = request_tool.car_filter(car_set=car_list, keyword='init')
        elif search_keyword == '已认证':
            car_list = request_tool.car_filter(car_set=car_list, keyword='success')
        else:
            car_list = request_tool.car_filter(car_set=car_list, keyword=search_keyword)
        count = car_list.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_car'] = paging['page_index']
        car_list = car_list[paging['start_item']:paging['end_item']]
        data['car_lists'] = car_list
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        request.session['search_keyword_car'] = ''
        return render_to_response('bms/car/car_list.html', data, context)
 

#申请认证
@login_required
@AdminRequired
def car_create(request):
    context = RequestContext(request)
    data = {}
    #2017修改用户流程
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    count1=client_set.count()
    #client_set = Client.objects().filter(user_type__ne='registered')
    data['clients'] = client_set
    page_index = request.session.get('page_index_car_list', '1')
    data['page_index'] = page_index
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新","港","澳","台"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            create_car = CarCertificate()
            create_car = bms_tools.validation_create_car(create_car)
            create_car.save()
            request.session['message'] = '申请成功，请认证。'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/car/car_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/car/car_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:car_detail', args=[create_car.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/car/car_create.html', data, context)
 

@login_required
@AdminRequired
def car_detail(request, car_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_car_id', '1')
    data['page_index'] = page_index
    car = CarCertificate.objects(id=car_id).first()
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新","港","澳","台"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    if car:
        total=car.liability_tax+car.liability_price+car.commercial_price
        net_value = total-car.oil_card_price
        data['car'] = car
        data['total'] = total
        data['net_value'] = net_value
        #分解车牌号
        data["short"]=""
        data["mid"]=""
        data["end"]=""
        if car.plate_number:
            try:
                a=car.plate_number
                short = car.plate_number[0]
                mid = car.plate_number[1]
                end = car.plate_number[3:]
                data["short_number"]=short
                data["mid_number"]=mid
                data["end_number"]=end
            except:
                pass
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:car_list', args=[page_index, ]))
    return render_to_response('bms/car/car_detail.html', data, context)  
    
#认证行驶证
def plate_certificate(request,car):  
    now = datetime.now()
    otherStyleTime = now.strftime("%Y-%m-%d ")
    plate_number              = request.POST.get('plate_number', '')        # 车牌号
    car_type              = request.POST.get('car_type', '')                #车辆类型
    holder                  = request.POST.get('holder', '')#所有人
    use_property                 = request.POST.get('use_property', '')#使用性质
    brand_digging       = request.POST.get('brand_digging', '')#品牌型号
    car_number                = request.POST.get('car_number', '')#车辆识别代码
    engine_number                = request.POST.get('engine_number', '')#发动机号
    issue_date                = request.POST.get('issue_date', '')#注册日期
    people_number                    = request.POST.get('people_number', '')#核载人数
    load_weight                    = request.POST.get('load_weight', '')#核载人数
    
    short = request.POST.get('short_number', '')        # 车牌号
    mid = request.POST.get('mid_number', '')        # 车牌号
    if plate_number:
        if not short or not mid:
            raise ParameterError('请选择车牌号前两位。如“黑A')
        if re.match(r'^[a-z_A-Z_0-9]{5}$', plate_number):
             plate_number = plate_number.upper()
             plate_number1 = short +mid +" "+plate_number
             car.plate_number=plate_number1
        else:
            raise ParameterError('您输入的车牌号不正确，请输入由英文或数字组成的五位字符串')
    else:
        raise ParameterError('车牌号不能为空')
#     if plate_number:
#         plate_number = plate_number.upper()
#         car.plate_number=plate_number
#     else:
#         raise ParameterError('未输入车牌号')
    if car_type:
        car.car_type=car_type
    else:
        raise ParameterError('认证车辆类型错误')
    if holder:
        car.holder=holder
    else:
        raise ParameterError('未输入车辆所有人')
    if use_property:
        car.use_property=use_property
    else:
        raise ParameterError('未输入使用性质')
    if brand_digging:
        car.brand_digging=brand_digging
    else:
        raise ParameterError('未输入品牌型号')
    if car_number:
        car.car_number=car_number
    else:
        raise ParameterError('未输入车辆识别代码')
    if engine_number:
        car.engine_number=engine_number
    else:
        raise ParameterError('未输入发动机号')
    if issue_date:
        if issue_date>otherStyleTime:
            raise ParameterError('注册日期不能大于当前日期')
        else:
            a=issue_date+" 00:00:00"
            issue_date= datetime.strptime(a,"%Y-%m-%d %H:%M:%S")
#             issue_date= d = datetime.datetime.strptime(issue_date,"%Y-%m-%d %H:%M:%S")
            #issue_date=issue_date+"00:00:00"
            car.issue_date=issue_date
    else:
        raise ParameterError('未输入注册日期')
    
    if people_number:
        car.people_number=people_number
#     else:
#         raise ParameterError('未输入核载人数')
    if load_weight:
        car.load_weight=load_weight
    if  people_number=="" and load_weight=="":
        raise ParameterError('“核载人数”或“核载质量”不能同时为空')
#     else:
#         raise ParameterError('未输入核载质量')

    return car
    
    
    
#认证交强险 
def liability_certificate(request,car):
    now =  datetime.now()
    otherStyleTime = now.strftime("%Y-%m-%d ")  
    liability_number                = request.POST.get('liability_number', '')#保单号
    liability_tax              = request.POST.get('liability_tax', '')#车船税
    liability_price                  = request.POST.get('liability_price', '')#保费
    liability_date_start                 = request.POST.get('liability_date_start', '')#保险期限起始日期
    liability_date_stop       = request.POST.get('liability_date_stop', '')#保险期限终止日期
    liability_company                = request.POST.get('liability_company', '')#承保公司
    liability_phone_num                = request.POST.get('liability_phone_num', '')#报案电话
    if liability_number:
        car.liability_number=liability_number
    else:
        raise ParameterError('交强险保单号未填写')
    if liability_tax:
        try:
            liability_tax=int(float(liability_tax)*100)
            car.liability_tax=liability_tax
        except:
            raise ParameterError('交强险车船税只能为最多带两位小数的数字')
    else:
        raise ParameterError('交强险车船税未填写')
    if liability_price:
        try:
            liability_price=int(float(liability_price)*100)
            car.liability_price=liability_price
        except:
            raise ParameterError('交强险保费只能为最多带两位小数的数字')
    else:
        raise ParameterError('交强险保费未填写')
    if liability_date_start:
        liability_date_start=liability_date_start+" 00:00:00"
        liability_date_start= datetime.strptime(liability_date_start,"%Y-%m-%d %H:%M:%S")
        car.liability_date_start=liability_date_start
    else:
        raise ParameterError('交强险保险期限起始日期未填写')
    
    if liability_date_stop:
        liability_date_stop=liability_date_stop+" 00:00:00"
        liability_date_stop= datetime.strptime(liability_date_stop,"%Y-%m-%d %H:%M:%S")
        if liability_date_stop<liability_date_start:
            raise ParameterError('交强险保险期限终止日期不能小于起始日期')
        else:
            car.liability_date_stop=liability_date_stop
    else:
        raise ParameterError('交强险保险期限终止日期未填写')
    
    if liability_company:
        car.liability_company=liability_company
    else:
        raise ParameterError('交强险承保公司未填写')
    if liability_phone_num:
        car.liability_phone_num=liability_phone_num
    else:
        raise ParameterError('交强险报案电话未填写')
    return car
    
#认证商业险
def commercial_certificate(request,car):
    now =  datetime.now()
    otherStyleTime = now.strftime("%Y-%m-%d ")
    commercial_num              = request.POST.get('commercial_num', '')#保单号
    commercial_price                 = request.POST.get('commercial_price', '')#保费
    commercial_date_start       = request.POST.get('commercial_date_start', '')#保险期限起始日期
    commercial_date_stop                = request.POST.get('commercial_date_stop', '')#保险期限结束日期
    commercial_company                = request.POST.get('commercial_company', '')#承保公司
    commercial_phone_num                = request.POST.get('commercial_phone_num', '')#报案电话
    if commercial_num:
        car.commercial_num=commercial_num
    else:
        raise ParameterError('商业险保单号未填写')
    if commercial_date_start:
        commercial_date_start=commercial_date_start+" 00:00:00"
        commercial_date_start= datetime.strptime(commercial_date_start,"%Y-%m-%d %H:%M:%S")
        car.commercial_date_start=commercial_date_start
    else:
        raise ParameterError('商业险起始日期未填写') 
    if commercial_date_stop:
        commercial_date_stop=commercial_date_stop+" 00:00:00"
        commercial_date_stop =  datetime.strptime(commercial_date_stop,"%Y-%m-%d %H:%M:%S")
        if commercial_date_stop<commercial_date_start:
            raise ParameterError('商业险结束日期不能大于开启日期')   
        else:
            car.commercial_date_stop = commercial_date_stop
    else:
        raise ParameterError('商业险结束日期未填写')
    if commercial_company:
        car.commercial_company=commercial_company
    else:
        raise ParameterError('商业险承保公司未填写')
    if commercial_phone_num:
        car.commercial_phone_num=commercial_phone_num
    else:
        raise ParameterError('商业险报警电话未填写')
    #险种清单
    a=[]
    car.commercial_tax=a
#     for tax in car.commercial_tax:
#         car.commercial_tax.remove(tax)

            
    commercial_tax_list = request.POST.getlist('position')
    commercial_price=0
    if len(commercial_tax_list) > 0:
        for commercial_tax in commercial_tax_list:
            try:
                xz = request.POST.get("xz_" + commercial_tax)
                je = request.POST.get("je_" + commercial_tax)
                taxlist=TaxList()
            except:
                raise ParameterError('商业险险种格式不正确')
            if xz:
                taxlist.com_kind=xz
            else:
                raise ParameterError('商业险险种未填写')
            if je:
                try:
                    je=int(float(je)*100)
                    taxlist.com_price=je
                    commercial_price=commercial_price+je
                except:
                    raise ParameterError('商业险保费只能为最多带两位小数的数字')
                
            else:
                raise ParameterError('商业险险种金额未填写')
            try:
                car.commercial_price=commercial_price
                car.commercial_tax.append( taxlist )
            except:
                raise ParameterError('险种存储过程出错，请检查输入保费部分（保费只能为最多带两位小数的数字）')
                
 
    else:
        raise ParameterError('商业险险种不能为空') 
    if commercial_price:
        car.commercial_price=commercial_price
    else:
        raise ParameterError('商业险保费未填写')
    return car
    
    
    
  #认证成功过程  
@login_required
@AdminRequired
def car_certificate(request, car_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.save_log()
    car = CarCertificate.objects(id=car_id).first()
    now = datetime.now()
#     now = datetime.datetime.now()
#     otherStyleTime = now.strftime("%Y-%m-%d ")
    #result = request.POST.get('type', '')
    result = request.GET.get('type', '')
    data['car']         =car
    data['posted_data'] = request.POST
    try:
        if result:
            #认证行驶证
            if result=="plate":
                car=plate_certificate(request,car)
                print(car.issue_date)
            #认证交强险  
            elif result=="liability":
                car=liability_certificate(request,car)  
            #认证商业险  
            elif result=="commercial":
                car=commercial_certificate(request,car)
            else:
                data['message']= '未找到认证类型' 
                return render_to_response('bms/car/car_detail.html', data, context)
        else:
            data['car'] = car
            data['message'] = '认证类型错误'
            return render_to_response('bms/car/car_detail.html', data, context)
    except CustomError as e:
        data['message'] = e.message
        return render_to_response('bms/car/car_detail.html', data, context)
    except Exception as e:
        data['message'] = str(e)
        return render_to_response('bms/car/car_detail.html', data, context)
    
    if car.car_type :
        car.state="success"
    else:
        car.state="init"
    car.certificate_time = now
    car.save()
    print("car.issue_date======")
    print(car.issue_date)
    return HttpResponseRedirect(reverse('bms:car_detail', args=[car.id, ]))

def car_delete(request,car_id):
    data={}
    page_index = request.session.get('page_index_campaign_driver', '1')
    data['page_index'] = page_index
    if request.method == 'GET':
        car_list = CarCertificate.objects(id=car_id).first()
        if car_list:
            for image_url in car_list.plate_image_left:
                image_tools = ImageTools()
                image_tools.delete(image_url)
            car_list.delete()
        else:
            request.session['message'] = '未找到对应的车辆信息'
    return HttpResponseRedirect(reverse('bms:car_list', args=[page_index, ]))

def car_edit(request,car_id):
    data={}
    car = CarCertificate.objects(id=car_id).first()
    print(car.issue_date)
    print("============================")
    data['car'] = car
    data['a'] = 0
    context = RequestContext(request)
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新","港","澳","台"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    #分解车牌号
    #分解车牌号
    data["short"]=""
    data["mid"]=""
    data["end"]=""
    if car.plate_number:
        try:
            a=car.plate_number
            short = car.plate_number[0]
            mid = car.plate_number[1]
            end = car.plate_number[3:]
            data["short_number"]=short
            data["mid_number"]=mid
            data["end_number"]=end
        except:
            pass
    if request.method == 'GET':
        return render_to_response('bms/car/car_edit.html', data, context)
    else:
        try:
            car=plate_certificate(request,car)
            #car.issue_date="2016年07月25日 00:00:00"
#             a="2016-07-06 00:00:00"
#             issue_date= datetime.datetime.strptime(a,"%Y-%m-%d %H:%M:%S")
# '            car.issue_date=issue_date'
            print(car.issue_date)
            #201610/28屏蔽下方两个验证
#             car=liability_certificate(request,car)
#             car=commercial_certificate(request,car)
        except CustomError as e:
            print("ceshi============")
            print(car.issue_date)
            data['message'] = e.message
            return render_to_response('bms/car/car_edit.html', data, context)
        except Exception as e:
            data['message'] = str(e)
            return render_to_response('bms/car/car_edit.html', data, context)
        car.save()
        data['car'] = car
#         data['message'] = '修改认证信息成功'
        return HttpResponseRedirect(reverse('bms:car_edit', args=[car.id, ]))
        
#编辑车辆图片
def validation_car_pic(request, car):
    car_image = request.FILES.get('car_image_edit', '')
    type =request.POST.get('image_type')
    old_url = request.POST.get('image_url_edit')
    if car_image:
        image_tool = ImageTools()
        car_image_url = image_tool.save(request_file=car_image, file_folder=ImageFolderType.car, old_file='')
        if car_image_url:
            if type=='plate':
                position = -1
                for i in range(len(car.plate_image_left)):
                    if str(car.plate_image_left[i]) == old_url:
                        position = i
                        break
                if position < 0:
                    raise ParameterError('要修改行驶证图片不存在')
                else:
                    car.plate_image_left[position] = car_image_url
            elif type=='liability':
                car.liability_image = car_image_url
            elif type=='commercial':
                car.commercial_image = car_image_url
            else:
                raise ParameterError('替换证件图片失败')
        else:
            raise ParameterError('生成图片地址失败')
    else:
        raise ParameterError('未选择图片，请选择图片')
    return car 
# 修改车辆证件图片
@login_required
@AdminRequired
def edit_car_pic(request, car_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    car = CarCertificate.objects(id=car_id).first()
    if car:
        data['car']=car
        try:
            car=validation_car_pic(request,car)
            car.save()
            request.session['message'] = '编辑图片成功'
        except ParameterError as e:
            request.session['message'] = '编辑图片失败:{0}'.format(e.message)
            return HttpResponseRedirect(reverse('bms:car_edit_new', args=[car.id, ]))
        return HttpResponseRedirect(reverse('bms:car_edit_new', args=[car.id, ]))
    else:
        request.session['message'] = '未找到对应车辆'
        return HttpResponseRedirect(reverse('bms:car_list', args=[1, ]))
    
    
    
# 修改返还油卡金额
@login_required
@AdminRequired
def car_oil_card(request, car_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    car = CarCertificate.objects(id=car_id).first()
    oil_price = request.POST.get("oil_price" )
    message="返还油卡"
    data['posted_data'] = request.POST
    if car:
        data['car']=car
        if oil_price:
            message = message+ oil_price
            try:
                oil_price=int(float(oil_price)*100)
                oil_price_count=oil_price+car.oil_card_price
                car.oil_card_price = oil_price_count
                car.save()
                message=message+"元，充值成功"
                request.session['message']= message
                return HttpResponseRedirect(reverse('bms:car_detail_new', args=[car.id, ]))
            except:
                request.session['message'] = '油卡金额只能为最多带两位小数的数字'
                return HttpResponseRedirect(reverse('bms:car_detail_new', args=[car.id, ]))
        else:
            request.session['message'] = '未输入返还油卡金额'
            return HttpResponseRedirect(reverse('bms:car_detail_new', args=[car.id, ]))
    else:
        request.session['message'] = '未找到对应车辆'
        return HttpResponseRedirect(reverse('bms:car_list', args=[1, ]))  
    
    
#－－－－－－－－－－－－－－－－－－－－－－－－－－     员工保险统计      －－－－－－－－－－－－－－－－－－－－－－－－－－
#员工保险列表
@login_required
@AdminRequired
def employee_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    employee_message = request.session.get('employee_message', )
    data["employee_message"]=employee_message
    request.session['employee_message'] = ""
    order_type = request_tool.get_parameter("order_type")
    order_type =order_type or "create_time"
    data['order_type'] = order_type
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['page_index_employee'] = page_index
        return HttpResponseRedirect(reverse('bms:employee_list', args=[page_index, ]))

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        employee_insurance_list = EmployeeInsurance.objects().order_by(order_type)
        count = employee_insurance_list.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_employee'] = paging['page_index']
        employee_insurance_list = employee_insurance_list[paging['start_item']:paging['end_item']]
        data['employee_insurance_list'] = employee_insurance_list
        #data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/car/employee_list.html', data, context)
    
#创建员工保险
@login_required
@AdminRequired
def employee_create(request):
    context = RequestContext(request)
    data={}
    #激活用户列表
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    data['clients'] = client_set
    #激活公司列表
    tail_company_set = InsuranceCompany.objects()
    tail_company_set = tail_company_set.filter(is_hidden=False)
    data['tail_companys'] = tail_company_set
    #险种列表
    insurance_type_list=EmployeeInsurance.INSURANCE_TYPE
    data['insurance_type_list'] = insurance_type_list
    #员工名单上传方式
    up_roster_list=EmployeeInsurance.UP_ROSTER
    data['up_roster_list'] = up_roster_list
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            employee = EmployeeInsurance()
            employee = bms_tools.validation_create_employee(employee)
            employee.save()
            request.session['message'] = '员工保险创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/car/employee_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/car/employee_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:employee_detail', args=[employee.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/car/employee_create.html', data, context)
    



#查看员工保险
@login_required
@AdminRequired
def employee_detail(request,employee_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_employee', '1')
    try:
        page_index=int(page_index)
    except:
        page_index=1
    data['page_index'] = page_index
    try:
        employee_set = EmployeeInsurance.objects(id=employee_id).first()
        data["employee"]=employee_set
    except Exception as e:
        request.session['employee_message'] = str(e)
        return HttpResponseRedirect(reverse('bms:employee_list', args=[page_index, ]))
    return render_to_response('bms/car/employee_detail.html', data, context)


#编辑员工保险
@login_required
@AdminRequired
def employee_edit(request,employee_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_employee', '1')
    try:
        page_index=int(page_index)
    except:
        page_index=1
    data['page_index'] = page_index
    #激活用户列表
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    data['clients'] = client_set
    #激活公司列表
    tail_company_set = InsuranceCompany.objects()
    tail_company_set = tail_company_set.filter(is_hidden=False)
    data['tail_companys'] = tail_company_set
    #险种列表
    insurance_type_list=EmployeeInsurance.INSURANCE_TYPE
    data['insurance_type_list'] = insurance_type_list
    #员工名单上传方式
    up_roster_list=EmployeeInsurance.UP_ROSTER
    data['up_roster_list'] = up_roster_list
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    try:
        employee_set = EmployeeInsurance.objects(id=employee_id).first()
        data["employee"]=employee_set
    except Exception as e:
        request.session['employee_message'] = str(e)
        return HttpResponseRedirect(reverse('bms:employee_list', args=[page_index, ]))
    if not employee_set:
        request.session['employee_message'] = "网络不稳定，查找员工保险失败"
        return HttpResponseRedirect(reverse('bms:employee_list', args=[page_index, ]))
    else:
        if request.method == 'POST':
            try:
                employee_set = employee_set
                employee_set = bms_tools.validation_create_employee(employee_set)
                employee_set.save()
                request.session['message'] = '员工保险编辑成功'
                data["employee"]=employee_set
                return HttpResponseRedirect(reverse('bms:employee_detail', args=[employee_set.id, ]))
            except CustomError as e:
                data['message'] = e.message
                return render_to_response('bms/car/employee_edit.html', data, context)
            except Exception as e:
                print(traceback.format_exc())
                data['message'] = str(e)
                return render_to_response('bms/car/employee_edit.html', data, context)
        else:
            return render_to_response('bms/car/employee_edit.html', data, context)


#删除员工保险 
@login_required
@AdminRequired
def employee_delete(request,employee_id):
    data={}
    page_index = request.session.get('page_index_employee', '1')
    try:
        page_index=int(page_index)
    except:
        page_index=1
    try:
        employee_set = EmployeeInsurance.objects(id=employee_id).first()
    except Exception as e:
        request.session['employee_message'] = "未找到员工保险信息，错误原因："+str(e)
        return HttpResponseRedirect(reverse('bms:employee_list', args=[page_index, ]))
    if employee_set:
        try:
            employee_set.delete()
            request.session['employee_message'] = '删除成功'
            return HttpResponseRedirect(reverse('bms:employee_list', args=[page_index, ]))
        except Exception as e:
            request.session['employee_message'] = str(e)
    else:
        request.session['employee_message'] ="未找到员工保险信息"
    return HttpResponseRedirect(reverse('bms:employee_list', args=[page_index, ]))
    
#－－－－－－－－－－－－－－－－－－－－－－－－－－     货运年险统计      －－－－－－－－－－－－－－－－－－－－－－－－－－
#货运年险列表
@login_required
@AdminRequired
def freight_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    freight_message = request.session.get('freight_message', )
    data["freight_message"]=freight_message
    request.session['freight_message'] = ""
    order_type = request_tool.get_parameter("order_type")
    order_type =order_type or "create_time"
    data['order_type'] = order_type
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['page_index_freight'] = page_index
        return HttpResponseRedirect(reverse('bms:freight_list', args=[page_index, ]))

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        freight_insurance_list = ＦreightInsurance.objects().order_by(order_type)
        count = freight_insurance_list.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_freight'] = paging['page_index']
        freight_insurance_list = freight_insurance_list[paging['start_item']:paging['end_item']]
        data['freight_insurance_list'] = freight_insurance_list
        #data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/car/freight_list.html', data, context)
    
#创建货运年险
@login_required
@AdminRequired
def freight_create(request):
    context = RequestContext(request)
    data={}
    #激活用户列表
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    data['clients'] = client_set
    #激活公司列表
    tail_company_set = InsuranceCompany.objects()
    tail_company_set = tail_company_set.filter(is_hidden=False)
    data['tail_companys'] = tail_company_set
    #险种列表
    insurance_type_list=ＦreightInsurance.INSURANCE_TYPE
    data['insurance_type_list'] = insurance_type_list
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            freight = ＦreightInsurance()
            freight = bms_tools.validation_create_freight(freight)
            freight.save()
            request.session['message'] = '货运年险创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/car/freight_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/car/freight_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:freight_detail', args=[freight.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/car/freight_create.html', data, context)
    



#查看货运年险
@login_required
@AdminRequired
def freight_detail(request,freight_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_freight', '1')
    try:
        page_index=int(page_index)
    except:
        page_index=1
    data['page_index'] = page_index
    try:
        freight_set = ＦreightInsurance.objects(id=freight_id).first()
        data["freight"]=freight_set
    except Exception as e:
        request.session['freight_message'] = str(e)
        return HttpResponseRedirect(reverse('bms:freight_list', args=[page_index, ]))
    return render_to_response('bms/car/freight_detail.html', data, context)


#编辑货运年险
@login_required
@AdminRequired
def freight_edit(request,freight_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_freight', '1')
    try:
        page_index=int(page_index)
    except:
        page_index=1
    data['page_index'] = page_index
    #激活用户列表
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    data['clients'] = client_set
    #激活公司列表
    tail_company_set = InsuranceCompany.objects()
    tail_company_set = tail_company_set.filter(is_hidden=False)
    data['tail_companys'] = tail_company_set
    #险种列表
    insurance_type_list=ＦreightInsurance.INSURANCE_TYPE
    data['insurance_type_list'] = insurance_type_list
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    try:
        freight_set = ＦreightInsurance.objects(id=freight_id).first()
        data["freight"]=freight_set
    except Exception as e:
        request.session['freight_message'] = str(e)
        return HttpResponseRedirect(reverse('bms:freight_list', args=[page_index, ]))
    if not freight_set:
        request.session['freight_message'] = "网络不稳定，查找货运年险失败"
        return HttpResponseRedirect(reverse('bms:freight_list', args=[page_index, ]))
    else:
        if request.method == 'POST':
            try:
                freight_set = freight_set
                freight_set = bms_tools.validation_create_freight(freight_set)
                freight_set.save()
                request.session['message'] = '货运年险编辑成功'
                data["freight"]=freight_set
                return HttpResponseRedirect(reverse('bms:freight_detail', args=[freight_set.id, ]))
            except CustomError as e:
                data['message'] = e.message
                return render_to_response('bms/car/freight_edit.html', data, context)
            except Exception as e:
                print(traceback.format_exc())
                data['message'] = str(e)
                return render_to_response('bms/car/freight_edit.html', data, context)
        else:
            return render_to_response('bms/car/freight_edit.html', data, context)


#删除货运年险 
@login_required
@AdminRequired
def freight_delete(request,freight_id):
    data={}
    page_index = request.session.get('page_index_freight', '1')
    try:
        page_index=int(page_index)
    except:
        page_index=1
    try:
        freight_set = ＦreightInsurance.objects(id=freight_id).first()
    except Exception as e:
        request.session['freight_message'] = "未找到货运年险信息，错误原因："+str(e)
        return HttpResponseRedirect(reverse('bms:freight_list', args=[page_index, ]))
    if freight_set:
        try:
            freight_set.delete()
            request.session['freight_message'] = '删除成功'
            return HttpResponseRedirect(reverse('bms:freight_list', args=[page_index, ]))
        except Exception as e:
            request.session['freight_message'] = str(e)
    else:
        request.session['freight_message'] ="未找到货运年险信息"
    return HttpResponseRedirect(reverse('bms:freight_list', args=[page_index, ]))




#－－－－－－－－－－－－－－－－－－－－－－－－－－     个人保险统计      －－－－－－－－－－－－－－－－－－－－－－－－－－
#个人保险列表
@login_required
@AdminRequired
def personal_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    personal_message = request.session.get('personal_message', )
    data["personal_message"]=personal_message
    request.session['personal_message'] = ""
    order_type = request_tool.get_parameter("order_type")
    order_type =order_type or "create_time"
    data['order_type'] = order_type
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['page_index_personal'] = page_index
        return HttpResponseRedirect(reverse('bms:personal_list', args=[page_index, ]))

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        personal_insurance_list = PersonalInsurance.objects().order_by(order_type)
        count = personal_insurance_list.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_personal'] = paging['page_index']
        personal_insurance_list = personal_insurance_list[paging['start_item']:paging['end_item']]
        data['personal_insurance_list'] = personal_insurance_list
        #data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/car/personal_list.html', data, context)
    
#创建个人保险
@login_required
@AdminRequired
def personal_create(request):
    context = RequestContext(request)
    data={}
    #激活用户列表
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    data['clients'] = client_set
    #激活公司列表
    tail_company_set = InsuranceCompany.objects()
    tail_company_set = tail_company_set.filter(is_hidden=False)
    data['tail_companys'] = tail_company_set
    #险种列表
    insurance_type_list=PersonalInsurance.INSURANCE_TYPE
    data['insurance_type_list'] = insurance_type_list
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            personal = PersonalInsurance()
            personal = bms_tools.validation_create_personal(personal)
            personal.save()
            request.session['message'] = '个人保险创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/car/personal_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/car/personal_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:personal_detail', args=[personal.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/car/personal_create.html', data, context)
    



#查看个人保险
@login_required
@AdminRequired
def personal_detail(request,personal_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_personal', '1')
    try:
        page_index=int(page_index)
    except:
        page_index=1
    data['page_index'] = page_index
    try:
        personal_set = PersonalInsurance.objects(id=personal_id).first()
        data["personal"]=personal_set
    except Exception as e:
        request.session['personal_message'] = str(e)
        return HttpResponseRedirect(reverse('bms:personal_list', args=[page_index, ]))
    return render_to_response('bms/car/personal_detail.html', data, context)


#编辑个人保险
@login_required
@AdminRequired
def personal_edit(request,personal_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_personal', '1')
    try:
        page_index=int(page_index)
    except:
        page_index=1
    data['page_index'] = page_index
    #激活用户列表
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    data['clients'] = client_set
    #激活公司列表
    tail_company_set = InsuranceCompany.objects()
    tail_company_set = tail_company_set.filter(is_hidden=False)
    data['tail_companys'] = tail_company_set
    #险种列表
    insurance_type_list=PersonalInsurance.INSURANCE_TYPE
    data['insurance_type_list'] = insurance_type_list
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    try:
        personal_set = PersonalInsurance.objects(id=personal_id).first()
        data["personal"]=personal_set
    except Exception as e:
        request.session['personal_message'] = str(e)
        return HttpResponseRedirect(reverse('bms:personal_list', args=[page_index, ]))
    if not personal_set:
        request.session['personal_message'] = "网络不稳定，查找个人保险失败"
        return HttpResponseRedirect(reverse('bms:personal_list', args=[page_index, ]))
    else:
        if request.method == 'POST':
            try:
                personal_set = personal_set
                personal_set = bms_tools.validation_create_personal(personal_set)
                personal_set.save()
                request.session['message'] = '个人保险编辑成功'
                data["personal"]=personal_set
                return HttpResponseRedirect(reverse('bms:personal_detail', args=[personal_set.id, ]))
            except CustomError as e:
                data['message'] = e.message
                return render_to_response('bms/car/personal_edit.html', data, context)
            except Exception as e:
                print(traceback.format_exc())
                data['message'] = str(e)
                return render_to_response('bms/car/personal_edit.html', data, context)
        else:
            return render_to_response('bms/car/personal_edit.html', data, context)


#删除个人保险 
@login_required
@AdminRequired
def personal_delete(request,personal_id):
    data={}
    page_index = request.session.get('page_index_personal', '1')
    try:
        page_index=int(page_index)
    except:
        page_index=1
    try:
        personal_set = PersonalInsurance.objects(id=personal_id).first()
    except Exception as e:
        request.session['personal_message'] = "未找到个人保险信息，错误原因："+str(e)
        return HttpResponseRedirect(reverse('bms:personal_list', args=[page_index, ]))
    if personal_set:
        try:
            personal_set.delete()
            request.session['personal_message'] = '删除成功'
            return HttpResponseRedirect(reverse('bms:personal_list', args=[page_index, ]))
        except Exception as e:
            request.session['personal_message'] = str(e)
    else:
        request.session['personal_message'] ="未找到个人保险信息"
    return HttpResponseRedirect(reverse('bms:personal_list', args=[page_index, ]))


#－－－－－－－－－－－－－－－－－－－－－－－－－－     车险      －－－－－－－－－－－－－－－－－－－－－－－－－－
#创建我的车辆
@login_required
@AdminRequired
def car_create_new(request):
    context = RequestContext(request)
    data = {}
    #2017修改用户流程
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    count1=client_set.count()
    #client_set = Client.objects().filter(user_type__ne='registered')
    data['clients'] = client_set
    page_index = request.session.get('page_index_car_list', '1')
    data['page_index'] = page_index
    #车牌号
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新","港","澳","台"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    #车辆类型
    car_type = CarCertificate.CAR_TYPE                 #车辆类型
    data['car_type_list'] =car_type
    #使用性质
    use_property = CarCertificate.USE_PROPERTY        #使用性质
    data['use_property_list'] = use_property
    #激活公司列表
    tail_company_set = InsuranceCompany.objects()
    tail_company_set = tail_company_set.filter(is_hidden=False)
    data['tail_companys'] = tail_company_set
    #商业险险种列表
    commercial_tax_list = CarCertificate.COMMERCIAL_KIND                 #商业险险种列表
    data['commercial_tax_list'] =commercial_tax_list
    
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            create_car = CarCertificate()
            create_car = bms_tools.validation_create_car_new(create_car)
            create_car.save()
            request.session['message'] = '车辆创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/car/car_create_new.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/car/car_create_new.html', data, context)
        return HttpResponseRedirect(reverse('bms:car_detail_new', args=[create_car.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/car/car_create_new.html', data, context)


@login_required
@AdminRequired
def car_detail_new(request, car_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_car_id', '1')
    data['page_index'] = page_index
    car = CarCertificate.objects(id=car_id).first()
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新","港","澳","台"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    if car:
        total=car.liability_tax+car.liability_price+car.commercial_price
        net_value = total-car.oil_card_price
        data['car'] = car
        data['total'] = total
        data['net_value'] = net_value
        #分解车牌号
        data["short"]=""
        data["mid"]=""
        data["end"]=""
        if car.plate_number:
            try:
                a=car.plate_number
                short = car.plate_number[0]
                mid = car.plate_number[1]
                end = car.plate_number[3:]
                data["short_number"]=short
                data["mid_number"]=mid
                data["end_number"]=end
            except:
                pass
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:car_list', args=[page_index, ]))
    return render_to_response('bms/car/car_detail_new.html', data, context)  

def car_edit_new(request,car_id):
    data={}
    car = CarCertificate.objects(id=car_id).first()
    print(car.issue_date)
    print("============================")
    data['car'] = car
    data['a'] = 0
    context = RequestContext(request)
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新","港","澳","台"]
    data["short_detail"] = short_detail
    mid_detail=['A' ,'B', 'C','D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    data["mid_detail"] = mid_detail
    #分解车牌号
    #分解车牌号
    data["short"]=""
    data["mid"]=""
    data["end"]=""
    if car.plate_number:
        try:
            a=car.plate_number
            short = car.plate_number[0]
            mid = car.plate_number[1]
            end = car.plate_number[3:]
            data["short_number"]=short
            data["mid_number"]=mid
            data["end_number"]=end
        except:
            pass
    #2017修改用户流程
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    count1=client_set.count()
    #client_set = Client.objects().filter(user_type__ne='registered')
    data['clients'] = client_set
    #车辆类型
    car_type = CarCertificate.CAR_TYPE                 #车辆类型
    data['car_type_list'] =car_type
    #使用性质
    use_property = CarCertificate.USE_PROPERTY        #使用性质
    data['use_property_list'] = use_property
    #激活公司列表
    tail_company_set = InsuranceCompany.objects()
    tail_company_set = tail_company_set.filter(is_hidden=False)
    data['tail_companys'] = tail_company_set
    #商业险险种列表
    commercial_tax_list = CarCertificate.COMMERCIAL_KIND                 #商业险险种列表
    data['commercial_tax_list'] =commercial_tax_list
    #添加商业险补充部分
    data['com_notice_list'] =["第三者责任险","划痕险","玻璃险","司机险","乘客险"]
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    if request.method == 'GET':
        return render_to_response('bms/car/car_edit_new.html', data, context)
    else:
        try:
            car = bms_tools.validation_create_car_new(car)
            car.save()
            request.session['message'] = '编辑成功'
        except CustomError as e:
            print("ceshi============")
            print(car.issue_date)
            data['message'] = e.message
            return render_to_response('bms/car/car_edit_new.html', data, context)
        except Exception as e:
            data['message'] = str(e)
            return render_to_response('bms/car/car_edit_new.html', data, context)
        data['car'] = car
#         data['message'] = '修改认证信息成功'
        return HttpResponseRedirect(reverse('bms:car_detail_new', args=[car.id, ]))
    
    
    
    
    #－－－－－－－－－－－－－－－－－－－－－－－－－－     其他保险统计      －－－－－－－－－－－－－－－－－－－－－－－－－－
#其他保险列表
@login_required
@AdminRequired
def other_insurance_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    other_insurance_message = request.session.get('other_insurance_message', )
    data["other_insurance_message"]=other_insurance_message
    order_type = request_tool.get_parameter("order_type")
    order_type =order_type or "create_time"
    data['order_type'] = order_type
    request.session['other_insurance_message'] = ""
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['page_index_other_insurance'] = page_index
        return HttpResponseRedirect(reverse('bms:other_insurance_list', args=[page_index, ]))

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        other_insurance_list = OtherInsurance.objects().order_by(order_type)
        count = other_insurance_list.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_other_insurance'] = paging['page_index']
        other_insurance_list = other_insurance_list[paging['start_item']:paging['end_item']]
        data['other_insurance_list'] = other_insurance_list
        #data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/car/other_insurance_list.html', data, context)
    
#创建其他保险
@login_required
@AdminRequired
def other_insurance_create(request):
    context = RequestContext(request)
    data={}
    #激活用户列表
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    data['clients'] = client_set

    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    #激活公司列表
    tail_company_set = InsuranceCompany.objects()
    tail_company_set = tail_company_set.filter(is_hidden=False)
    data['tail_companys'] = tail_company_set
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            other_insurance = OtherInsurance()
            other_insurance = bms_tools.validation_create_other_insurance(other_insurance)
            other_insurance.save()
            request.session['message'] = '其他保险创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/car/other_insurance_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/car/other_insurance_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:other_insurance_detail', args=[other_insurance.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/car/other_insurance_create.html', data, context)
    



#查看其他保险
@login_required
@AdminRequired
def other_insurance_detail(request,other_insurance_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_other_insurance', '1')
    try:
        page_index=int(page_index)
    except:
        page_index=1
    data['page_index'] = page_index
    try:
        other_insurance_set = OtherInsurance.objects(id=other_insurance_id).first()
        data["other_insurance"]=other_insurance_set
    except Exception as e:
        request.session['other_insurance_message'] = str(e)
        return HttpResponseRedirect(reverse('bms:other_insurance_list', args=[page_index, ]))
    return render_to_response('bms/car/other_insurance_detail.html', data, context)


#编辑其他保险
@login_required
@AdminRequired
def other_insurance_edit(request,other_insurance_id):
    data={}
    context = RequestContext(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_other_insurance', '1')
    #激活公司列表
    tail_company_set = InsuranceCompany.objects()
    tail_company_set = tail_company_set.filter(is_hidden=False)
    data['tail_companys'] = tail_company_set
    try:
        page_index=int(page_index)
    except:
        page_index=1
    data['page_index'] = page_index
    #激活用户列表
    user_set = User.objects(is_active=True)
    client_set = Client.objects().filter(user__in=user_set)
    data['clients'] = client_set

    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    try:
        other_insurance_set = OtherInsurance.objects(id=other_insurance_id).first()
        data["other_insurance"]=other_insurance_set
    except Exception as e:
        request.session['other_insurance_message'] = str(e)
        return HttpResponseRedirect(reverse('bms:other_insurance_list', args=[page_index, ]))
    if not other_insurance_set:
        request.session['other_insurance_message'] = "网络不稳定，查找其他保险失败"
        return HttpResponseRedirect(reverse('bms:other_insurance_list', args=[page_index, ]))
    else:
        if request.method == 'POST':
            try:
                other_insurance_set = other_insurance_set
                other_insurance_set = bms_tools.validation_create_other_insurance(other_insurance_set)
                other_insurance_set.save()
                request.session['message'] = '其他保险编辑成功'
                data["other_insurance"]=other_insurance_set
                return HttpResponseRedirect(reverse('bms:other_insurance_detail', args=[other_insurance_set.id, ]))
            except CustomError as e:
                data['message'] = e.message
                return render_to_response('bms/car/other_insurance_edit.html', data, context)
            except Exception as e:
                print(traceback.format_exc())
                data['message'] = str(e)
                return render_to_response('bms/car/other_insurance_edit.html', data, context)
        else:
            return render_to_response('bms/car/other_insurance_edit.html', data, context)


#删除其他保险 
@login_required
@AdminRequired
def other_insurance_delete(request,other_insurance_id):
    data={}
    page_index = request.session.get('page_index_other_insurance', '1')
    try:
        page_index=int(page_index)
    except:
        page_index=1
    try:
        other_insurance_set = OtherInsurance.objects(id=other_insurance_id).first()
    except Exception as e:
        request.session['other_insurance_message'] = "未找到其他保险信息，错误原因："+str(e)
        return HttpResponseRedirect(reverse('bms:other_insurance_list', args=[page_index, ]))
    if other_insurance_set:
        try:
            other_insurance_set.delete()
            request.session['other_insurance_message'] = '删除成功'
            return HttpResponseRedirect(reverse('bms:other_insurance_list', args=[page_index, ]))
        except Exception as e:
            request.session['other_insurance_message'] = str(e)
    else:
        request.session['other_insurance_message'] ="未找到其他保险信息"
    return HttpResponseRedirect(reverse('bms:other_insurance_list', args=[page_index, ]))




#-----------------------2018/1/02 保险管家隐藏各个保险产品-----------------------------------------------------------------------
#隐藏车险
@login_required
@AdminRequired
def car_change_state(request, car_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    if request.method == 'POST':
        request_tools.save_log()
        state = request.POST.get('state', '')
        page_index = request.POST.get('page_index', '1')
    else:
        request_tools.save_log()
        state = request.GET.get('state', '')
        page_index = request.GET.get('page_index', '1')
    if state not in ['show','hide']:
         request.session['message'] = '车辆保险修改状态不正确，请刷新后重试'
         return HttpResponseRedirect(reverse('bms:car_list', args=[page_index, ]))
    if state == 'show':
         car_state = False
    else:
         car_state = True
    try:
        car = CarCertificate.objects(id=car_id).first()
        car.is_hidden= car_state
        car.save()
    except:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:car_list', args=[page_index, ]))
    return HttpResponseRedirect(reverse('bms:car_list', args=[page_index, ]))


#修改保险管家各个保险显示状态
@login_required
@AdminRequired
def policy_change_state(request, policy_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    if request.method == 'POST':
        request_tools.save_log()
        state = request.POST.get('state', '')
        policy_state = request.POST.get('policy_state', '')
        page_index = request.POST.get('page_index', '1')
    else:
        request_tools.save_log()
        state = request.GET.get('state', '')
        policy_state = request.GET.get('policy_state', '')
        page_index = request.GET.get('page_index', '1')
    if policy_state not in ['employee','freight','personal','other_insurance']:
         request.session['message'] = '保险修改状态不正确，请刷新后重试'
         return HttpResponseRedirect(reverse('bms:car_list', args=[page_index, ]))
    next_url='bms:'+str(policy_state)+'_list'
    if state not in ['show','hide']:
         request.session['message'] = '保险修改状态不正确，请刷新后重试'
         return HttpResponseRedirect(reverse(next_url, args=[page_index, ]))
    if state == 'show':
         policy_type = False
    else:
         policy_type = True
    try:
        if policy_state == 'employee':
            policy = EmployeeInsurance.objects(id=policy_id).first()
        elif policy_state == 'freight':
            policy = ＦreightInsurance.objects(id=policy_id).first()
        elif policy_state == 'personal':
            policy = PersonalInsurance.objects(id=policy_id).first()
        elif policy_state == 'other_insurance':
            policy = OtherInsurance.objects(id=policy_id).first()
        else:
            request.session['message'] = '未找到对应数据'
            return HttpResponseRedirect(reverse(next_url, args=[page_index, ]))
        policy.is_hidden= policy_type
        policy.save()
    except:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse(next_url, args=[page_index, ]))
    return HttpResponseRedirect(reverse(next_url, args=[page_index, ]))






      