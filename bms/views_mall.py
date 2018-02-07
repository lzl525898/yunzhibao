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
#-----------------------------------------------------添加二手商品类型-------------------------------------------------------------------------------
#商品类型部分
@login_required
@AdminRequired
def goods_type_list(request, page_index):
    context = RequestContext(request)
    data = {}
    try:
        page_index = int(page_index) 
    except:
        page_index = 1
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        #search_keyword = request.POST.get('search_keyword', '')
        #request.session['search_keyword_goods_type'] = search_keyword
        request.session['page_index'] = page_index
        return HttpResponseRedirect(reverse('bms:goods_type_list', args=[page_index, ]))

    elif request.method == 'GET':
        
        request_tool.check_message(data)
        data["get_data"] = request.GET
        #search_keyword = request.session.get('search_keyword_goods_type', '')
        goods_type_list = GoodsType.objects()
        count = goods_type_list.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index'] = paging['page_index']
        goods_type_list = goods_type_list[paging['start_item']:paging['end_item']]
        data['goods_type_lists'] = goods_type_list
        #data['search_keyword'] = search_keyword
        data['paging'] = paging
        #request.session['search_keyword_goods_type'] = ''
        return render_to_response('bms/mall/goods_type_list.html', data, context)
 


@login_required
@AdminRequired
def goods_type_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            create_goods_type = GoodsType()
            create_goods_type = bms_tools.validation_goods_type(create_goods_type)
            create_goods_type.save()
            request.session['message'] = '创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/mall/goods_type_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/mall/goods_type_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:goods_type_detail', args=[create_goods_type.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/mall/goods_type_create.html', data, context)
 

@login_required
@AdminRequired
def goods_type_detail(request, goods_type_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        goods_type = GoodsType.objects(id=goods_type_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:goods_type_list', args=[1, ]))
    if goods_type:
        data['goods_type'] = goods_type
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:goods_type_list', args=[page_index, ]))
    return render_to_response('bms/mall/goods_type_detail.html', data, context)  

@login_required
@AdminRequired
def goods_type_edit(request, goods_type_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        goods_type = GoodsType.objects(id=goods_type_id).first()
    except:
        request.session['message'] = '网络问题，未找到对应数据'
        return HttpResponseRedirect(reverse('bms:goods_type_list', args=[page_index, ]))
    if goods_type:
        data['goods_type'] = goods_type
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:goods_type_list', args=[page_index, ]))
    if request.method == 'POST':
        try:
            create_goods_type = goods_type
            create_goods_type = bms_tools.validation_goods_type(create_goods_type)
            create_goods_type.save()
            request.session['message'] = '编辑成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/mall/goods_type_edit.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/mall/goods_type_edit.html', data, context)
        return HttpResponseRedirect(reverse('bms:goods_type_detail', args=[create_goods_type.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/mall/goods_type_edit.html', data, context) 

@login_required
@AdminRequired
def goods_type_delete(request, goods_type_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        goods_type = GoodsType.objects(id=goods_type_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:goods_type_list', args=[1, ]))
    if  not goods_type:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:goods_type_list', args=[page_index, ]))
    #检测是否关联商品
    try:
        mall_goods_count = MallGoods.objects(goods_type=goods_type).count()
        if mall_goods_count>0:
            request.session['message'] = str(goods_type.name)+',此货物类别管理商品不能直接删除,暂时隐藏'
            goods_type.is_hidden=True
            goods_type.save()
            return HttpResponseRedirect(reverse('bms:goods_type_list', args=[page_index, ]))
    except:
        request.session['message'] = str(goods_type.name)+',此货物类别管理商品不能直接删除,暂时隐藏'
        goods_type.is_hidden=True
        goods_type.save()
        return HttpResponseRedirect(reverse('bms:goods_type_list', args=[page_index, ]))
    try:
        goods_type.delete()
        request.session['message'] = '删除成功'
    except:
        request.session['message'] = '网络延迟，删除出错请稍后再试'
    return HttpResponseRedirect(reverse('bms:goods_type_list', args=[page_index, ]))


#-----------------------------------------------------添加二手商品-------------------------------------------------------------------------------
#商品部分
@login_required
@AdminRequired
def mall_goods_list(request, page_index):
    context = RequestContext(request)
    data = {}
    try:
        page_index = int(page_index) 
    except:
        page_index = 1
    request.session['page_index'] = page_index
    request_tool = RequestTools(request)
    #商品大类
    goods_type_list = GoodsType.objects()
    data['goods_type_list'] = goods_type_list
    #商品状态
    present_situation_list=MallGoods.PRESENT_SITUATION
    data['present_situation_list'] = present_situation_list
    #认证用户列表
    try:
        certificate_set = Certificate.objects(state = 'success')
        if not certificate_set:
            request.session['message'] ='无已认证用户'
            return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[1, ]))
        data['certificate_list'] =certificate_set 
    except:
        data['certificate_list'] =[]
    if request.method == 'POST':
        request_tool.save_log()
        search_state = request.POST.get('search_state', '')#显示状态
        search_present_situation = request.POST.get('search_present_situation', '')#商品状态
        search_goods_type = request.POST.get('search_goods_type', '')#商品分类
        client_sign = request.POST.get('client_sign', '')#所有人
        search_keyword = request.POST.get('search_keyword', '')#关键字
        get_parameter = "?search_state={0}&search_present_situation={1}&search_goods_type={2}&client_sign={3}&search_keyword={4}".format(search_state, search_present_situation, search_goods_type, client_sign,search_keyword,)
        return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword  = request.GET.get("search_keyword", '')# request.session.get('search_keyword_goods_type', '')
        mall_goods_list = MallGoods.objects()
        count1 = mall_goods_list.count()
        mall_goods_list = request_tool.mall_goods_filter(mall_goods=mall_goods_list).order_by('-create_time')
        count = mall_goods_list.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index'] = paging['page_index']
        mall_goods_list = mall_goods_list[paging['start_item']:paging['end_item']]
        data['mall_goods_lists'] = mall_goods_list
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        #request.session['search_keyword_goods_type'] = ''
        return render_to_response('bms/mall/mall_goods_list.html', data, context)

#创建二手商品
@login_required
@AdminRequired
def mall_goods_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    mall_set = MallGoods()
    data['mall_set'] = mall_set
    #认证用户列表
    try:
        certificate_set = Certificate.objects(state = 'success')
        if not certificate_set:
            request.session['message'] ='无已认证用户'
            return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[1, ]))
        data['certificate_set'] =certificate_set 
    except:
        request.session['message'] ='网络延迟获取认证用户列表失败'
        return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[1, ]))
    #商品现状
    present_situation=mall_set.PRESENT_SITUATION
    data['present_situations'] = present_situation
    #上架状态
    state_list=mall_set.TYPE
    data['state_list'] = state_list
    #证明产品价值的方法
    certificate_type=mall_set.CERTIFICATE_TYPE
    data['certificate_types'] = certificate_type
    #地址部分
    pro_area_list = CargoArea.objects(level='1')
    data['pro_area_list'] = pro_area_list
    city_area_list = CargoArea.objects(level='2')
    data['city_area_list'] = city_area_list
    dist_area_list = CargoArea.objects(level='3')
    data['dist_area_list'] = dist_area_list
    #商品大类
    goods_type_list = GoodsType.objects(is_hidden=False)
    data['goods_type_list'] = goods_type_list
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            create_mall_goods = MallGoods()
            create_mall_goods = bms_tools.validation_mall_goods(create_mall_goods)
            create_mall_goods.save()
            request.session['message'] = '创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/mall/mall_goods_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/mall/mall_goods_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:mall_goods_detail', args=[create_mall_goods.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/mall/mall_goods_create.html', data, context)


@login_required
@AdminRequired
def mall_goods_detail(request, mall_goods_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        mall_goods = MallGoods.objects(id=mall_goods_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[1, ]))
    if mall_goods:
        data['mall_goods'] = mall_goods
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[page_index, ]))
    return render_to_response('bms/mall/mall_goods_detail.html', data, context)  

@login_required
@AdminRequired
def mall_goods_edit(request, mall_goods_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        mall_goods = MallGoods.objects(id=mall_goods_id).first()
        if not mall_goods:
             request.session['message'] = '未找到对应数据'
             return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[page_index, ]))
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[1, ]))
    data['mall_goods'] = mall_goods
    #认证用户列表
    try:
        certificate_set = Certificate.objects(state = 'success')
        if not certificate_set:
            request.session['message'] ='无已认证用户'
            return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[1, ]))
        data['certificate_set'] =certificate_set 
    except:
        request.session['message'] ='网络延迟获取认证用户列表失败'
        return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[1, ]))
    #商品现状
    present_situation=mall_goods.PRESENT_SITUATION
    data['present_situations'] = present_situation
    #上架状态
    state_list=mall_goods.TYPE
    data['state_list'] = state_list
    #证明产品价值的方法
    certificate_type=mall_goods.CERTIFICATE_TYPE
    data['certificate_types'] = certificate_type
    #地址部分
    pro_area_list = CargoArea.objects(level='1')
    data['pro_area_list'] = pro_area_list
    city_area_list = CargoArea.objects(level='2')
    data['city_area_list'] = city_area_list
    dist_area_list = CargoArea.objects(level='3')
    data['dist_area_list'] = dist_area_list
    #商品大类
    goods_type_list = GoodsType.objects(is_hidden=False)
    data['goods_type_list'] = goods_type_list
    #2017 分解地址省市区联动
    data["mail_prov_set"]=""
    data["mail_city_set"] =''
    data["mail_dist"]=""
    try:
        mail_address = mall_goods.mail_address
        mail_address_list =mail_address.split(' ')
        mail_prov=mail_address_list[0]
        #mail_prov_set = CargoArea.objects(level='1',name=mail_prov).first()
        data["mail_prov_set"]=mail_prov
#         mail_prov_number = mail_prov_set.code
        mail_city =mail_address_list[1]
        #mail_city_set = CargoArea.objects(level='2',name=mail_city).first()
        data["mail_city_set"] =mail_city
       # mail_city_number = mail_city_set.code
        data["mail_dist"]= ''
        if mail_address_list[2]:
            mail_dist =mail_address_list[2]
            data["mail_dist"]= mail_dist
    except:
        pass
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            create_mall_goods = bms_tools.validation_mall_goods(mall_goods)
            create_mall_goods.save()
            request.session['message'] = '编辑成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/mall/mall_goods_edit.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/mall/mall_goods_edit.html', data, context)
        return HttpResponseRedirect(reverse('bms:mall_goods_detail', args=[create_mall_goods.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/mall/mall_goods_edit.html', data, context)


@login_required
@AdminRequired
def mall_goods_delete(request, mall_goods_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index', '1')
    data['page_index'] = page_index
    try:
        mall_goods = MallGoods.objects(id=mall_goods_id).first()
    except:
        request.session['message'] = '未找到对应数据。'
        return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[1, ]))
    if  not mall_goods:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[page_index, ]))
    try:
        mall_goods.delete()
        request.session['message'] = '删除成功'
    except:
        request.session['message'] = '网络延迟，删除出错请稍后再试'
    return HttpResponseRedirect(reverse('bms:mall_goods_list', args=[page_index, ]))






























