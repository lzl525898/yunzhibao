from common.models import *
from django.contrib.auth.decorators import login_required
from common.decorators import AdminRequired
from common.decorators import SuperAdminRequired
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from common.tools import *
from common.tools import RequestTools
from bms.tools import DocumentBmsTools
from django.shortcuts import render_to_response, HttpResponse
import traceback

#－－－－－－－－－－－－－－－－－－－－－－－－－－     意见和建议      －－－－－－－－－－－－－－－－－－－－－－－－－－
@login_required
@AdminRequired
def suggestions_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_suggestions'] = search_keyword
        request.session['page_index_suggestions'] = 1
        return HttpResponseRedirect(reverse('bms:suggestions_list', args=[1, ]))

    elif request.method == 'GET':
        message = request.session.get('message', '')
        request.session['message'] = ''
        search_keyword = request.session.get('search_keyword_suggestions', '')
        suggestions_set = Suggestions.objects()
        count = suggestions_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_suggestions'] = paging['page_index']
        suggestions_set = suggestions_set[paging['start_item']:paging['end_item']]
        data['suggestionss'] = suggestions_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/interactive/suggestions_list.html', data, context)

@login_required
@AdminRequired
def suggestions_detail(request, suggestions_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_suggestions', '1')
    data['page_index'] = page_index
    data['suggestions_id'] = suggestions_id
    suggestions = Suggestions.objects(id=suggestions_id).first()
    if suggestions:
        data['suggestions'] = suggestions
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:suggestions_list', args=[page_index, ]))
    return render_to_response('bms/interactive/suggestions_detail.html', data, context)
