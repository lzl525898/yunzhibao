from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from wss.tools import *
#js_ticket
from wss.views_ticket import *
from common.models import *
from common.decorators import ExceptionRequired
from common.decorators import AdminRequired
from wss.tools_wechat import OpenidViewRequired
from django.contrib.auth.decorators import login_required

import time
import pingpp
import json

from wss.views_sendmessage import  send_wx_message
from common import tools_string
from requests.api import request
from common.driver_dict import *
from wss.tools import DocumentWssTools
from common.tools_legoo import *
import datetime
#二维码
import qrcode
#2017/06/09测试汇聚宝传值
from bms.views_order import order_pass_test
#2017/12/08分页
from common.tools import  PageTools

#---------------------------------推荐产品----------------------------------------------------------------
@CODE_View_Required
@JSAPI_TICKET_Required
#推荐产品详情
def wx_recommend_product(request, recommend_product_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    try:
        recommend_product = RecommendProduct.objects(id=recommend_product_id).first()
    except:
        data['message'] = '未找到对应数据。'
        return render_to_response('wss/warn.html', data, context)
    if recommend_product:
        data['recommend_product'] = recommend_product
    else:
        data['message'] = '未找到对应数据'
        return render_to_response('wss/warn.html', data, context)
    return render_to_response('wss/insure/recommend_insurance_product.html', data, context)


#推荐详情列表
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_recommend_list(request, page_index):
    context = RequestContext(request)
    data = {}
    data=CREAT_DATA_CONTENT(request)
    page_index = int(page_index)
    request_tool = RequestTools(request)

    if request.method == 'POST':
        product_state = request.POST.get('product_state', 'loan')#特推产品类型
        search_keyword = request.POST.get('search_keyword', '')#显示状态
        get_parameter = "?product_state={0}&search_keyword={1}".format( product_state,search_keyword,)
        return HttpResponseRedirect(reverse('wss:wx_recommend_list', args=[1, ]) + get_parameter)
    elif request.method == 'GET':
        data["get_data"] = request.GET
        product_state  = request.GET.get("product_state", 'loan')
        try:
           recommend_product_set = RecommendProduct.objects(is_hidden=False,product_type=product_state).order_by('-create_time')
           #mall_goods_list = MallGoods.objects(is_hidden=False,product_type=product_state).order_by('-create_time')
           #mall_goods_list = MallGoods.objects()
           recommend_product_set = request_tool.recommend_product_filter(recommend_product_set=recommend_product_set)
        except Exception as e :
            data['message'] = '网络延迟,查询出错'+str(e)
            return render_to_response('wss/warn.html', data, context)
        count = recommend_product_set.count()
        #暂时屏蔽分页部分
#         page = PageTools()
#         paging = page.get_paging(5, page_index, count)
#         request.session['page_index_employee'] = paging['page_index']
#         mall_goods_set = mall_goods_set[paging['start_item']:paging['end_item']]
        data['recommend_product_list'] = recommend_product_set
#         data['paging'] = paging
    
    return render_to_response('wss/insure/wx_recommend_product.html', data, context)










