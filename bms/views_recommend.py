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
#众安保险
from pss.ZhongAnApiClient import ZhongAnApiClient
import collections
from django.template import RequestContext
from django.shortcuts import render_to_response
import json
from django.conf import settings
#－－－－－－－－－－－－－－－－－－－－－－－－－－     特推产品      －－－－－－－－－－－－－－－－－－－－－－－－－－


@login_required
@AdminRequired
def recommend_product_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        state = request.POST.get('state', '')
        search_keyword = request.POST.get('search_keyword', '')
        get_parameter = "?search_keyword={0}&state={1}".format(search_keyword,state)
        return HttpResponseRedirect(reverse('bms:recommend_product_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        message = request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request_tool.get_parameter("search_keyword")
        recommend_product_set = RecommendProduct.objects()
        recommend_product_set = request_tool.recommend_product_filter(recommend_product_set=recommend_product_set)
        count = recommend_product_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_head_company'] = paging['page_index']
        recommend_product_set = recommend_product_set[paging['start_item']:paging['end_item']]
        data['recommend_product_set'] = recommend_product_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/product/recommend_product_list.html', data, context)
    
    

#创建二手商品
@login_required
@AdminRequired
def recommend_product_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    recommend_product_set = RecommendProduct()
    data['recommend_product_set'] = recommend_product_set
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            create_recommend_product = RecommendProduct()
            create_recommend_product = bms_tools.validation_recommend_product(create_recommend_product)
            create_recommend_product.save()
            request.session['message'] = '创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/product/recommend_product_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/product/recommend_product_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:recommend_product_detail', args=[create_recommend_product.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/product/recommend_product_create.html', data, context)


@login_required
@AdminRequired
def recommend_product_detail(request, recommend_product_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        recommend_product = RecommendProduct.objects(id=recommend_product_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:recommend_product_list', args=[1, ]))
    if recommend_product:
        data['recommend_product'] = recommend_product
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:recommend_product_list', args=[page_index, ]))
    return render_to_response('bms/product/recommend_product_detail.html', data, context)  

@login_required
@AdminRequired
def recommend_product_edit(request, recommend_product_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        recommend_product = RecommendProduct.objects(id=recommend_product_id).first()
        if not recommend_product:
             request.session['message'] = '未找到对应数据'
             return HttpResponseRedirect(reverse('bms:recommend_product_list', args=[page_index, ]))
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:recommend_product_list', args=[1, ]))
    data['recommend_product'] = recommend_product

    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            create_recommend_product = bms_tools.validation_recommend_product(recommend_product)
            create_recommend_product.save()
            request.session['message'] = '编辑成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/product/recommend_product_edit.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/product/recommend_product_edit.html', data, context)
        return HttpResponseRedirect(reverse('bms:recommend_product_detail', args=[create_recommend_product.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/product/recommend_product_edit.html', data, context)


@login_required
@AdminRequired
def recommend_product_delete(request, recommend_product_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        recommend_product = RecommendProduct.objects(id=recommend_product_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:recommend_product_list', args=[1, ]))
    if  not recommend_product:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:recommend_product_list', args=[page_index, ]))
    try:
        recommend_product.delete()
        request.session['message'] = '删除成功'
    except:
        request.session['message'] = '网络延迟，删除出错请稍后再试'
    return HttpResponseRedirect(reverse('bms:recommend_product_list', args=[page_index, ]))










