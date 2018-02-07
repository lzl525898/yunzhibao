from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect
from wss.tools import *
from common.models import *
from django.core.urlresolvers import reverse
#2017/12/08分页
from common.tools import  PageTools
from wss.tools_wechat import OpenidViewRequired
from wss.views_ticket import *

#－－－－－－－－－－－－－－－－－－－－－－－－－－     二手商品统计      －－－－－－－－－－－－－－－－－－－－－－－－－－
#二手商品列表
# @OpenidViewRequired
@JSAPI_TICKET_Required
@CODE_View_Required
def wx_second_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    data = {}
    context = RequestContext(request)
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        pass
#         data['message'] = '网络延迟未获取用户信息'
#         return render_to_response('wss/warn.html', data, context)
    #判断是否是认证用户
    certificate_state="N"
    try:
        certificate_set = Certificate.objects(state = 'success',client =client ).first()
        if  certificate_set:
            certificate_state="Y"
    except:
        certificate_state="N"
    data['certificate_state'] = certificate_state
    #商品大类
    goods_type_list = GoodsType.objects(is_hidden=False)
    data['goods_type_list'] = goods_type_list
    #广告位
    advertising_list=[]
    try:
        advertising_position = AdvertisingPosition.objects(is_hidden=False,paper_id='1' ).first()
        if len(advertising_position)==0:
            pass
        else:
            advertising_list = Advertising.objects(is_hidden=False,position=advertising_position)
    except:
        pass
    data['advertising_list'] = advertising_list
    
    if request.method == 'POST':
        goods_type_state = request.POST.get('goods_type_state', 'all')#产品类型
        search_keyword = request.POST.get('search_keyword', '')#显示状态
        get_parameter = "?goods_type_state={0}&search_keyword={1}".format( goods_type_state,search_keyword,)
        return HttpResponseRedirect(reverse('wss:secondhand_list', args=[1, ]) + get_parameter)
    elif request.method == 'GET':
        data["get_data"] = request.GET
        goods_type_state  = request.GET.get("goods_type_state", 'all')
        data["goods_type_state"] =goods_type_state
        try:
           mall_goods_list = MallGoods.objects(is_hidden=False,state='publish').order_by('-create_time')
           #mall_goods_list = MallGoods.objects()
           mall_goods_set = request_tool.wx_mallgoods_filter(mall_goods_set=mall_goods_list)
        except Exception as e :
            data['message'] = '网络延迟,查询出错'+str(e)
            return render_to_response('wss/warn.html', data, context)
        count = mall_goods_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_employee'] = paging['page_index']
        mall_goods_set = mall_goods_set[paging['start_item']:paging['end_item']]
        data['mall_goods_list'] = mall_goods_set
        data['paging'] = paging
    
    return render_to_response('wss/secondHand/second_list_new.html', data, context)

#发布商品
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_publish_info(request):
    data = {}
    data=CREAT_DATA_CONTENT(request)
    context = RequestContext(request)
    wss_tools = DocumentWssTools(request)
    #商品现状
    present_situations =[]
    present_situation_list=MallGoods.PRESENT_SITUATION
    for present_situation in present_situation_list:
        present_situation_name=str(present_situation[1])
        present_situations.append(present_situation_name)
    data['present_situations'] = present_situations
    #商品大类
    goods_type_detail =[]
    goods_type_list = GoodsType.objects(is_hidden=False)
    for goods_type in goods_type_list:
        goods_name=str(goods_type.name)
        goods_type_detail.append(goods_name)
    data['goods_type_detail'] = goods_type_detail
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            create_mall_goods = MallGoods()
            create_mall_goods = wss_tools.wss_validation_goods(create_mall_goods)
            create_mall_goods.save()
            request.session['message'] = '创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('wss/secondHand/publish_info.html', data, context)
        except Exception as e:
            data['message'] = str(e)
            return render_to_response('wss/secondHand/publish_info.html', data, context)
        return HttpResponseRedirect(reverse('wss:secondhand_detail', args=[create_mall_goods.id, ]))

    elif request.method == 'GET':
        return render_to_response('wss/secondHand/publish_info.html', data, context)

#编辑
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_secondhand_edit(request, secondhand_id):
    context = RequestContext(request)
    data = {}
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    try:
        mall_goods = MallGoods.objects(id=secondhand_id).first()
    except:
        data['message'] = '未找到对应数据'
        return render_to_response('wss/warn.html', data, context)
    if mall_goods:
        data['mall_goods'] = mall_goods
    else:
        data['message'] = '未找到对应数据。'
        return render_to_response('wss/warn.html', data, context)
    context = RequestContext(request)
    wss_tools = DocumentWssTools(request)
    #商品现状
    present_situations =[]
    present_situation_list=MallGoods.PRESENT_SITUATION
    for present_situation in present_situation_list:
        present_situation_name=str(present_situation[1])
        present_situations.append(present_situation_name)
    data['present_situations'] = present_situations
    #商品大类
    goods_type_detail =[]
    goods_type_list = GoodsType.objects(is_hidden=False)
    for goods_type in goods_type_list:
        goods_name=str(goods_type.name)
        goods_type_detail.append(goods_name)
    data['goods_type_detail'] = goods_type_detail
    #页面翻译
    #商品现状
    goods_present_number = mall_goods.goods_present_situation
    goods_present_name=""
    for present_situation in present_situation_list:
       if  goods_present_number ==str(present_situation[0]):
           goods_present_name = str(present_situation[1])
    data['goods_present_name'] = goods_present_name
    if request.method == 'POST':
        try:
            mall_goods = wss_tools.wss_validation_goods(mall_goods)
            mall_goods.save()
            request.session['message'] = '创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('wss/secondHand/secondhand_edit.html', data, context)
        except Exception as e:
            data['message'] = str(e)
            return render_to_response('wss/secondHand/secondhand_edit.html', data, context)
        return HttpResponseRedirect(reverse('wss:secondhand_detail', args=[mall_goods.id, ]))

    elif request.method == 'GET':
        return render_to_response('wss/secondHand/secondhand_edit.html', data, context)

#商品详情
# @OpenidViewRequired
@JSAPI_TICKET_Required
@CODE_View_Required
def wx_secondhand_detail(request, secondhand_id):
    context = RequestContext(request)
    data={}
    data=CREAT_DATA_CONTENT(request)
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        pass
#         data['message'] = '网络延迟未获取用户信息'
#         return render_to_response('wss/warn.html', data, context)
    try:
        mall_goods = MallGoods.objects(id=secondhand_id).first()
    except:
        data['message'] = '未找到对应数据'
        return render_to_response('wss/warn.html', data, context)
    if mall_goods:
        data['mall_goods'] = mall_goods
    else:
        data['message'] = '未找到对应数据。'
        return render_to_response('wss/warn.html', data, context)
    return render_to_response('wss/secondHand/second_detail.html', data, context) 

#删除商品
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_secondhand_delete(request, secondhand_id):
    context = RequestContext(request)
    data = {}
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    try:
        mall_goods = MallGoods.objects(id=secondhand_id).first()
    except:
        data['message'] = '未找到对应数据'
        return render_to_response('wss/warn.html', data, context)
    if mall_goods:
        try:
            mall_goods.is_hidden= True
            mall_goods.save()
            data['message'] = "删除成功"
            return render_to_response('wss/success.html', data, context)
        except:
            data['message'] = '网络延迟，删除失败'
            return render_to_response('wss/warn.html', data, context)
    else:
        data['message'] = '未找到对应数据。'
        return render_to_response('wss/warn.html', data, context)
    #return HttpResponseRedirect(reverse('wss:wx_my_secondhands', args=[1, ]))

#管理我的产品
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_my_secondhands(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    data = {}
    context = RequestContext(request)
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    #商品大类
    goods_type_list = GoodsType.objects(is_hidden=False)
    data['goods_type_list'] = goods_type_list
    if request.method == 'POST':
        goods_type_state = request.POST.get('goods_type_state', 'all')#产品类型
        search_keyword = request.POST.get('search_keyword', '')#显示状态
        get_parameter = "?goods_type_state={0}&search_keyword={1}".format( goods_type_state,search_keyword,)
        return HttpResponseRedirect(reverse('wss:wx_my_secondhands', args=[1, ]) + get_parameter)
    elif request.method == 'GET':
        data["get_data"] = request.GET
        try:
           mall_goods_list = MallGoods.objects(is_hidden=False,client=client)
           mall_goods_set = request_tool.wx_mallgoods_filter(mall_goods_set=mall_goods_list)
           mall_goods_set = mall_goods_set.filter(Q(state='publish')|Q(state='offshelf')|Q(state='done'))
        except Exception as e :
            data['message'] = '网络延迟,查询出错'+str(e)
            return render_to_response('wss/warn.html', data, context)
        count = mall_goods_set.count()
        data["mall_goods_list"] = mall_goods_set
        data["publish_list"] =mall_goods_set.filter(Q(state='publish'))
        data["offshelf_list"] =mall_goods_set.filter(Q(state='offshelf'))
        data["done_list"] =mall_goods_set.filter(Q(state='done'))
        data['order_page']="my_secondhands"
    return render_to_response('wss/secondHand/my_secondhands.html', data, context)


#改变商品上架状态
@OpenidViewRequired
@JSAPI_TICKET_Required
def wx_change_secondhand(request, secondhand_id):
    context = RequestContext(request)
    data = {}
    if request.method == 'POST':
        change_state = request.POST.get('change_state', '')#上架状态
    else:
        change_state = request.GET.get('change_state', '')#上架状态
    if change_state not in ['offshelf' , 'done','publish']:
        data['message'] = '目标状态不正确，请稍后在试'
        return render_to_response('wss/warn.html', data, context)
    try:
        client = Client.objects(user=request.user).first()
        #client = Client.objects(id='58e598cf9a8f2b11f4680e4c').first()
        data['client'] = client
    except:
        data['message'] = '网络延迟未获取用户信息'
        return render_to_response('wss/warn.html', data, context)
    try:
        mall_goods = MallGoods.objects(id=secondhand_id).first()
    except:
        data['message'] = '未找到对应数据'
        return render_to_response('wss/warn.html', data, context)
    if mall_goods:
        try:
            mall_goods.state= str(change_state)
            mall_goods.save()
            request.session['message'] = '修改成功'
        except:
            data['message'] = '网络延迟，修改失败'
            return render_to_response('wss/warn.html', data, context)
    else:
        data['message'] = '未找到对应数据。'
        return render_to_response('wss/warn.html', data, context)
    return HttpResponseRedirect(reverse('wss:secondhand_detail', args=[mall_goods.id, ]))



#-----------------------------------------------分页信息------------------------------------------------------------------------

def get_secondhand_detail(request):
    goods_type_state = request.GET.get('goods_type_state', '')
    search_keyword = request.GET.get('search_keyword', '')
    page_index = request.GET.get('page', '')
    context = RequestContext(request)
    data = {}
    try:
        page_index = int(page_index)
    except:
        message= '网络延迟未获取分页信息'
        return  JsonResult(data=data, code=CODE_ERROR, message=message).response()
    request_tool = RequestTools(request)
    try:
       mall_goods_list = MallGoods.objects(is_hidden=False,state='publish').order_by('-create_time')
       #mall_goods_list = MallGoods.objects()
       mall_goods_list = request_tool.wx_mallgoods_filter(mall_goods_set=mall_goods_list)
    except Exception as e :
        data['message'] = '网络延迟,查询出错'+str(e)
        return render_to_response('wss/warn.html', data, context)
    count = mall_goods_list.count()
    page = PageTools()
    paging = page.get_paging(5, page_index, count)
    mall_goods_list = mall_goods_list[paging['start_item']:paging['end_item']]
    if len(mall_goods_list)>0:
        mall_goods_detail=[]
        for mall_goods_set in mall_goods_list:
            try:
                goods_set={}
                goods_name =mall_goods_set.goods_name
                if goods_name:
                    if len(goods_name)>10:
                        goods_name = goods_name[0:9]+'…'
                goods_price = mall_goods_set.unit_price
                goods_price1=''
                if goods_price :
                    goods_price1 =str( float(goods_price)/100)
                    if len(goods_price1)>6:
                        goods_price1 = goods_price1[0:5]+'…'
                #商品原价
                original_cost = mall_goods_set.original_cost
                original_cost1=''
                if original_cost :
                    original_cost1 =str( float(original_cost)/100)
                    if len(original_cost1)>6:
                        original_cost1 = original_cost1[0:5]+'…'
                goods_number =mall_goods_set.goods_count
                if goods_number:
                    if len(goods_number)>6:
                        goods_number = goods_number[0:5]+'…'
                #公共部分
                goods_set["goods_id"]=str(mall_goods_set.id) or ""#商品id
                goods_set["goods_picture"]=str(mall_goods_set.goods_image_list[0]) or "" #展示图片
                goods_set["goods_name"]=str(goods_name) or ""#商品名称
                goods_set["goods_price"]=str(goods_price1) or ""#商品价格
                goods_set["original_cost"]=str(original_cost1) or ""#商品原价
                goods_set["goods_number"]=str(goods_number) or ""#商品数量
                mall_goods_detail.append(goods_set)
            except Exception as e :
                #break
                message= '网络延迟,查询出错'+str(e)
                return  JsonResult(data=data, code=CODE_ERROR, message=message).response()
        data['mall_goods_detail'] = mall_goods_detail
    else:
        message= '未获取其他信息'
        return  JsonResult(data=data, code=CODE_ERROR, message=message).response()

    print(data)
    return JsonResult(data=data, code=CODE_SUCCESS).response()


#二手货分类列表
def wx_goodstype_list(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    #商品大类
    goods_type_list = GoodsType.objects(is_hidden=False)
    if len(goods_type_list)>0:
        
        i=0
        temp=[]
        temp2=[]
        for insurance_image in goods_type_list:
            i=i+1
            temp.append(insurance_image)
            if i%2 == 0:
                temp2.append(temp)
                temp=[]
        if len(temp)==1:
            temp.append([])
        temp2.append(temp)
                
    data['goods_type_list'] = temp2
    return render_to_response('wss/secondHand/wx_goodstype_list.html', data, context)










