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

from wss.views_sendmessage import  send_wx_message

#－－－－－－－－－－－－－－－－－－－－－－－－－－     保额统计      －－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def insurance_amount(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_head_company'] = search_keyword
        request.session['page_index_head_company'] = 1
        # return HttpResponseRedirect(reverse('bms:head_company_list', args=[1, ]))
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:head_company_list', args=[1, ]) + get_parameter)

    elif request.method == 'GET':
        return render_to_response('bms/statistics/insurance_amount.html', data, context)