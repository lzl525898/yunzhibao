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
#-----------------------------------------------------广告管理-------------------------------------------------------------------------------
#广告位管理

#广告位列表
@login_required
@AdminRequired
def advertising_position_list(request, page_index):
    context = RequestContext(request)
    data = {}
    try:
        page_index = int(page_index) 
    except:
        page_index = 1
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['page_index'] = page_index
        return HttpResponseRedirect(reverse('bms:advertising_position_list', args=[page_index, ]))
    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        advertising_position_list = AdvertisingPosition.objects()
        count = advertising_position_list.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index'] = paging['page_index']
        advertising_position_list = advertising_position_list[paging['start_item']:paging['end_item']]
        data['advertising_position_list'] = advertising_position_list
        data['paging'] = paging
        return render_to_response('bms/settings/advertising/advertising_position_list.html', data, context)
    
@login_required
@AdminRequired
def advertising_position_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            create_advertising_position = AdvertisingPosition()
            create_advertising_position = bms_tools.validation_advertising_position(create_advertising_position)
            create_advertising_position.save()
            request.session['message'] = '创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/settings/advertising/advertising_position_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/settings/advertising/advertising_position_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:advertising_position_detail', args=[create_advertising_position.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/settings/advertising/advertising_position_create.html', data, context)
    
@login_required
@AdminRequired
def advertising_position_detail(request, advertising_position_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        advertising_position = AdvertisingPosition.objects(id=advertising_position_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:advertising_position_list', args=[1, ]))
    if advertising_position:
        data['advertising_position'] = advertising_position
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:advertising_position_list', args=[page_index, ]))
    return render_to_response('bms/settings/advertising/advertising_position_detail.html', data, context)

@login_required
@AdminRequired
def advertising_position_edit(request, advertising_position_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        advertising_position = AdvertisingPosition.objects(id=advertising_position_id).first()
    except:
        request.session['message'] = '网络问题，未找到对应数据'
        return HttpResponseRedirect(reverse('bms:advertising_position_list', args=[page_index, ]))
    if advertising_position:
        data['advertising_position'] = advertising_position
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:advertising_position_list', args=[page_index, ]))
    if request.method == 'POST':
        try:
            create_advertising_position = advertising_position
            create_advertising_position = bms_tools.validation_advertising_position(create_advertising_position)
            create_advertising_position.save()
            request.session['message'] = '编辑成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/settings/advertising/advertising_position_edit.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/settings/advertising/advertising_position_edit.html', data, context)
        return HttpResponseRedirect(reverse('bms:advertising_position_detail', args=[create_advertising_position.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/settings/advertising/advertising_position_edit.html', data, context) 
    
    
@login_required
@AdminRequired
def advertising_position_delete(request, advertising_position_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        advertising_position = AdvertisingPosition.objects(id=advertising_position_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:advertising_position_list', args=[1, ]))
    if  not advertising_position:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:advertising_position_list', args=[page_index, ]))
    #检测是否关联商品
    try:
        advertising_count = Advertising.objects(position=advertising_position).count()
        if advertising_count>0:
            request.session['message'] = str(advertising_position.name)+',此货物类别管理商品不能直接删除,暂时隐藏'
            advertising_position.is_hidden=True
            advertising_position.save()
            return HttpResponseRedirect(reverse('bms:advertising_position_list', args=[page_index, ]))
    except:
        request.session['message'] = str(advertising_position.name)+',此货物类别管理商品不能直接删除,暂时隐藏'
        advertising_position.is_hidden=True
        advertising_position.save()
        return HttpResponseRedirect(reverse('bms:advertising_position_list', args=[page_index, ]))
    try:
        advertising_position.delete()
        request.session['message'] = '删除成功'
    except:
        request.session['message'] = '网络延迟，删除出错请稍后再试'
    return HttpResponseRedirect(reverse('bms:advertising_position_list', args=[page_index, ]))


#-----------------------------广告管理--------------------------------------------
#广告列表
@login_required
@AdminRequired
def advertising_list(request, page_index):
    context = RequestContext(request)
    data = {}
    try:
        page_index = int(page_index) 
    except:
        page_index = 1
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['page_index'] = page_index
        return HttpResponseRedirect(reverse('bms:advertising_list', args=[page_index, ]))
    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        advertising_list = Advertising.objects()
        count = advertising_list.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index'] = paging['page_index']
        advertising_list = advertising_list[paging['start_item']:paging['end_item']]
        data['advertising_list'] = advertising_list
        data['paging'] = paging
        return render_to_response('bms/settings/advertising/advertising_list.html', data, context)
    
    
@login_required
@AdminRequired
def advertising_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    #广告位列表
    advertising_position_list = AdvertisingPosition.objects(is_hidden = False)
    if len(advertising_position_list)==0:
        data['message'] = '请先创建可用广告位'
    data['advertising_position_list']=advertising_position_list
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            create_advertising = Advertising()
            create_advertising = bms_tools.validation_advertising(create_advertising)
            create_advertising.save()
            request.session['message'] = '创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/settings/advertising/advertising_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/settings/advertising/advertising_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:advertising_detail', args=[create_advertising.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/settings/advertising/advertising_create.html', data, context)
    
@login_required
@AdminRequired
def advertising_detail(request, advertising_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        advertising = Advertising.objects(id=advertising_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:advertising_list', args=[1, ]))
    if advertising:
        data['advertising'] = advertising
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:advertising_list', args=[page_index, ]))
    return render_to_response('bms/settings/advertising/advertising_detail.html', data, context)

@login_required
@AdminRequired
def advertising_edit(request, advertising_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    #广告位列表
    advertising_position_list = AdvertisingPosition.objects(is_hidden = False)
    if len(advertising_position_list)==0:
        data['message'] = '请先创建可用广告位'
    data['advertising_position_list']=advertising_position_list
    try:
        advertising = Advertising.objects(id=advertising_id).first()
    except:
        request.session['message'] = '网络问题，未找到对应数据'
        return HttpResponseRedirect(reverse('bms:advertising_list', args=[page_index, ]))
    if advertising:
        data['advertising'] = advertising
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:advertising_list', args=[page_index, ]))
    if request.method == 'POST':
        try:
            create_advertising = advertising
            create_advertising = bms_tools.validation_advertising(create_advertising)
            create_advertising.save()
            request.session['message'] = '编辑成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/settings/advertising/advertising_edit.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/settings/advertising/advertising_edit.html', data, context)
        return HttpResponseRedirect(reverse('bms:advertising_detail', args=[create_advertising.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/settings/advertising/advertising_edit.html', data, context) 
    
    
@login_required
@AdminRequired
def advertising_delete(request, advertising_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        advertising = Advertising.objects(id=advertising_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:advertising_list', args=[1, ]))
    if  not advertising:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:advertising_list', args=[page_index, ]))
    try:
        advertising.delete()
        request.session['message'] = '删除成功'
    except:
        request.session['message'] = '网络延迟，删除出错请稍后再试'
    return HttpResponseRedirect(reverse('bms:advertising_list', args=[page_index, ]))


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    