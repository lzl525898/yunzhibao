__author__ = 'mlzx'
from django.contrib.auth.decorators import login_required
from common.decorators import SuperAdminRequired, ExceptionRequired
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from common.models import *
from common.tools import RequestTools, PageTools


# Create your views here.
@login_required
@SuperAdminRequired
def exception_list(request, page_index):
    context = RequestContext(request)
    page_index = int(page_index)
    if request.method == 'POST':
        search_keyword = request.POST.get('search_keyword', '')
        if len(search_keyword) > 30:
            request.session['message'] = '搜索关键字过长，请控制在30个字以内'
            return HttpResponseRedirect(reverse('bms:exception_list', args=[request.session.get('page_index', '1'), ]))
        request.session['search_keyword_exception'] = search_keyword
        request.session['page_index_exception'] = 1
        return HttpResponseRedirect(reverse('bms:exception_list', args=[1, ]))

    elif request.method == 'GET':
        data = {}
        message = request.session.get('message', '')
        data['message'] = message
        request.session['message'] = ''
        keyword = request.session.get('search_keyword_exception', '')
        data['search_keyword'] = keyword
        request.session['search_keyword_exception'] = ''
        if keyword == '':
            exceptions_set = DException.objects()
        else:
            exceptions_set = DException.objects(Q(exception__contains=keyword) | Q(type__contains=keyword))
        count = exceptions_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        data['paging'] = paging
        request.session['page_index_exception'] = paging['page_index']
        exceptions = exceptions_set[paging['start_item']: paging['end_item']]
        data['exceptions'] = exceptions
        return render_to_response('bms/log/system/exception/exception_list.html', data, context)


@login_required
@SuperAdminRequired
def exception_detail(request, exception_id):
    context = RequestContext(request)
    data = {}
    exception = DException.objects(id=exception_id).first()
    page_index = request.session.get('page_index_exception', '1')
    data['page_index'] = page_index
    if exception:
        data['exception'] = exception
    else:
        request.session['message'] = '未找到指定异常'
        return HttpResponseRedirect(reverse('bms:exception_list', args=[page_index, ]))
    return render_to_response('bms/log/system/exception/exception.html', data, context)


@login_required
@SuperAdminRequired
def new_exception_detail(request):
    context = RequestContext(request)
    data = {}
    exception = DException.objects().first()
    page_index = request.session.get('page_index_exception', '1')
    data['page_index'] = page_index
    if exception:
        data['exception'] = exception
    else:
        request.session['message'] = '未找到指定异常'
        return HttpResponseRedirect(reverse('bms:exception_list', args=[page_index, ]))
    return render_to_response('bms/log/system/exception/exception.html', data, context)


@login_required
@SuperAdminRequired
def exception_delete(request, exception_id):
    context = RequestContext(request)
    request_tool = RequestTools(request)
    request_tool.save_log()
    # data = {}
    exception = DException.objects(id=exception_id).first()
    page_index = request.session.get('page_index_exception', '1')
    # data['page_index'] = page_index
    if exception:
        try:
            exception.delete()
            request.session['message'] = '异常已被删除'
        except Exception as e:
            request.session['message'] = '删除异常失败：{0}'.format(e)
    else:
        request.session['message'] = '异常编号错误'
    return HttpResponseRedirect(reverse('bms:exception_list', args=[page_index, ]))


@login_required
@SuperAdminRequired
def exception_delete_all(request):
    request_tool = RequestTools(request)
    request_tool.save_log()
    page_index = request.session.get('page_index_exception', '1')
    try:
        keyword = request.POST.get('keyword', '')
        if keyword == '':
            exceptions_set = DException.objects()
        else:
            exceptions_set = DException.objects(Q(exception__contains=keyword) | Q(type__contains=keyword))
        exceptions_set.delete()
        request.session['message'] = '异常已被删除'
    except Exception as e:
        request.session['message'] = '删除异常失败：{0}'.format(e)
    return HttpResponseRedirect(reverse('bms:exception_list', args=[page_index, ]))


@login_required
@SuperAdminRequired
def exception_delete_similar(request, exception_id):
    context = RequestContext(request)
    request_tool = RequestTools(request)
    request_tool.save_log()
    # data = {}
    exception = DException.objects(id=exception_id).first()
    page_index = request.session.get('page_index_exception', '1')
    # data['page_index'] = page_index
    if exception:
        try:
            exception_set = DException.objects(traceback=exception.traceback)
            exception_set.delete()
            request.session['message'] = '异常已被删除'
        except Exception as e:
            request.session['message'] = '删除异常失败：{0}'.format(e)
    else:
        request.session['message'] = '异常编号错误'
    return HttpResponseRedirect(reverse('bms:exception_list', args=[page_index, ]))