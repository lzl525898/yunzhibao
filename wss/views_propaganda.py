from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from wss.tools import *
from common.models import *
from common.decorators import ExceptionRequired
from common.decorators import AdminRequired
#js_ticket
from wss.views_ticket import *
# from wss.tools_wechat import
from django.contrib.auth.decorators import login_required
import datetime
from common.driver_dict import *
from common.tools import *
from bms.views_campaign import CountCarAge


#物流公司
@JSAPI_TICKET_Required
def transport_list(request):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    logistics_set = LogisticsCompany.objects()
    if request.method == 'POST':
        search_keyword = request.POST.get('search_keyword', '')
        if search_keyword :
            data['search'] = search_keyword
            logistics_set = request_tool.wx_logistics_filter(logistics_set=logistics_set, keyword=search_keyword)
    else:
            data['search'] = ""
    data['logisticss'] = logistics_set.order_by('-priority')
    return render_to_response('wss/propaganda/transport_list.html', data, context)

@JSAPI_TICKET_Required
#物流详情
def transport_detail(request, logistics_id):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    list = []
    logistics = LogisticsCompany.objects(id=logistics_id).first()
    if logistics:
        data['logistics'] = logistics
    else:
        request.session['message'] = '未找到对应数据'
    return render_to_response('wss/propaganda/transport_detail.html', data, context)


#物流管理系统
@JSAPI_TICKET_Required
def manager_list(request):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/propaganda/manager_list.html', data, context)

@JSAPI_TICKET_Required
def manager_detail(request):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    return render_to_response('wss/propaganda/manager_detail.html', data, context)


#律师
@JSAPI_TICKET_Required
def lawyer_list(request):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    request_tool = RequestTools(request)
    campaign_lawyer_set = CampaignLawyer.objects()
    if request.method == 'POST':
        search_keyword = request.POST.get('search_keyword', '')
        if search_keyword :
            data['search'] = search_keyword
            campaign_lawyer_set = request_tool.lawyer_filter(campaign_lawyer_set=campaign_lawyer_set, keyword=search_keyword)
    else:
            data['search'] = ""
    
    data['campaign_lawyers'] = campaign_lawyer_set.order_by('-priority')
    return render_to_response('wss/propaganda/lawyer_list.html', data, context)

@JSAPI_TICKET_Required
def lawyer_detail(request, lawyer_id):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    campaign_lawyer = CampaignLawyer.objects(id=lawyer_id).first()
    data['campaign_lawyer'] = campaign_lawyer
    return render_to_response('wss/propaganda/lawyer_detail.html', data, context)

#司机
@JSAPI_TICKET_Required
def driver_list(request):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    data['car_type'] = Trucker.Driver_Car_Type
    data['car_length'] = Trucker.Driver_Car_Length
    request_tool = RequestTools(request)
    if request.method == 'POST':
        search_keyword = request.POST.get('search_keyword', '')
        car_type = request.POST.get('car_type', '')
        car_length = request.POST.get('car_length', '')
        trucker_set = Trucker.objects()
        if search_keyword or car_type or car_length:
            trucker_set = request_tool.wx_driver_filter(trucker_set=trucker_set, keyword=search_keyword,car_type=car_type,car_length=car_length)
        data['truckers'] = trucker_set.order_by('-priority')
        return render_to_response('wss/propaganda/driver_list.html', data, context)
    else:
        trucker_set = Trucker.objects()
        data['truckers'] = trucker_set.order_by('-priority')

        return render_to_response('wss/propaganda/driver_list.html', data, context)

@JSAPI_TICKET_Required
def driver_detail(request,driver_id):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    trucker = Trucker.objects(id=driver_id).first()
    if trucker:
        for k,v in DriverCarType:
            if int(k) == int(trucker.car_type):
                data['car_type_text']  = v
        for k,v in DriverCarLength:
            if int(k) == int(trucker.car_length):
                data['car_length_text']  = v       
        data['trucker'] = trucker
        car_age=CountCarAge(trucker.car_init_date)
        data['car_age'] = car_age
    else:
        request.session['message'] = '未找到对应数据'
    return render_to_response('wss/propaganda/driver_detail.html', data, context)