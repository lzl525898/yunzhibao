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
from wss.views_sendmessage import  send_wx_message
@login_required
@AdminRequired
def certificate_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_certificate'] = search_keyword
        request.session['page_index_certificate'] = 1
        state = request_tool.get_parameter("state")
        certification_goal = request_tool.get_parameter("certification_goal")
        get_parameter = "?state={0}&certification_goal={1}".format(state, certification_goal)
        return HttpResponseRedirect(reverse('bms:certificate_list', args=[1, ]) + get_parameter)
        # return HttpResponseRedirect(reverse('bms:certificate_list', args=[1, ]))

    elif request.method == 'GET':
        # message = request.session.get('message', '')
        message = request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_certificate', '')
        certificate_set = Certificate.objects()
        certificate_set = request_tool.certificate_filter(certificate_set=certificate_set, keyword=search_keyword)
        count = certificate_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_certificate'] = paging['page_index']
        certificate_set = certificate_set[paging['start_item']:paging['end_item']]
        data['certificates'] = certificate_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/user/certificate_list.html', data, context)

@login_required
@AdminRequired
def certificate_detail(request, certificate_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_certificate', '1')
    data['page_index'] = page_index
    data['certificate_id'] = certificate_id
    certificate = Certificate.objects(id=certificate_id).first()
    if certificate:
        data['certificate'] = certificate
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:certificate_list', args=[certificate_id, page_index, ]))
    return render_to_response('bms/user/certificate_detail.html', data, context)

@login_required
@AdminRequired
def certificate_result(request, certificate_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.save_log()
    certificate = Certificate.objects(id=certificate_id).first()
    client = Client.objects(id=certificate.client.id).first()
    result = request.POST.get('result', '')
    try:
        if result == 'on':
            certificate.state = 'success'
            client.user_type = certificate.user_type
            client.user_classify = certificate.user_classify
            client.name = certificate.name
            client.national_id = certificate.national_id
            client.national_image = certificate.national_image
            client.driver_id = certificate.driver_id
            client.driver_image = certificate.driver_image
            client.plate_number = certificate.plate_number
            client.plate_image = certificate.plate_image
            client.transportation_license_id = certificate.transportation_license_id
            client.transportation_image = certificate.transportation_image
            client.operating_permit_id = certificate.operating_permit_id
            client.operating_permit_image = certificate.operating_permit_image
            client.business_license_id = certificate.business_license_id
            client.business_license_image = certificate.business_license_image
           # touser = "oYXlSwfedYTw0OtzfRy2SYpPrNE8"     
            touser = client.wx_id
            content = "恭喜，您已认证成功！成为运之宝的认证用户。立即开启您的物流保险之旅！我们有专业的服务团队在此恭候。"
            send_wx_message(touser,content);
            
        else:
            failed_reason = request.POST.get('fail', '')
            note = request.POST.get('note', '')
            if failed_reason:
                certificate.failed_reason = failed_reason
            else:
                data['message'] = "驳回理由不能为空"
                data['certificate'] = certificate
                return render_to_response('bms/certificate/certificate_detail.html', data, context)
            certificate.note = note
            certificate.state = 'fail'
    except:
        data['certificate'] = certificate
        return render_to_response('bms/certificate/certificate_detail.html', data, context)
    certificate.certificate_time = datetime.now()
    certificate.save()
    client.save()
    return HttpResponseRedirect(reverse('bms:certificate_detail', args=[certificate_id, ]))

