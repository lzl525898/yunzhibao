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
from common.tools import RequestTools
from bms.tools import DocumentBmsTools
from django.shortcuts import render_to_response, HttpResponse
import traceback


#－－－－－－－－－－－－－－－－－－－－－－－－－－     赔案      －－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def compensate_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_compensate'] = search_keyword
        request.session['page_index_compensate'] = 1
        state = request_tool.get_parameter("state")
        compensate_state = request_tool.get_parameter("compensate_state")
        get_parameter = "?state={0}&compensate_state={1}".format(state, compensate_state)
        return HttpResponseRedirect(reverse('bms:compensate_list', args=[1, ]) + get_parameter)

    elif request.method == 'GET':
        message = request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_compensate', '')
        compensate_set = Compensate.objects()
        compensate_set = request_tool.compensate_filter(compensate_set=compensate_set, keyword=search_keyword)
        count = compensate_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_compensate'] = paging['page_index']
        compensate_set = compensate_set[paging['start_item']:paging['end_item']]
        data['compensates'] = compensate_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/compensate/compensate_list.html', data, context)

@login_required
@AdminRequired
def compensate_detail(request, compensate_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_compensate', '1')
    data['page_index'] = page_index
    compensate = Compensate.objects(id=compensate_id).first()
    if compensate:
        data['compensate'] = compensate
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:compensate_list', args=[page_index, ]))
    return render_to_response('bms/compensate/compensate_detail.html', data, context)


@login_required
@AdminRequired
def compensate_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_compensate', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    company_set = InsuranceCompany.objects(is_hidden=False)
    client_set = Client.objects()
    product_set = InsuranceProducts.objects()
    insurance_type = INSURANCE_TYPE
    data['companys'] = company_set
    data['clients'] = client_set
    data['insurance_types'] = insurance_type
    data['insurance_products'] = product_set
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            compensate = Compensate()
            compensate = bms_tools.validation_compensate(compensate)
            if request.POST.get('active', '') == 'show':
                compensate.is_hidden = False
            else:
                compensate.is_hidden = True
            compensate.save()
            request.session['message'] = '创建成功'
            return HttpResponseRedirect(reverse('bms:compensate_detail', args=[compensate.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
        return render_to_response('bms/compensate/compensate_create.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/compensate/compensate_create.html', data, context)


@login_required
@AdminRequired
def compensate_edit(request, compensate_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_compensate', '1')
    data['page_index'] = page_index
    company_set = InsuranceCompany.objects(is_hidden=False)
    client_set = Client.objects()
    product_set = InsuranceProducts.objects()
    insurance_type = INSURANCE_TYPE
    data['companys'] = company_set
    data['clients'] = client_set
    data['insurance_types'] = insurance_type
    data['insurance_products'] = product_set
    compensate = Compensate.objects(id=compensate_id).first()
    if compensate:
        data['compensate'] = compensate
    else:
        request.session['message'] = '未找到对应的保险公司'
        return HttpResponseRedirect(reverse('bms:compensate_detail', args=[compensate_id, ]))
    if request.method == 'POST':
        try:
            compensate = bms_tools.validation_compensate(compensate)
            if request.POST.get('active', '') == 'show':
                compensate.is_hidden = False
            else:
                compensate.is_hidden = True
            compensate.save()
            request.session['message'] = '编辑成功'
            return HttpResponseRedirect(reverse('bms:compensate_detail', args=[compensate.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/compensate/compensate_edit.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/compensate/compensate_edit.html', data, context)


@login_required
@AdminRequired
def compensate_pay(request, compensate_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_compensate', '1')
    data['page_index'] = page_index
    compensate = Compensate.objects(id=compensate_id).first()
    if compensate:
        data['compensate'] = compensate
    else:
        request.session['message'] = '未找到对应的保险公司'
        return HttpResponseRedirect(reverse('bms:compensate_detail', args=[compensate_id, ]))
    if request.method == 'POST':
        try:
            pay_compensate = bms_tools.get_parameter('pay_compensate')
            if pay_compensate:
                compensate.state = 'paid'
                compensate.pay_price = pay_compensate
                compensate.save()
            else:
                data['message'] = '货物价值不能为空'
                return render_to_response('bms/compensate/compensate_detail.html', data, context)
            return render_to_response('bms/compensate/compensate_detail.html', data, context)
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/compensate/compensate_detail.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/compensate/compensate_detail.html', data, context)

#
#
#
# # 屏蔽保单
# @login_required
# @AdminRequired
# def policy_hidden(request, policy_id):
#     context = RequestContext(request)
#     data = {}
#     request_tools = RequestTools(request)
#     request_tools.check_message(data)
#     page_index = request.session.get('page_index_policy', '1')
#     data['page_index'] = page_index
#     print(policy_id)
#     policy = Policy.objects(id=policy_id).first()
#     if policy:
#         if policy.is_hidden:
#             policy.is_hidden = False
#         else:
#             policy.is_hidden = True
#         policy.save()
#     else:
#         request.session['message_policy'] = '未找到对应的保单'
#         return HttpResponseRedirect(reverse('bms:policy_detail', args=[policy_id, ]))
#     return HttpResponseRedirect(reverse('bms:policy_detail', args=[policy_id, ]))
