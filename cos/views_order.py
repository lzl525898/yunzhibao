__author__ = 'mlzx'
import hashlib
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from common.tools import *
from django.shortcuts import render_to_response, HttpResponse
import traceback
import math
from common.tools_legoo import DocumentTools, DocumentFolderType, ImageTools, ImageFolderType
from common.tools import RequestTools
from bms.tools import DocumentBmsTools
from common.tools_excel_export import ExcelExportTools
from django.contrib.staticfiles.templatetags.staticfiles import static
#微信通知
from wss.views_sendmessage import  send_wx_message
#－－－－－－－－－－－－－－－－－－－－－－－－－－     订单列表      －－－－－－－－－－－－－－－－－－－－－－－－－－

#原来订单筛选方法
@login_required
#@AdminRequired
def order_list1(request, page_index):
    
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    test_user =request.user
    claim = Claim.objects(user = test_user).first()
    claims_company = claim.company
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_order'] = search_keyword
        start_time = request.POST.get('start_time', '')
        request.session['start_time'] = start_time
        end_time = request.POST.get('end_time', '')
        request.session['end_time'] = end_time
        request.session['page_index_order'] = 1
        state = request_tool.get_parameter("state")
        pay_state = request_tool.get_parameter("pay_state")
        user_type = request_tool.get_parameter("user_type")
        id_client = request_tool.get_parameter("client_sign")
        get_parameter = "?state={0}&pay_state={1}&user_type={2}&id_client={3}".format(state, pay_state, user_type, id_client)
        return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_order', '')
        order_set = Ordering.objects()
        order_set = request_tool.order_filter(order_set=order_set, keyword=search_keyword)
        order_set = order_set.filter(is_hidden=False, state='paid')
        order_set = order_set.filter(company = claims_company)
        count = order_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_order'] = paging['page_index']
        order_set = order_set[paging['start_item']:paging['end_item']]

        user_type = request_tool.get_parameter("user_type", '')
        if user_type:
            client_set = Client.objects().filter(user_type=user_type)
        else:
            client_set = Client.objects().filter(user_type__ne='registered')
        data['clients'] = client_set
        data['orders'] = order_set
        data['search_keyword'] = search_keyword
        data['start_time'] = request.session.get('start_time', '')
        data['end_time'] = request.session.get('end_time', '')
        request.session['start_time'] = ''
        request.session['end_time'] = ''
        data['paging'] = paging
        return render_to_response('cos/order/order_list.html', data, context)
    
#201711011014添加订单筛选页面
@login_required
#@AdminRequired
def order_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    test_user =request.user
    claim = Claim.objects(user = test_user).first()
    claims_company = claim.company
    try:
        insurance_product_list = InsuranceProducts.objects(company=claims_company)
        insurance_product_list = insurance_product_list.filter(is_hidden=False)#只能查看在保状态保单
    except Exception as e:
        test_message = str(e)
        insurance_product_list=[]
    data['insurance_product_list'] = insurance_product_list
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_order'] = search_keyword
        start_time = request.POST.get('start_time', '')
        request.session['start_time'] = start_time
        end_time = request.POST.get('end_time', '')
        request.session['end_time'] = end_time
        request.session['page_index_order'] = 1
        state = request_tool.get_parameter("state")
        pay_state = request_tool.get_parameter("pay_state")
        user_type = request_tool.get_parameter("user_type")
        id_client = request_tool.get_parameter("client_sign")
        product_detail_id =request_tool.get_parameter("product_detail_id")
        #修改订单状态
        order_from = "cos_order"
        get_parameter = "?state={0}&product_detail_id={1}&user_type={2}&client_sign={3}&start_time={4}&end_time={5}&search_keyword={6}&order_from={7}".format(state, product_detail_id, user_type, id_client,start_time,end_time,search_keyword,order_from)
        return HttpResponseRedirect(reverse('cos:order_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request_tool.get_parameter("search_keyword", '')
        product_detail_id =request_tool.get_parameter("product_detail_id", '')#按保险产品查询
        order_set = Ordering.objects()
        order_set = request_tool.order_filter(order_set=order_set, keyword=search_keyword)
        order_set = order_set.filter(is_hidden=False, state='paid')
        order_set = order_set.filter(company = claims_company)
        order_set_list = order_set
        data['order_set_list'] = order_set_list
        count = order_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_order'] = paging['page_index']
        order_set = order_set[paging['start_item']:paging['end_item']]

        user_type = request_tool.get_parameter("user_type", '')
        if user_type:
            client_set = Client.objects().filter(user_type=user_type)
        else:
            #修改流程后所有用户都可以下单
            user_set = User.objects(is_active=True)
            client_set = Client.objects().filter(user__in=user_set)
            #client_set = Client.objects().filter(user_type__ne='registered')
        data['clients'] = client_set
        data['orders'] = order_set
        data['search_keyword'] = search_keyword
        data['start_time'] = request_tool.get_parameter("start_time", '')
        data['end_time'] = request_tool.get_parameter("end_time", '')
        data['paging'] = paging
        return render_to_response('cos/order/order_list.html', data, context)

@login_required
#@AdminRequired
def order_detail(request, order_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    order = Ordering.objects(id=order_id).first()
    if order:
        data['order'] = order
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('cos:order_list', args=[page_index, ]))
    return render_to_response('cos/order/order_detail.html', data, context)


@login_required
def order_export(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    search_keyword = request_tool.get_parameter('search_keyword', '')
    start_time = request.POST.get('start_time', '')
    end_time = request.POST.get('end_time', '')
    user_type = request_tool.get_parameter("user_type")
    id_client = request_tool.get_parameter("client_sign")
    product_detail_id =request_tool.get_parameter("product_detail_id")
    request.session['search_keyword_order'] = search_keyword
    request.session['page_index_order'] = 1
    test_user =request.user
    claim = Claim.objects(user = test_user).first()
    claims_company = claim.company
    get_parameter = "?product_detail_id={0}&user_type={1}&client_sign={2}&start_time={3}&end_time={4}&search_keyword={5}".format( product_detail_id, user_type, id_client,start_time,end_time,search_keyword)
    try:
        request.session['start_time'] = start_time
        request.session['end_time'] = end_time

        order_set = Ordering.objects()
        order_set = request_tool.order_filter(order_set=order_set, keyword=search_keyword)
        order_set = order_set.filter(company = claims_company)
        order_set = order_set.filter(is_hidden=False, state='paid')
        if order_set:
            export_tools = ExcelExportTools()
            file_url = export_tools.export(order_set, Ordering.FIELD_TUPLE)
            print(file_url)
            url = static('/static/'+file_url)
            # request_tool.set_message('导出成功')
            return HttpResponseRedirect(url)
        else:
            request_tool.set_message('没有找到要导入的订单')
            return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]) + get_parameter)
    except CustomError as e:
        request_tool.set_message(e.message)
    except Exception as e:
        print(traceback.format_exc())
        request_tool.set_message(str(e))
    return HttpResponseRedirect(reverse('bms:order_list', args=[1, ]) + get_parameter)

@login_required
# @AdminRequired
def import_insurance(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    search_keyword = request_tool.get_parameter('search_keyword', '')
    start_time = request.POST.get('start_time', '')
    request.session['start_time'] = start_time
    end_time = request.POST.get('end_time', '')
    request.session['end_time'] = end_time
    state = request_tool.get_parameter("state")
    pay_state = request_tool.get_parameter("pay_state")
    user_type = request_tool.get_parameter("user_type")
    id_client = request_tool.get_parameter("client_sign")
    request.session['search_keyword_order'] = search_keyword
    request.session['page_index_order'] = 1
    get_parameter = "?state={0}&pay_state={1}&user_type={2}&id_client={3}".format(state, pay_state, user_type, id_client)
    test_user =request.user
    claim = Claim.objects(user = test_user).first()
    claims_company = claim.company
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            image_tool = ImageTools()
            order_set = Ordering.objects()
            order_set = request_tool.order_filter(order_set=order_set, keyword=search_keyword)
            order_set = order_set.filter(company = claims_company)
            order_set = order_set.filter(state = 'paid')
            for order in order_set:
                if order.state == 'paid':
                    insurance_image_list = request.FILES.getlist('insurance_image_list', '')
                    insurance_id = request_tool.get_parameter('insurance_id', '')
                    temp = []
                    if insurance_image_list:
                        for insurance_image in insurance_image_list:
                            order_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
                            if not order_image_url:
                                request_tool.set_message(order.paper_id+'生成图片地址失败')
                                return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
                            else:
                                temp.append(order_image_url)
                    else:
                        request_tool.set_message('导入失败，请填入保单图片')
                        return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)

                    order.insurance_id = insurance_id
                    order.insurance_image_list = temp
                    order.state = 'done'
                    order.save()
                else:
                    request_tool.set_message(order.paper_id+'订单的状态不正确')
                    return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
            request_tool.set_message('导入成功')
            return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]))
        except CustomError as e:
            request_tool.set_message(e.message)
        except Exception as e:
            print(traceback.format_exc())
            request_tool.set_message(str(e))
        return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
    
    
    
    
    
    
#－－－－－－－－－－－－－－－－－－－－－－－－－－    中介询价 订单列表      －－－－－－－－－－－－－－－－－－－－－－－－－
    
@login_required
#@AdminRequired
def cos_jdclbx_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    #报价中介
    try:
        test_user =request.user
        intermediary_people = IntermediaryPeople.objects(user = test_user).first()
    except:
        data['message']='未获取登陆中介人员身份信息，请稍后重试'
        return render_to_response('cos/order/jdclbx_list.html', data, context)
    data['intermediary_name'] = intermediary_people.intermediary.intermediary_name
    if request.method == 'POST':
        request_tool.save_log()
        pay_state = request_tool.get_parameter("pay_state")
        id_client = request_tool.get_parameter("client_sign")
        search_keyword = request.POST.get('search_keyword', '')
        get_parameter = "?pay_state={0}&search_keyword={1}&id_client={2}".format(pay_state, search_keyword, id_client)
        #return HttpResponseRedirect(reverse('bms:jdclbx_list', args=[page_index, ])+ get_parameter )
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ])+ get_parameter )

    elif request.method == 'GET':
        client_set = Client.objects().filter(user_type__ne='registered')
        data['clients'] = client_set
        request_tool.check_message(data)
        data["get_data"] = request.GET
        order_set = InquiryInfo.objects(Q(state = 'price') | Q(state = 'wait')).filter(intermediary_list__icontains=intermediary_people.intermediary).order_by('-create_time')
        order_set = request_tool.jdcbx_filter(order_set=order_set)
   
        count = order_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_order'] = paging['page_index']
        order_set = order_set[paging['start_item']:paging['end_item']]

        data['orders'] = order_set
        data['paging'] = paging
        return render_to_response('cos/order/jdclbx_list.html', data, context)
    
    
@login_required
def cos_jdclbx_detail(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    jdclbx_id=jdclbx_id
    try:
        test_user =request.user
        intermediary_people = IntermediaryPeople.objects(user = test_user).first()
        data['intermediary_name'] = intermediary_people.intermediary.intermediary_name
    except:
        request.session['message'] = '未获取登陆中介人员身份信息，请稍后重试。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    
    
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()
        if jdclbx_set.state != 'price'  and jdclbx_set.state != 'wait' :
            return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
#         a=jdclbx_set.plate_image_left
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    if jdclbx_set:
        data['jdclbx_set'] = jdclbx_set
        print(data)
        price_message=request.session.get('price_message',"")
        request.session['price_message'] =""
        if price_message:
            data["message"]=price_message
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    
    #2017添加中介下保险公司是否承保该订单的判断
    company_list = intermediary_people.intermediary.intermediary_company_list
    company_list1=[]
    for company in company_list:
        try:
             intermediary_rate_set = IntermediaryRate.objects(intermediary=intermediary_people.intermediary , company=company,jdclbx_order=jdclbx_set).first()
             if intermediary_rate_set:
                 if intermediary_rate_set.company_state==True:
                     company_list1.append(company)
        except:
            print('中介渠道下关联公司出现调整')
            
            
    data["company_list"] = company_list1
    
    try:
        intermediary_price_list =IntermediaryPrice.objects(insurance_intermediary = intermediary_people.intermediary,order =jdclbx_set )
        data["intermediary_price_list"]=intermediary_price_list
    except:
        data["intermediary_price_list"]=''
        
    order_state="0"
    try:
        intermediary_price_state=IntermediaryPrice.objects(insurance_intermediary = intermediary_people.intermediary,order =jdclbx_set ).first()
        if intermediary_price_state:
            order_state=intermediary_price_state.state 
    except:
        order_state="0"
    data['order_state'] = order_state
    #添加特别约定回显
    if jdclbx_set.special_agreement:
        if len(jdclbx_set.special_agreement)>40:
            data['special_agreement'] = jdclbx_set.special_agreement[0:39]+'……'
        else:
            data['special_agreement'] = jdclbx_set.special_agreement
    return render_to_response('cos/order/jdclbx_detail_new.html', data, context)  


#验证单个公司报价
def verify_intermediary_price(request, jdclbx_set,intermediary_price):
    #报价公司
    bj_company_id = request.POST.get('bj_company_id', '')#报价公司
    if bj_company_id:
        try:
            company_set = InsuranceCompany.objects(id =bj_company_id ).first()
            if not company_set:
                raise ParameterError('网络问题，未获取到当前报价公司信息!')
        except:
            raise ParameterError('网络问题未获取到当前报价公司信息。')
    else:
        raise ParameterError('网络问题未获取到当前报价公司信息')
    intermediary_price.company=company_set
    
    #报价订单
    if not jdclbx_set:
        raise ParameterError('网络问题未获取到当前报价订单信息')
    intermediary_price.order=jdclbx_set
        
    #报价中介
    try:
        test_user =request.user
        intermediary_people = IntermediaryPeople.objects(user = test_user).first()
    except:
        raise ParameterError('未获取登陆中介人员身份信息，请稍后重试')
    intermediary_price.insurance_intermediary=intermediary_people.intermediary
    
    #获取报价手续费中间表信息
    try:
        intermediary_rate_set =IntermediaryRate.objects(company=company_set , intermediary=intermediary_people.intermediary,jdclbx_order=jdclbx_set).first()
    except:
        raise ParameterError('获取手续费信息失败，请联系管理员')
    if not intermediary_rate_set:
        raise ParameterError('未获取到报价公司手续费比例，请及时联系管理员设置本公司手续费比例')
    else:
        if intermediary_rate_set.company_state ==False:
            raise ParameterError(str(company_set.simple_name)+'不保此单无需报价')
        intermediary_price.liability_process_price=intermediary_rate_set.liability_process_price#交强险险手续费比例
        intermediary_price.commercial_process_price=intermediary_rate_set.commercial_process_price#商业险手续费比例
    
    
    #交强险
    liability_price = request.POST.get('liability_price', '')
    liability_process_price = request.POST.get('liability_process_price', '')
    if jdclbx_set.liability_state == True:
        #交强险报价
        if liability_price:
            try:
                liability_price = int(float(liability_price)*100)
                intermediary_price.liability_price=liability_price
            except:
                raise ParameterError('交强险报价请输入最多两位小数的数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'交强险报价')
    else:
        intermediary_price.liability_price=0
    
    
    #车船稅
    vehicle_vessel_price = request.POST.get('vehicle_vessel_price', '')
    vehicle_vessel_process_price = request.POST.get('vehicle_vessel_process_price', '')
    if jdclbx_set.vehicle_vessel_tax_state == True:
        #车船稅报价
        if vehicle_vessel_price:
            try:
                vehicle_vessel_price = int(float(vehicle_vessel_price)*100)
                intermediary_price.vehicle_vessel_price=vehicle_vessel_price
            except:
                raise ParameterError('车船稅报价请输入最多两位小数的数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'车船稅报价')
    else:
        intermediary_price.vehicle_vessel_price=0
    
    #商业险
    #商业险详情
    #三者险
    third_insurance_price = request.POST.get('third_insurance_price', '')
    if jdclbx_set.third_insurance != 0:
        if third_insurance_price:
            try:
                third_insurance_price = int(float(third_insurance_price)*100)
                if third_insurance_price <=0:
                    raise ParameterError(str(company_set.simple_name)+'三者险报价应大于零')
                intermediary_price.third_insurance_price=third_insurance_price
            except:
                raise ParameterError('三者险报价请输入数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'三者险报价')
    else:
        intermediary_price.third_insurance_price=0
    #车损险
    damage_insurance_price = request.POST.get('damage_insurance_price', '')
    if  jdclbx_set.damage_insurance == True:
        if damage_insurance_price:
            try:
                damage_insurance_price = int(float(damage_insurance_price)*100)
                if damage_insurance_price <=0:
                    raise ParameterError(str(company_set.simple_name)+'车损险报价应大于零')
                intermediary_price.damage_insurance_price = damage_insurance_price
            except:
                raise ParameterError('车损险报价请输入数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'车损险报价')
    else:
        intermediary_price.damage_insurance_price = 0
    #玻璃险
    glass_insurance_price = request.POST.get('glass_insurance_price', '')
    if  jdclbx_set.glass_insurance != 'no' :
        if glass_insurance_price:
            try:
                glass_insurance_price = int(float(glass_insurance_price)*100)
                if glass_insurance_price <=0:
                    raise ParameterError(str(company_set.simple_name)+'玻璃险报价应大于零')
                intermediary_price.glass_insurance_price = glass_insurance_price
            except:
                raise ParameterError('玻璃险报价请输入数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'玻璃险报价')
    else:
        intermediary_price.glass_insurance_price = 0

    #司机险
    driver_insurance_price = request.POST.get('driver_insurance_price', '')
    if  jdclbx_set.driver_insurance != 0:
        if driver_insurance_price:
            try:
                driver_insurance_price = int(float(driver_insurance_price)*100)
                if driver_insurance_price <=0:
                    raise ParameterError(str(company_set.simple_name)+'司机险报价应大于零')
                intermediary_price.driver_insurance_price = driver_insurance_price
            except:
                raise ParameterError('司机险报价请输入数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'司机险报价')
    else:
        intermediary_price.driver_insurance_price = 0
    #盗抢险    
    theft_insurance_price = request.POST.get('theft_insurance_price', '')
    if   jdclbx_set.theft_insurance == True:
        if theft_insurance_price:
            try:
                theft_insurance_price = int(float(theft_insurance_price)*100)
                if theft_insurance_price <=0:
                    raise ParameterError(str(company_set.simple_name)+'盗抢险报价应大于零')
                intermediary_price.theft_insurance_price = theft_insurance_price
            except:
                raise ParameterError('盗抢险报价请输入数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'盗抢险报价')
    else:
        intermediary_price.theft_insurance_price = 0
        
    #   乘客险
    passenger_insurance_price = request.POST.get('passenger_insurance_price', '')
    if   jdclbx_set.passenger_insurance != 0:
        if passenger_insurance_price:
            try:
                passenger_insurance_price = int(float(passenger_insurance_price)*100)
                if passenger_insurance_price <=0:
                    raise ParameterError(str(company_set.simple_name)+'乘客险报价应大于零')
                intermediary_price.passenger_insurance_price = passenger_insurance_price
            except:
                raise ParameterError('乘客险报价请输入数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'乘客险报价')
    else:
        intermediary_price.passenger_insurance_price = 0
        
    #不计免赔险
    iop_insurance_price = request.POST.get('iop_insurance_price', '')
    if   jdclbx_set.iop_insurance == True:
        if iop_insurance_price:
            try:
                iop_insurance_price = int(float(iop_insurance_price)*100)
                if iop_insurance_price <=0:
                    raise ParameterError (str(company_set.simple_name)+'不计免赔险报价应大于零')
                intermediary_price.iop_insurance_price = iop_insurance_price
            except Exception as e:
                raise ParameterError (str(e))
#                 raise ParameterError('不计免赔险报价请输入数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'不计免赔险报价')
    else:
        intermediary_price.iop_insurance_price = 0
    
    #自燃损失
    autoignition_insurance_price = request.POST.get('autoignition_insurance_price', '')
    if   jdclbx_set.autoignition_insurance == True:
        if autoignition_insurance_price:
            try:
                autoignition_insurance_price = int(float(autoignition_insurance_price)*100)
                if autoignition_insurance_price <=0:
                    raise ParameterError(str(company_set.simple_name)+'自燃损失险报价应大于零')
                intermediary_price.autoignition_insurance_price = autoignition_insurance_price
            except:
                raise ParameterError('自燃损失险报价请输入数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'自燃损失险报价')
    else:
        intermediary_price.autoignition_insurance_price = 0
    #涉水险
    wading_insurance_price = request.POST.get('wading_insurance_price', '')
    if   jdclbx_set.wading_insurance == True:
        if wading_insurance_price:
            try:
                wading_insurance_price = int(float(wading_insurance_price)*100)
                if wading_insurance_price <=0:
                    raise ParameterError(str(company_set.simple_name)+'涉水险报价应大于零')
                intermediary_price.wading_insurance_price = wading_insurance_price
            except:
                raise ParameterError('涉水险报价请输入数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'涉水险报价')
    else:
        intermediary_price.wading_insurance_price = 0
        
    #划痕险
    scratch_insurance_price = request.POST.get('scratch_insurance_price', '')
    if   jdclbx_set.scratch_insurance != 0:
        if scratch_insurance_price:
            try:
                scratch_insurance_price = int(float(scratch_insurance_price)*100)
                if scratch_insurance_price <=0:
                    raise ParameterError(str(company_set.simple_name)+'划痕险报价应大于零')
                intermediary_price.scratch_insurance_price = scratch_insurance_price
            except:
                raise ParameterError('划痕险报价请输入数字')
        else:
            raise ParameterError('请输入'+str(company_set.simple_name)+'划痕险报价')
    else:
        intermediary_price.scratch_insurance_price = 0
        
    #商业险总价
    try:
        commercial_price1 = int(intermediary_price.third_insurance_price) + int(intermediary_price.damage_insurance_price) +int(intermediary_price.glass_insurance_price)
        commercial_price2 = int(intermediary_price.driver_insurance_price) + int(intermediary_price.passenger_insurance_price) +int(intermediary_price.theft_insurance_price)
        commercial_price3 = int(intermediary_price.iop_insurance_price) + int(intermediary_price.autoignition_insurance_price) +int(intermediary_price.wading_insurance_price)+int(intermediary_price.scratch_insurance_price)
        commercial_price4 = commercial_price1 +commercial_price2 +commercial_price3
    except:
        raise ParameterError(str(company_set.simple_name)+'商业险总报价计算错误，请稍后再试')
    intermediary_price.commercial_price = commercial_price4
    
    #订单总价
    try:
        intermediary_price.order_price_all = intermediary_price.commercial_price + intermediary_price.liability_price + intermediary_price.vehicle_vessel_price
    except:
        raise ParameterError(str(company_set.simple_name)+'订单总报价计算错误，请稍后再试')  
    
    #订单不包含手续费的总价
    try:
        liability_price1=intermediary_price.liability_price  *(100 -  intermediary_price.liability_process_price)/100
        #vehicle_vessel_price1=intermediary_price.vehicle_vessel_price  *(100 - intermediary_price.vehicle_vessel_process_price)/100
        vehicle_vessel_price1=intermediary_price.vehicle_vessel_price  
        commercial_price1=intermediary_price.commercial_price  *(100 -  intermediary_price.commercial_process_price)/100
        
        intermediary_price.order_price_no_process = int(round(liability_price1+vehicle_vessel_price1 +commercial_price1))
    except:
        raise ParameterError(str(company_set.simple_name)+'订单不包含手续费部分报价出错，请稍后再试')  
    
    #订单包含利润点给用户呈现部分
    try:
        a=intermediary_price.order_price_all
        b=intermediary_price.insurance_intermediary.intermediary_profit_point/100
        #利润点
        #交强险利润
        if intermediary_price.liability_process_price>intermediary_price.insurance_intermediary.intermediary_profit_point:
            liability_profit_point1 = intermediary_price.liability_price * intermediary_price.insurance_intermediary.intermediary_profit_point/100
        else:
            liability_profit_point1 = intermediary_price.liability_price * intermediary_price.liability_process_price/100
        #商业险利润
        if intermediary_price.commercial_process_price>intermediary_price.insurance_intermediary.intermediary_profit_point:
            commercial_profit_point1 = intermediary_price.commercial_price * intermediary_price.insurance_intermediary.intermediary_profit_point/100
        else:
            commercial_profit_point1 = intermediary_price.commercial_price * intermediary_price.commercial_process_price/100
#         profit_point = intermediary_price.order_price_all * intermediary_price.insurance_intermediary.intermediary_profit_point/100
        order_price_add_profit =int(round (intermediary_price.order_price_no_process + commercial_profit_point1 + liability_profit_point1))
        intermediary_price.order_price_add_profit = order_price_add_profit
    except:
        raise ParameterError(str(company_set.simple_name)+'订单总报价计算错误，请稍后再试。') 
    
    #保存订单中介手续费比例
    try:
        intermediary_price.intermediary_profit_point =intermediary_price.insurance_intermediary.intermediary_profit_point
    except:
        raise ParameterError(str(company_set.simple_name)+'订单信息保存出错请稍后再试') 

    
    return intermediary_price

#中介报价（单个公司）
@login_required
def cos_intermediary_price(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    jdclbx_id=jdclbx_id
    try:
        test_user =request.user
        intermediary_people = IntermediaryPeople.objects(user = test_user).first()
        data['intermediary_name'] = intermediary_people.intermediary.intermediary_name
    except:
        request.session['message'] = '未获取登陆中介人员身份信息，请稍后重试。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()
        data['jdclbx_set'] = jdclbx_set
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    if jdclbx_set:
        #确定报价信息唯一性
        #报价公司
        bj_company_id = request.POST.get('bj_company_id', '')#报价公司
        if bj_company_id:
            try:
                company_set = InsuranceCompany.objects(id =bj_company_id ).first()
                print(company_set.simple_name)
                if not company_set:
                    request.session['price_message'] = '网络问题，未获取到当前报价公司信息!'
                    return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
            except:
                request.session['price_message'] ='网络问题未获取到当前报价公司信息。'
                return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
        else:
            request.session['price_message'] ='网络问题未获取到当前报价公司信息'
            return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
        #登陆中介
        try:
            test_user =request.user
            intermediary_people_set = IntermediaryPeople.objects(user = test_user).first()
        except:
            request.session['message'] = '未获取登陆中介人员身份信息，请稍后重试。'
            return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
        
        #确定中间表状态是编辑状态还是创建状态
        try:
            order_count =IntermediaryPrice.objects(insurance_intermediary = intermediary_people_set.intermediary,company = company_set,order =jdclbx_set ).count()
        except:
            request.session['price_message'] = '网络不稳定。'
            HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
        if order_count == 0:
            intermediary_price = IntermediaryPrice()
        else:
            intermediary_price =IntermediaryPrice.objects(insurance_intermediary = intermediary_people_set.intermediary,company = company_set,order =jdclbx_set ).first()
        
        try:
            #intermediary_price = IntermediaryPrice()
            intermediary_price = verify_intermediary_price(request, jdclbx_set,intermediary_price)
            intermediary_price.save()
        except CustomError as e:
            request.session['price_message'] =  e.message
            HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
        except ParameterError as e:
            request.session['price_message'] = e.message
            HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
        except Exception as e:
            print(traceback.format_exc())
            request.session['price_message'] = str(e)
            HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
#         data['jdclbx_set'] = jdclbx_set
#         print(data)
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))


#更改订单状态（从询价中变询价完成的未确认状态）
#确认报价（验证）
@login_required
def verify_jdclbx_state(request, order):

    order_state = ""
    intermediary_list=order.intermediary_list
    if intermediary_list:
        for intermediary_detail  in intermediary_list:
            try:
                intermediary_price_set =IntermediaryPrice.objects(insurance_intermediary  = intermediary_detail ,order =order ).first()
            except:
                intermediary_price_set=''
            if intermediary_price_set:
                a=intermediary_price_set.state
                if intermediary_price_set.state == 'verify':
                    order_state='verify'
                    break
                elif intermediary_price_set.state == 'done':
                    order_state ='done'
                else:
                    order_state = ""
                    print('询价订单信息错误，请检查')
                    break
            else:
                order_state = ""
                break
    if order_state =='done':
        order.state='wait'
        order.save()
        print('询价完成，请检查')
    return "已检查订单状态"







#确认报价
@login_required
def confirm_intermediary_price(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    jdclbx_id=jdclbx_id
    try:
        test_user =request.user
        intermediary_people = IntermediaryPeople.objects(user = test_user).first()
        data['intermediary_name'] = intermediary_people.intermediary.intermediary_name
    except:
        request.session['message'] = '未获取登陆中介人员身份信息，请稍后重试。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    #company_list = intermediary_people.intermediary.intermediary_company_list#中介下所有的保险公司


    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()#中介报价的订单
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    if jdclbx_set:
        data['jdclbx_set'] = jdclbx_set
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    
    #2017添加中介下保险公司是否承保该订单的判断
    company_list1 = intermediary_people.intermediary.intermediary_company_list#中介下所有的保险公司
    company_list=[]#筛选后可以承保的保险公司
    for company in company_list1:
        try:
             intermediary_rate_set = IntermediaryRate.objects(intermediary=intermediary_people.intermediary , company=company,jdclbx_order=jdclbx_set).first()
             if intermediary_rate_set:
                 if intermediary_rate_set.company_state==True:
                     company_list.append(company)
        except:
            print('中介渠道下关联公司出现调整')
#     data["company_list"] = company_list
#     
    test_price=0
    company_simple_name=""
    for company_set in company_list:
        try:
            count_test =IntermediaryPrice.objects(insurance_intermediary = intermediary_people.intermediary,order =jdclbx_set,company = company_set ).count()
        except:
            count_test =0
        if count_test == 0:
            test_price=1
            company_simple_name=company_set.simple_name
            break
    if test_price==1:
        request.session['price_message'] = str(company_simple_name)+'未报价'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
    else:
        try:
             intermediary_price_list =IntermediaryPrice.objects(insurance_intermediary = intermediary_people.intermediary,order =jdclbx_set )
             for intermediary_price1 in intermediary_price_list:
                 intermediary_price1.state='done'
                 intermediary_price1.save()
        except Exception as e:
            request.session['price_message'] = '更改报价状态出错，出错信息：'+str(e)
            return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
        
 
    request.session['price_message'] = '提交报价成功，报价不可修改'
    #验证是否询价完成
    try:
        jdclbx_set.state='wait'
        jdclbx_set.save()
    except Exception as e:
        request.session['price_message'] = '更改订单状态出错，出错信息：'+str(e)
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
    #微信通知
    try:
        touser = jdclbx_set.client.wx_id
        content='您的' +str(jdclbx_set.plate_number) + '号车辆保险询价有新报价信息，请您在运至宝公众号中，点击我的订单-车险订单，查看报价信息'
        send_wx_message(touser,content)
    except Exception as e:
        request.session['price_message'] = '网络不稳定，通知用户微信信息发送失败：'+str(e)
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
        
    
#     a=verify_jdclbx_state(request,jdclbx_set)
#     print(a)
    return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))


#－－－－－－－－－－－－－－－－－－－－－－－－－－    中介询价 已投保订单列表      －－－－－－－－－－－－－－－－－－－－－－－－－
    
@login_required
#@AdminRequired
def confirm_jdclbx_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    try:
        test_user =request.user
        intermediary_people = IntermediaryPeople.objects(user = test_user).first()
        data['intermediary_name'] = intermediary_people.intermediary.intermediary_name
    except:
        request.session['message'] = '未获取登陆中介人员身份信息，请稍后重试。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    if request.method == 'POST':
        request_tool.save_log()
        pay_state = request_tool.get_parameter("pay_state")
        id_client = request_tool.get_parameter("client_sign")
        search_keyword = request.POST.get('search_keyword', '')
        get_parameter = "?pay_state={0}&search_keyword={1}&id_client={2}".format(pay_state, search_keyword, id_client)
        return HttpResponseRedirect(reverse('cos:confirm_jdclbx_list', args=[page_index, ])+ get_parameter )

    elif request.method == 'GET':
        client_set = Client.objects().filter(user_type__ne='registered')
        data['clients'] = client_set
        request_tool.check_message(data)
        data["get_data"] = request.GET
        order_set = InquiryInfo.objects(insurance_intermediary= intermediary_people.intermediary ).filter(Q(state = 'paid') | Q(state = 'done') ).order_by('-create_time')
        order_set = request_tool.jdcbx_filter(order_set=order_set) 
        count = order_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_order'] = paging['page_index']
        order_set = order_set[paging['start_item']:paging['end_item']]

        data['orders'] = order_set
        data['paging'] = paging
        return render_to_response('cos/order/confirm_jdclbx_list.html', data, context)



@login_required
def confirm_jdclbx_detail(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    jdclbx_id=jdclbx_id
    try:
        test_user =request.user
        intermediary_people = IntermediaryPeople.objects(user = test_user).first()
        data['intermediary_name'] = intermediary_people.intermediary.intermediary_name
    except:
        request.session['message'] = '未获取登陆中介人员身份信息，请稍后重试。'
        return HttpResponseRedirect(reverse('cos:confirm_jdclbx_list', args=[page_index, ]))
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('cos:confirm_jdclbx_list', args=[page_index, ]))
    if jdclbx_set:
        data['jdclbx_set'] = jdclbx_set
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('cos:confirm_jdclbx_list', args=[page_index, ]))
    try:
        intermediary_price_set =IntermediaryPrice.objects(insurance_intermediary= intermediary_people.intermediary,order =jdclbx_set,company = jdclbx_set.company ).first()
        #count = intermediary_price_set.count()
        data["intermediary_price_detail"]=intermediary_price_set
    except:
        data["intermediary_price_set"]=''
    #添加特别约定回显
    if jdclbx_set.special_agreement:
        if len(jdclbx_set.special_agreement)>40:
            data['special_agreement'] = jdclbx_set.special_agreement[0:39]+'……'
        else:
            data['special_agreement'] = jdclbx_set.special_agreement
    return render_to_response('cos/order/confirm_jdclbx_detail_new.html', data, context)  



#添加图片未完成
#注意报价时保存给中介的价格
# 添加保单号
@login_required
def add_jdclbx_pic(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    bms_tools = DocumentBmsTools(request)
    #订单信息
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()#中介报价的订单
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[1, ]))
    #中介人员信息
    try:
        test_user =request.user
        intermediary_people = IntermediaryPeople.objects(user = test_user).first()
        data['intermediary_name'] = intermediary_people.intermediary.intermediary_name
    except:
        request.session['message'] = '未获取登陆中介人员身份信息，请稍后重试。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    #中介报价信息
    try:
        intermediary_price = IntermediaryPrice.objects(insurance_intermediary= intermediary_people.intermediary, order = jdclbx_set ).first()
    except:
        request.session['message'] = '未获取报价订单信息，请稍后再试'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    if not intermediary_price:
        request.session['message'] = '未获取报价订单信息，请稍后再试。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[page_index, ]))
    
    if jdclbx_set.state != 'paid':
        request.session['message'] = '要增加的订单状态不正确。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[1, ]))
    if request.method == 'POST':
        liability_id = request.POST.get('liability_id', '')
        commercial_id = request.POST.get('commercial_id', '')
        liability_type = request.POST.get('liability_type', '')
        if liability_type == 'web_url':
            liability_image_list = request.POST.get('liability_image', '')
        else:
            liability_image_list = request.FILES.getlist('liability_image', '')
        commercial_type = request.POST.get('commercial_type', '')
        if commercial_type == 'web_url':
            commercial_image_list = request.POST.get('commercial_image', '')
        else:
            commercial_image_list = request.FILES.getlist('commercial_image', '')
        
        #交强险投保
        if jdclbx_set.liability_state ==True:
            #交强险保单号
            if liability_id:
                jdclbx_set.liability_id = liability_id
            else:
                request.session['message'] ='请输入交强险保单号'  
                return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
            if liability_type == 'picture':
                #交强险保单图片
                image_tool = ImageTools()
                jd_liability_image_url=[]
                if liability_image_list:
                    for liability_image in liability_image_list:
                        try:
                            liability_image_url = image_tool.save(request_file=liability_image, file_folder=ImageFolderType.jdclbx, old_file='')
                            if liability_image_url:
                                jd_liability_image_url.append(liability_image_url)
                            else:
                                request.session['message'] ='交强险保单图片上传失败'  
                                return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
                        except:
                            request.session['message'] ='保存交强险保单图片失败'
                            return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
                    jdclbx_set.liability_image_list = jd_liability_image_url
                    jdclbx_set.liability_up_state = liability_type
                else:
                    request.session['message'] = '请上传交强险保单图片'
                    return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
            elif liability_type == 'pdf':
                if liability_image_list:
                    #交强险文档
                    jd_liability_document_url=[]
                    for jd_liability_image in liability_image_list:
                        document_tools = DocumentTools()
                        try:
                            file_url = document_tools.save(request_file=jd_liability_image, file_folder=DocumentFolderType.jdclbx, old_file='')
                        except Exception as e:
                            request.session['message'] =str(e)+'保存交强险保单文件失败'
                            return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
                        jd_liability_document_url.append(file_url)
                    if not jd_liability_document_url:
                        request.session['message'] ='生成保存交强险保单文件地址失败'
                        return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
                    jdclbx_set.liability_image_list = jd_liability_document_url
                    jdclbx_set.liability_up_state = liability_type
                else:
                    request.session['message'] = '请上传交强险保单文件'
                    return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
            elif liability_type == 'web_url':
                if liability_image_list:
                    liability_web_url = []
                    liability_image_list = str(liability_image_list)
                    liability_web_url.append(liability_image_list)
                    jdclbx_set.liability_image_list = liability_web_url
                    jdclbx_set.liability_up_state = liability_type
                else:
                    request.session['message'] = '请填写交强险保单下载链接'
                    return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
            else:
                 request.session['message'] = '请选择交强险保单上传方式'
                 return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))   
                
         
        if intermediary_price.commercial_price >0:
            #商业险保单号
            if commercial_id:
                jdclbx_set.commercial_id = commercial_id
            else:
                request.session['message'] ='请输入交强险保单号'    
                return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
            if commercial_type == 'picture':
                #交强险保单图片
                image_tool = ImageTools()
                jd_commercial_image_url=[]
                if commercial_image_list:
                    for commercial_image in commercial_image_list:
                        try:
                            commercial_image_url = image_tool.save(request_file=commercial_image, file_folder=ImageFolderType.jdclbx, old_file='')
                            if commercial_image_url:
                                jd_commercial_image_url.append(commercial_image_url)
                            else:
                                request.session['message'] ='商业险保单图片上传失败'  
                                return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
                        except:
                            request.session['message'] ='保存商业险保单图片失败'
                            return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
                    jdclbx_set.commercial_image_list = jd_commercial_image_url
                    jdclbx_set.commercial_up_state = commercial_type
                else:
                    request.session['message'] = '请上传商业险保单图片'
                    return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
            elif commercial_type == 'pdf':
                if commercial_image_list:
                    #交强险文档
                    jd_commercial_document_url=[]
                    for commercial_image_detail in commercial_image_list:
                        document_tools = DocumentTools()
                        try:
                            file_url = document_tools.save(request_file=commercial_image_detail, file_folder=DocumentFolderType.jdclbx, old_file='')
                        except:
                            request.session['message'] ='保存商业险保单文件失败'
                            return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
                        jd_commercial_document_url.append(file_url)
                    if not jd_commercial_document_url:
                        request.session['message'] ='生成保存商业险保单文件地址失败'
                        return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
                    jdclbx_set.commercial_image_list = jd_commercial_document_url
                    jdclbx_set.commercial_up_state = commercial_type
                else:
                    request.session['message'] = '请上传商业险保单文件'
                    return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
            elif commercial_type == 'web_url':
                if commercial_image_list:
                    commercial_web_url = []
                    commercial_image_list = str(commercial_image_list)
                    commercial_web_url.append(commercial_image_list)
                    jdclbx_set.commercial_image_list = commercial_web_url
                    jdclbx_set.commercial_up_state = commercial_type
                else:
                    request.session['message'] = '请填写商业险保单下载链接'
                    return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
            else:
                 request.session['message'] = '请选择商业险保单上传方式'
                 return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))   

        #保存订单
        try:
            jdclbx_set.save()
            jdclbx_set.state = 'done'
            jdclbx_set.save()
            request.session['message'] = '上传保单成功'
        except Exception as e:
            request.session['message'] = str(e)
            return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
        
#         #2017-09-04添加动态增加
#         if jdclbx_set.state == 'done':
#             print('自动同步车辆')
#             try:
#                 create_car_count = CarCertificate.objects(plate_number = jdclbx_set.plate_number,client=jdclbx_set.client).count()
#                 if create_car_count == 0:
#                     create_car = CarCertificate()
#                     create_car.client=jdclbx_set.client
#                     create_car.plate_number=jdclbx_set.plate_number
#                     create_car.plate_image_left.append( jdclbx_set.plate_image_left )
#                     create_car.plate_image_left.append( jdclbx_set.plate_image_right )
#                     create_car.state='success'
#                     create_car.car_state='1'
#                     create_car.certificate_time=datetime.now
# #                     create_car.ddd=jdclbx_set.
# #                     create_car.ddd=jdclbx_set.
#                     create_car.save()
#             except CustomError as e:
#                 request.session['message'] ='上传保单成功。'
            
        return HttpResponseRedirect(reverse('cos:confirm_jdclbx_detail', args=[jdclbx_set.id, ]))
    else:
        return HttpResponseRedirect(reverse('cos:confirm_jdclbx_list', args=[1, ]))





#拒保
@login_required
def jdclbx_refuse_company(request, jdclbx_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    jdclbx_id=jdclbx_id
    #中介
    try:
        test_user =request.user
        intermediary_people = IntermediaryPeople.objects(user = test_user).first()
        data['intermediary_name'] = intermediary_people.intermediary.intermediary_name
    except:
        request.session['message'] = '未获取登陆中介人员身份信息，请稍后重试。'
        return HttpResponseRedirect(reverse('cos:confirm_jdclbx_list', args=[page_index, ]))
    # 订单
    try:
        jdclbx_set= InquiryInfo.objects(id=jdclbx_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('cos:confirm_jdclbx_list', args=[page_index, ]))
    if jdclbx_set:
        data['jdclbx_set'] = jdclbx_set
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('cos:confirm_jdclbx_list', args=[page_index, ]))
    #拒保公司
    company_id  = request.POST.get('company_id', '')
    if not company_id :
        request.session['price_message'] ='网络不稳定，未获取拒保公司信息。'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
    try :
        company_set = InsuranceCompany.objects( id =company_id ).first()
    except:
        request.session['price_message'] ='网络不稳定，未获取拒保公司信息'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
    #查看对应报价信息
    try:
        intermediary_rate_set =IntermediaryRate.objects(intermediary= intermediary_people.intermediary,jdclbx_order =jdclbx_set,company=company_set ).first()
    except:
        request.session['price_message'] = '网络不稳定，未获取拒保公司后台添加信息'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
    if intermediary_rate_set:
        try:
            intermediary_rate_set.company_state = False
            intermediary_rate_set.save()
            request.session['price_message'] =str(company_set.simple_name)+'成功拒保'
        except:
            request.session['price_message'] = '网络不稳定，该公司未成功拒保'
            return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
        #删除已有的报价信息
        try:
            test_intermediary_price = IntermediaryPrice.objects(order=jdclbx_set, insurance_intermediary= intermediary_people.intermediary,company=company_set)
            if test_intermediary_price.count()>0:
                for test_intermediary_detail in test_intermediary_price:
                    test_intermediary_detail.delete()
        except:
            request.session['price_message'] = '网络不稳定，拒保公司删除信息失败'
            return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))
            
                
    #检查该中介下是否有公司可承保
    try:
        intermediary_rate_list =IntermediaryRate.objects(intermediary= intermediary_people.intermediary,jdclbx_order =jdclbx_set )
    except:
        request.session['price_message'] ='网络不稳定，信息出错'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[1, ]))
    test_company_state = '0'
    for intermediary_rate_detail in intermediary_rate_list:
        if intermediary_rate_detail.company_state == True:
            test_company_state = '1'
    if test_company_state == '1':
        print('本单，该中介存在投保公司')
    else:
        #该中介不存在投保公司
        #删除报价信息
        try:
            intermediary_price_list=IntermediaryPrice.objects(order=jdclbx_set, insurance_intermediary= intermediary_people.intermediary)
            if intermediary_price_list:
                for intermediary_price_detail in intermediary_price_list:
                    intermediary_price_detail.delete()
        except:
            request.session['message'] = '删除报价信息出错'
            return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[1, ]))
        #删除手续费信息
        try:
            for intermediary_rate_detail in intermediary_rate_list:
                intermediary_rate_detail.delete()
        except:
            request.session['message'] = '删除订单后台信息出错'
            return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[1, ]))      
        #去除保险公司可看权限
        try:
            jdclbx_set.intermediary_list.remove(intermediary_people.intermediary)
            jdclbx_set.save()
        except:
            request.session['message'] =  '去除不可保订单信息失败'
            return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[1, ]))      
    if not jdclbx_set.intermediary_list:
        try:
            jdclbx_set.state= 'fail'  
            jdclbx_set.fail_reason = '没有中介可承保该订单已退回'
            jdclbx_set.save()
        except:
            request.session['message'] = '拒保成功'
            return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[1, ]))     
#     else:
        #验证是否询价完成
#         a=verify_jdclbx_state(request,jdclbx_set)
#         print(a) 
    if test_company_state != '1':
        request.session['message'] = '订单拒保成功'
        return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[1, ]))     
    return HttpResponseRedirect(reverse('cos:cos_jdclbx_detail', args=[jdclbx_id, ]))



#2017/11/03批量导入保单号（三种方式）
@login_required
# @AdminRequired
def import_insurance_new(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    search_keyword = request_tool.get_parameter('search_keyword', '')
    start_time = request.POST.get('start_time', '')
    request.session['start_time'] = start_time
    end_time = request.POST.get('end_time', '')
    request.session['end_time'] = end_time
    state = request_tool.get_parameter("state")
    pay_state = request_tool.get_parameter("pay_state")
    user_type = request_tool.get_parameter("user_type")
    id_client = request_tool.get_parameter("client_sign")
    request.session['search_keyword_order'] = search_keyword
    request.session['page_index_order'] = 1
    get_parameter = "?state={0}&pay_state={1}&user_type={2}&id_client={3}".format(state, pay_state, user_type, id_client)
    test_user =request.user
    claim = Claim.objects(user = test_user).first()
    claims_company = claim.company
    if request.method == 'POST':
        data['posted_data'] = request.POST
        #提取信息
        try:
            insurance_id = request_tool.get_parameter('insurance_id', '')#订单号
            if not insurance_id:
                request_tool.set_message("请填写保单号码")
                return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
            insurance_type = request_tool.get_parameter('insurance_type', '')#保单状态
            if insurance_type == 'web_url':
                insurance_image_list = request.POST.get('insurance_image', '')
            else:
                insurance_image_list = request.FILES.getlist('insurance_image', '')
            if not insurance_image_list:
                request_tool.set_message("请上传保单信息")
                return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
            #选择订单
            choose_order_list =request.REQUEST.getlist("choose_order")
            if len(choose_order_list)==0:
                 request_tool.set_message("您未选择导入保单的订单")
                 return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
        except Exception as e:
            request_tool.set_message("提取保单信息出错："+str(e))
            return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
        
        #存储保单信息
        insurance_image_list_detail=[]
         #保单图片
        if insurance_type == 'picture':
            try:
                image_tool = ImageTools()
                if insurance_image_list:
                    for insurance_image in insurance_image_list:
                        order_image_url = image_tool.save(request_file=insurance_image, file_folder=ImageFolderType.insurance, old_file='')
                        if not order_image_url:
                            request_tool.set_message(order.paper_id+'生成图片地址失败')
                            return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
                        else:
                            insurance_image_list_detail.append(order_image_url)
                else:
                    request_tool.set_message('导入失败，请填入保单图片')
                    return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
            except ParameterError as e:
                # 初始化错误信息
                request_tool.set_message(e.message)
                return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
        #pdf文件保存
        elif insurance_type == 'pdf':
                if insurance_image_list:
                    #交强险文档
                    liability_document_url=[]
                    for insurance_image in insurance_image_list:
                        document_tools = DocumentTools()
                        try:
                            file_url = document_tools.save(request_file=insurance_image, file_folder=DocumentFolderType.order, old_file='')
                        except Exception as e:
                            request_tool.set_message(str(e)+'保单文件上传失败')
                            return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
                        liability_document_url.append(file_url)
                    if not liability_document_url:
                        request_tool.set_message('生成保单文件地址失败')
                        return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
                    else:
                        insurance_image_list_detail=liability_document_url
                else:
                    request_tool.set_message('请上传保单文件')
                    return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
        elif insurance_type == 'web_url':
                if insurance_image_list:
                    insurance_web_url = []
                    insurance_image_list = str(insurance_image_list)
                    insurance_web_url.append(insurance_image_list)
                    insurance_image_list_detail = insurance_web_url
                else:
                    request.session['message'] = '请填写保单下载链接'
                    return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)
                
                
        #将保单信息批量导入订单中
        input_count=0
        len_choose_order = len(choose_order_list)
        wrong_order=''
        for  choose_order_id  in choose_order_list:
            try:
                order = Ordering.objects(id=choose_order_id).first()
                
            except:
                pass
            
            if not order:
                wrong_order = wrong_order + str(choose_order_id) +'、'
            else:
                if order.state == 'paid':
                    try:
                        order.insurance_image_list=insurance_image_list_detail#保单详情内容
                        order.insurance_id = insurance_id#保存订单号
                        order.insurance_up_state = insurance_type#保存上传保单类别
                        order.picture_upload_path = 'yzb'
                        order.state = 'done'
                        order.save()
                        input_count =input_count+1
                    except:
                        wrong_order = wrong_order + str(choose_order_id) +'、'
        
        #存储保单信息结束
        if input_count != int(len_choose_order):
            request_tool.set_message("导入部分保单成功，订单id为" + wrong_order +'的订单导入保单失败，请联系管理员')
        else:
            request_tool.set_message("选中的订单，全部导入保单成功")
        return HttpResponseRedirect(reverse('cos:order_list', args=[1, ]) + get_parameter)




