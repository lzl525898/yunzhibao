__author__ = 'mlzx'
from django.contrib.auth.decorators import login_required
from common.decorators import SuperAdminRequired, ExceptionRequired
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from common.models import *
from common.tools import RequestTools, PageTools
from wss.models_wechat import Event

# Create your views here.
@login_required
@SuperAdminRequired
def log_list(request, page_index):
    context = RequestContext(request)
    page_index = int(page_index)
    if request.method == 'POST':
        search_keyword = request.POST.get('search_keyword', '')
        if len(search_keyword) > 30:
            request.session['message'] = '搜索关键字过长，请控制在30个字以内'
            return HttpResponseRedirect(reverse('bms:log_list', args=[request.session.get('page_index', '1'), ]))
        request.session['search_keyword_log'] = search_keyword
        request.session['page_index_log'] = 1
        return HttpResponseRedirect(reverse('bms:log_list', args=[1, ]))

    elif request.method == 'GET':
        data = {}
        message = request.session.get('message', '')
        data['message'] = message
        request.session['message'] = ''
        keyword = request.session.get('search_keyword_log', '')
        data['search_keyword'] = keyword
        request.session['search_keyword_log'] = ''
        logs_set = Log.objects(Q(content__contains=keyword)
                               | Q(ip__contains=keyword)
                               | Q(type__contains=keyword)
                               | Q(path__contains=keyword))
        count = logs_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        data['paging'] = paging
        request.session['page_index_log'] = paging['page_index']
        logs = logs_set[paging['start_item']: paging['end_item']]
        data['logs'] = logs
        return render_to_response('bms/log/system/log_list.html', data, context)


@login_required
@SuperAdminRequired
def log_detail(request, log_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_log', '1')
    data['page_index'] = page_index
    log = Log.objects(id=log_id).first()
    if log:
        data['log'] = log
    else:
        data['message'] = '未找到指定日志'
    return render_to_response('bms/log/system/log.html', data, context)


@login_required
@SuperAdminRequired
def log_delete(request, log_id):
    context = RequestContext(request)
    log = Log.objects(id=log_id).first()
    page_index = request.session.get('page_index_log', '1')
    if log:
        try:
            log.delete()
            request.session['message'] = '日志已被删除'
            request_tool = RequestTools(request)
            request_tool.save_log()
        except Exception as e:
            request.session['message'] = '删除日志失败：{0}'.format(e)
    else:
        request.session['message'] = '日志编号错误'
    return HttpResponseRedirect(reverse('bms:log_list', args=[page_index, ]))


@login_required
@SuperAdminRequired
def log_delete_all(request):
    page_index = request.session.get('page_index_log', '1')
    try:
        Log.objects().delete()
        request.session['message'] = '日志已被删除'
        request_tool = RequestTools(request)
        request_tool.save_log()
    except Exception as e:
        request.session['message'] = '删除日志失败：{0}'.format(e)
    return HttpResponseRedirect(reverse('bms:log_list', args=[page_index, ]))


@login_required
@SuperAdminRequired
def wechat_event_list(request, page_index):
    context = RequestContext(request)
    page_index = int(page_index)
    if request.method == 'POST':
        search_keyword = request.POST.get('search_keyword', '')
        if len(search_keyword) > 30:
            request.session['message'] = '搜索关键字过长，请控制在30个字以内'
            return HttpResponseRedirect(reverse('bms:wechat_event_list', args=[request.session.get('page_index', '1'), ]))
        request.session['search_keyword_wechat_event'] = search_keyword
        request.session['page_index_wechat_event'] = 1
        return HttpResponseRedirect(reverse('bms:wechat_event_list', args=[1, ]))

    elif request.method == 'GET':
        data = {}
        message = request.session.get('message', '')
        data['message'] = message
        request.session['message'] = ''
        keyword = request.session.get('search_keyword_wechat_event', '')
        data['search_keyword'] = keyword
        request.session['search_keyword_wechat_event'] = ''
        wechat_events_set = Event.objects(Q(from_user_name__contains=keyword)
                               | Q(to_user_name__contains=keyword)
                               | Q(msg_type__contains=keyword)
                               | Q(content__contains=keyword))
        count = wechat_events_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        data['paging'] = paging
        request.session['page_index_wechat_event'] = paging['page_index']
        wechat_events = wechat_events_set[paging['start_item']: paging['end_item']]
        data['wechat_events'] = wechat_events
        return render_to_response('bms/log/wechat/event_list.html', data, context)


@login_required
@SuperAdminRequired
def wechat_event_detail(request, wechat_event_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_wechat_event', '1')
    data['page_index'] = page_index
    wechat_event = Event.objects(id=wechat_event_id).first()
    if wechat_event:
        data['wechat_event'] = wechat_event
    else:
        data['message'] = '未找到指定日志'
    return render_to_response('bms/log/wechat/event.html', data, context)


@login_required
@SuperAdminRequired
def wechat_event_delete(request, wechat_event_id):
    context = RequestContext(request)
    wechat_event = Event.objects(id=wechat_event_id).first()
    page_index = request.session.get('page_index_wechat_event', '1')
    if wechat_event:
        try:
            wechat_event.delete()
            request.session['message'] = '日志已被删除'
            request_tool = RequestTools(request)
            request_tool.save_log()
        except Exception as e:
            request.session['message'] = '删除日志失败：{0}'.format(e)
    else:
        request.session['message'] = '日志编号错误'
    return HttpResponseRedirect(reverse('bms:wechat_event_list', args=[page_index, ]))


@login_required
@SuperAdminRequired
def wechat_event_delete_all(request):
    page_index = request.session.get('page_index_wechat_event', '1')
    try:
        Event.objects().delete()
        request.session['message'] = '日志已被删除'
        request_tool = RequestTools(request)
        request_tool.save_log()
    except Exception as e:
        request.session['message'] = '删除日志失败：{0}'.format(e)
    return HttpResponseRedirect(reverse('bms:wechat_event_list', args=[page_index, ]))
