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
#－－－－－－－－－－－－－－－－－－－－－－－－－－     保险总公司      －－－－－－－－－－－－－－－－－－－－－－－－－－


@login_required
@AdminRequired
def head_company_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_head_company'] = search_keyword
        request.session['page_index_head_company'] = 1
        # return HttpResponseRedirect(reverse('bms:head_company_list', args=[1, ]))
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:head_company_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        message = request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_head_company', '')
        head_company_set = InsuranceCompanyParent.objects()
        head_company_set = request_tool.head_company_filter(head_company_set=head_company_set, keyword=search_keyword)
        count = head_company_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_head_company'] = paging['page_index']
        head_company_set = head_company_set[paging['start_item']:paging['end_item']]
        data['head_companys'] = head_company_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/product/head_company_list.html', data, context)

@login_required
@AdminRequired
def head_company_detail(request, head_company_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_head_company', '1')
    data['page_index'] = page_index
    data['head_company_id'] = head_company_id
    head_company = InsuranceCompanyParent.objects(id=head_company_id).first()
    if head_company:
        data['head_company'] = head_company
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:head_company_list', args=[page_index, ]))
    return render_to_response('bms/product/head_company_detail.html', data, context)


@login_required
@AdminRequired
def head_company_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_head_company', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            head_company = InsuranceCompanyParent()
            head_company = bms_tools.validation_head_company(head_company)
            if request.POST.get('active', '') == 'show':
                head_company.is_hidden = False
            else:
                head_company.is_hidden = True
            head_company.save()
            request.session['message'] = '创建成功'
            return HttpResponseRedirect(reverse('bms:head_company_detail', args=[head_company.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/product/head_company_create.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/product/head_company_create.html', data, context)




@login_required
@AdminRequired
def head_company_edit(request, head_company_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_head_company', '1')
    data['page_index'] = page_index
    head_company = InsuranceCompanyParent.objects.get(id=head_company_id)
    if head_company:
        data['head_company'] = head_company
    else:
        request.session['message'] = '未找到对应的保险公司'
        return HttpResponseRedirect(reverse('bms:head_company_detail', args=[head_company_id, ]))
    if request.method == 'POST':
        try:
            head_company = bms_tools.validation_head_company(head_company)
            if request.POST.get('active', '') == 'show':
                head_company.is_hidden = False
            else:
                head_company.is_hidden = True
            head_company.save()
            request.session['message'] = '编辑成功'
            return HttpResponseRedirect(reverse('bms:head_company_detail', args=[head_company.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/product/head_company_edit.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/product/head_company_edit.html', data, context)


# @login_required
# @AdminRequired
# def company_document_save(request, company_id):
#     context = RequestContext(request)
#     data = {}
#     request_tools = RequestTools(request)
#     request_tools.check_message(data)
#     page_index = request.session.get('page_index_company', '1')
#     data['page_index'] = page_index
#     data['company_id'] = company_id
#     insurance_document_set = InsuranceDocument.objects(company_id=company_id, is_hidden=False)
#     data['insurance_documents'] = insurance_document_set
#     company = InsuranceCompany.objects(id=company_id).first()
#     if company:
#         data['company'] = company
#     else:
#         request.session['message'] = '未找到对应数据'
#         return HttpResponseRedirect(reverse('bms:company_list', args=[page_index, ]))
#     return render_to_response('bms/insurance/company_detail.html', data, context)


#－－－－－－－－－－－－－－－－－－－－－－－－－－     保险分公司     －－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def tail_company_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_tail_company'] = search_keyword
        request.session['page_index_tail_company'] = 1
        # return HttpResponseRedirect(reverse('bms:tail_company_list', args=[1, ]))
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:tail_company_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        message = request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_tail_company', '')
        tail_company_set = InsuranceCompany.objects()
        tail_company_set = request_tool.tail_company_filter(tail_company_set=tail_company_set, keyword=search_keyword)
        count = tail_company_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_tail_company'] = paging['page_index']
        tail_company_set = tail_company_set[paging['start_item']:paging['end_item']]
        data['tail_companys'] = tail_company_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/product/tail_company_list.html', data, context)

@login_required
@AdminRequired
def tail_company_detail(request, tail_company_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_tail_company', '1')
    data['page_index'] = page_index
    data['tail_company_id'] = tail_company_id
    tail_company = InsuranceCompany.objects(id=tail_company_id).first()
    # insurance_document_set = InsuranceDocument.objects(tail_company_id=tail_company_id, is_hidden=False)
    # data['insurance_documents'] = insurance_document_set
    # if request.method == 'POST':
    #     tail_company.docking_documents = []
    #     for insurance_document in insurance_document_set:
    #         # insurance_document = insurance_document.id
    #         print(str(insurance_document.id))
    #         insurance_document_name = request.POST.get(str(insurance_document.id), '')
    #         document_type = request.POST.get('document_type', '')
    #         if insurance_document_name:
    #             if tail_company:
    #                 if document_type == 'docking_document':
    #                     if insurance_document not in tail_company.docking_documents:
    #                         tail_company.docking_documents.append(insurance_document)
    #                 elif document_type == 'car_document':
    #                     if insurance_document not in tail_company.car_documents:
    #                         tail_company.car_documents.append(insurance_document)
    #                 elif document_type == 'batch_document':
    #                     if insurance_document not in tail_company.batch_documents:
    #                         tail_company.batch_documents.append(insurance_document)
    #                 else:
    #                     request.session['message'] = '未找到对应的保险保险文档'
    #                     return HttpResponseRedirect(reverse('bms:tail_company_detail', args=[tail_company.id, ]))
    #             else:
    #                 request.session['message'] = '未找到对应的保险公司'
    #             return HttpResponseRedirect(reverse('bms:tail_company_detail', args=[tail_company.id, ]))
    #         else:
    #             if tail_company:
    #                 insurance_document_delete = InsuranceDocument.objects(id=insurance_document.id).first()
    #                 if insurance_document_delete:
    #                     if document_type == 'docking_document':
    #                         if insurance_document_delete in tail_company.docking_documents:
    #                             tail_company.docking_documents.remove(insurance_document_delete)
    #                     elif document_type == 'car_document':
    #                         if insurance_document_delete in tail_company.car_documents:
    #                             tail_company.car_documents.remove(insurance_document_delete)
    #                     elif document_type == 'batch_document':
    #                         if insurance_document_delete in tail_company.batch_documents:
    #                             tail_company.batch_documents.remove(insurance_document_delete)
    #                     else:
    #                         request.session['message'] = '未找到对应的保险保险文档'
    #                         return HttpResponseRedirect(reverse('bms:tail_company_detail', args=[tail_company.id, ]))
    #             else:
    #                 request.session['message'] = '未找到对应的保险公司'
    #                 return HttpResponseRedirect(reverse('bms:tail_company_detail', args=[tail_company.id, ]))
    #     tail_company.save()
    #     return HttpResponseRedirect(reverse('bms:tail_company_detail', args=[tail_company.id, ]))
    #
    # elif request.method == 'GET':
    if tail_company:
        data['tail_company'] = tail_company
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:tail_company_list', args=[page_index, ]))
    return render_to_response('bms/product/tail_company_detail.html', data, context)


@login_required
@AdminRequired
def tail_company_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_tail_company', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    head_company_set = InsuranceCompanyParent.objects()
    data['head_companys'] = head_company_set
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            tail_company = InsuranceCompany()
            tail_company = bms_tools.validation_tail_company(tail_company)
            if request.POST.get('active', '') == 'show':
                tail_company.is_hidden = False
            else:
                tail_company.is_hidden = True
            tail_company.save()
            request.session['message'] = '创建成功'
            return HttpResponseRedirect(reverse('bms:tail_company_detail', args=[tail_company.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/product/tail_company_create.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/product/tail_company_create.html', data, context)

@login_required
@AdminRequired
def tail_company_edit(request, tail_company_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_tail_company', '1')
    data['page_index'] = page_index
    tail_company = InsuranceCompany.objects(id=tail_company_id).first()
    if tail_company:
        data['tail_company'] = tail_company
    else:
        request.session['message'] = '未找到对应的保险公司'
        return HttpResponseRedirect(reverse('bms:tail_company_detail', args=[tail_company_id, ]))
    if request.method == 'POST':
        try:
            tail_company = bms_tools.validation_tail_company(tail_company)
            if request.POST.get('active', '') == 'show':
                tail_company.is_hidden = False
            else:
                tail_company.is_hidden = True
            tail_company.save()
            request.session['message'] = '编辑成功'
            return HttpResponseRedirect(reverse('bms:tail_company_detail', args=[tail_company.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/product/tail_company_edit.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/product/tail_company_edit.html', data, context)



#－－－－－－－－－－－－－－－－－－－－－－－－－－     保险文档      －－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def insurance_document_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_insurance_document'] = search_keyword
        request.session['page_index_insurance_document'] = 1
        # return HttpResponseRedirect(reverse('bms:insurance_document_list', args=[1, ]))
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:insurance_document_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        # message = request.session.get('message', '')
        # request.session['message'] = ''
        message = request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_insurance_document', '')
        insurance_document_set = InsuranceDocument.objects()
        insurance_document_set = request_tool.insurance_document_filter(insurance_document_set=insurance_document_set, keyword=search_keyword)
        count = insurance_document_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_insurance_document'] = paging['page_index']
        insurance_document_set = insurance_document_set[paging['start_item']:paging['end_item']]
        data['insurance_documents'] = insurance_document_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/product/document_list.html', data, context)

@login_required
@AdminRequired
def insurance_document_detail(request, document_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_insurance_document', '1')
    data['page_index'] = page_index
    insurance_document = InsuranceDocument.objects(id=document_id).first()
    if insurance_document:
        data['insurance_document'] = insurance_document
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:insurance_document_list', args=[page_index, ]))
    return render_to_response('bms/product/document_detail.html', data, context)


@login_required
@AdminRequired
def insurance_document_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_insurance_document', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    company_set = InsuranceCompany.objects()
    data['companys'] = company_set
    insurance_product_set = InsuranceProducts.objects()
    data['insurance_products'] = insurance_product_set
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            insurance_document = InsuranceDocument()
            insurance_document = bms_tools.validation_document(insurance_document)
            if request.POST.get('active', '') == 'show':
                insurance_document.is_hidden = False
            else:
                insurance_document.is_hidden = True
            insurance_document.save()
            request.session['message'] = '创建成功'
            return HttpResponseRedirect(reverse('bms:insurance_document_detail', args=[insurance_document.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
        return render_to_response('bms/product/document_create.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/product/document_create.html', data, context)

@login_required
@AdminRequired
def insurance_document_edit(request, document_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_insurance_document', '1')
    data['page_index'] = page_index
    company_set = InsuranceCompany.objects()
    data['companys'] = company_set
    insurance_product_set = InsuranceProducts.objects()
    data['insurance_products'] = insurance_product_set
    insurance_document = InsuranceDocument.objects.get(id=document_id)

    if insurance_document:
        data['insurance_document'] = insurance_document
    else:
        request.session['message'] = '未找到对应的保险公司'
        return HttpResponseRedirect(reverse('bms:insurance_document_detail', args=[document_id, ]))
    if request.method == 'POST':
        try:
            insurance_document = bms_tools.validation_document(insurance_document)
            if request.POST.get('active', '') == 'show':
                insurance_document.is_hidden = False
            else:
                insurance_document.is_hidden = True
            insurance_document.save()
            request.session['message'] = '编辑成功'
            return HttpResponseRedirect(reverse('bms:insurance_document_detail', args=[document_id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/product/document_edit.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/product/document_edit.html', data, context)

@login_required
@AdminRequired
def insurance_document_preview(request, document_id):
    insurance_document = InsuranceDocument.objects.get(id=document_id)
    return HttpResponse(insurance_document.content)


#－－－－－－－－－－－－－－－－－－－－－－－－－－     保险产品      －－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def insurance_product_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_insurance_product'] = search_keyword
        request.session['page_index_insurance_product'] = 1
        # return HttpResponseRedirect(reverse('bms:insurance_product_list', args=[1, ]))
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:insurance_product_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        message = request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_insurance_product', '')
        insurance_product_set = InsuranceProducts.objects()
        insurance_product_set = request_tool.insurance_product_filter(insurance_product_set=insurance_product_set, keyword=search_keyword)
        count = insurance_product_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_insurance_product'] = paging['page_index']
        insurance_product_set = insurance_product_set[paging['start_item']:paging['end_item']]
        data['insurance_products'] = insurance_product_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/product/insurance_product_list.html', data, context)

@login_required
@AdminRequired
def insurance_product_detail(request, insurance_product_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_insurance_product', '1')
    data['page_index'] = page_index
    insurance_product = InsuranceProducts.objects(id=insurance_product_id).first()
    cargo_list = Cargo.objects(state = True)
    data['cargo_list'] = cargo_list
    product_cargo = ProductCargo.objects()
    data['product_cargo_list'] = product_cargo
    cargo_area_list = CargoArea.objects(level =  '1' )
    data['cargo_area_list'] = cargo_area_list
    if insurance_product:
        data['insurance_product'] = insurance_product
        a=insurance_product.no_insurable_route
        print(a)
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:insurance_product_list', args=[page_index, ]))
    return render_to_response('bms/product/insurance_product_detail.html', data, context)


@login_required
@AdminRequired
def insurance_product_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_insurance_product', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    company_set = InsuranceCompany.objects()
    data['tail_companys'] = company_set
    document_set = InsuranceDocument.objects()
    data['documents'] = document_set
    data['product_types'] = InsuranceProducts.PRODUCT_TYPE
    data['insurance_types'] = InsuranceProducts.INSURANCE_TYPE
    insurance_product = InsuranceProducts()
    data['insurance_product' ]=insurance_product
    #添加中介信息
    intermediary_set = Intermediary.objects.filter(state=True)
    data['intermediary_set'] = intermediary_set 
    # insurance_product_set = InsuranceProducts.objects()
    # data['insurance_products'] = insurance_product_set
    #2017/5/22添加来源渠道
    data['create_ways'] = InsuranceProducts.CREATE_WAY
    #2017/6/1添加可承包用户类型
    data['user_types'] = InsuranceProducts.USER_TYPE
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            insurance_product = InsuranceProducts()
            insurance_product = bms_tools.validation_insurance_product(insurance_product)
            insurance_product.save()
            if request.POST.get('active', '') == 'show':
                insurance_product.is_hidden = False
            else:
                insurance_product.is_hidden = True
            insurance_product.save()
            request.session['message'] = '创建成功'
            return HttpResponseRedirect(reverse('bms:insurance_product_detail', args=[insurance_product.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
        return render_to_response('bms/product/insurance_product_create.html', data, context)
    elif request.method == 'GET':
#         insurance_product = InsuranceProducts()
#         data['insurance_product' ]=insurance_product
        return render_to_response('bms/product/insurance_product_create.html', data, context)

#############为产品新建文档，产品详情页面
@login_required
@AdminRequired
def insurance_product_create_document(request, insurance_product_id, company_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_insurance_product', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    insurance_product = InsuranceProducts.objects(id=insurance_product_id).first()
    company = InsuranceCompany.objects(id=company_id).first()
    insurance_document_set = InsuranceDocument.objects(company=company)
    data['documents'] = insurance_document_set
    data['company_id'] = company_id
    data['insurance_product_id'] = insurance_product_id
    data['insurance_product'] = insurance_product

    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            insurance_product.documents = []
            document_ids = request.POST.getlist('documents', [])
            if document_ids:
                insurance_documents = InsuranceDocument.objects(id__in=document_ids)
                for insurance_document in insurance_documents:
                    if insurance_document not in insurance_product.documents:
                        insurance_product.documents.append(insurance_document)
            insurance_product.save()
            request.session['message'] = '创建成功'
            return HttpResponseRedirect(reverse('bms:insurance_product_detail', args=[insurance_product.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
        return render_to_response('bms/product/insurance_product_create_document.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/product/insurance_product_create_document.html', data, context)

########删除产品里的文档
@login_required
@AdminRequired
def insurance_product_delete_document(request, insurance_product_id, document_id):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_insurance_product', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    insurance_product = InsuranceProducts.objects(id=insurance_product_id).first()
    try:
        if insurance_product:
            insurance_document = InsuranceDocument.objects(id=document_id).first()
            if insurance_document:
                insurance_product.documents.remove(insurance_document)
            else:
                request.session['message'] = '删除失败，该商品不存在删除的文档'
                return HttpResponseRedirect(reverse('bms:insurance_product_detail', args=[insurance_product.id, ]))
        else:
            request.session['message'] = '删除失败，该产品不存在'
            return HttpResponseRedirect(reverse('bms:insurance_product_detail', args=[insurance_product.id, ]))
    except CustomError as e:
        data['message'] = e.message
    except Exception as e:
        print(traceback.format_exc())
        data['message'] = str(e)
    request.session['message'] = '删除成功'
    insurance_product.save()
    return HttpResponseRedirect(reverse('bms:insurance_product_detail', args=[insurance_product.id, ]))

#校验产品与货物相关联
def  check_insurance_cargo(request, insurance_product_id):
    insurance_product = InsuranceProducts.objects.get(id=insurance_product_id)
    rate_list=[]
    state=""
#     product_cargo_set = ProductCargo()
#     product_cargo_set =bms_tools.validation_cargo_and_product(insurance_product,cargo_set,product_cargo_set)
    for product_rate in insurance_product.product_rate_list:
        product_cargo_set = ProductCargo.objects(state=product_rate.good_type, product=insurance_product)
        rate_list.append(product_rate.good_type)
        print(rate_list)
        if product_cargo_set:
            a=str(product_rate.good_type)+"已经与货物关联"
            print(a)
#             for product_cargo in product_cargo_set:
#                 product_cargo.cargo.state = False
#                 product_cargo.cargo.save()
        else:
            state = True
#             insurance_product.is_hidden = True
    if state == True:
        insurance_product.is_hidden = True
    else:
         insurance_product.is_hidden = False      
    product_cargo_list = ProductCargo.objects(product=insurance_product)
    for product_cargo_detail in product_cargo_list:
        if product_cargo_detail.state in rate_list:
            continue
        else:
            product_cargo_detail.delete()
            
    return insurance_product


@login_required
@AdminRequired
def insurance_product_edit(request, insurance_product_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_insurance_product', '1')
    data['page_index'] = page_index
    company_set = InsuranceCompany.objects()
    data['tail_companys'] = company_set
    document_set = InsuranceDocument.objects()
    data['documents'] = document_set
    data['product_types'] = InsuranceProducts.PRODUCT_TYPE
    data['insurance_types'] = InsuranceProducts.INSURANCE_TYPE
    insurance_product = InsuranceProducts.objects.get(id=insurance_product_id)
    #2017/5/22添加来源渠道
    data['create_ways'] = InsuranceProducts.CREATE_WAY
    #2017/6/1添加可承包用户类型
    data['user_types'] = InsuranceProducts.USER_TYPE
    if insurance_product:
        data['insurance_product'] = insurance_product
    else:
        request.session['message'] = '未找到对应的保险产品'
        return HttpResponseRedirect(reverse('bms:insurance_product_detail', args=[insurance_product_id, ]))
        #添加中介信息
    intermediary_set = Intermediary.objects.filter(state=True)
    data['intermediary_set'] = intermediary_set
    if request.method == 'POST':
        try:
            insurance_product = bms_tools.validation_insurance_product(insurance_product)
            if request.POST.get('active', '') == 'show':
                insurance_product.is_hidden = False
            else:
                insurance_product.is_hidden = True
            insurance_product.save()
#             insurance_product=check_insurance_cargo( request ,insurance_product.id)
#             insurance_product.save()
            request.session['message'] = '编辑成功'
            return HttpResponseRedirect(reverse('bms:insurance_product_detail', args=[insurance_product_id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/product/insurance_product_edit.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/product/insurance_product_edit.html', data, context)


#－－－－－－－－－－－－－－－－－－－－－－－－－－     优惠券      －－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def coupon_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_coupon'] = search_keyword
        request.session['page_index_coupon'] = 1
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:coupon_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        message = request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_coupon', '')
        coupon_set = Coupon.objects()
        coupon_set = request_tool.coupon_filter(coupon_set=coupon_set, keyword=search_keyword)
        count = coupon_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_coupon'] = paging['page_index']
        coupon_set = coupon_set[paging['start_item']:paging['end_item']]
        data['coupons'] = coupon_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/product/coupon_list.html', data, context)


@login_required
@AdminRequired
def coupon_detail(request, coupon_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_coupon', '1')
    data['page_index'] = page_index
    coupon = Coupon.objects(id=coupon_id).first()
    if coupon:
        data['coupon'] = coupon
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:coupon_list', args=[page_index, ]))
    return render_to_response('bms/product/coupon_detail.html', data, context)


@login_required
@AdminRequired
def coupon_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_coupon', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    product_set = InsuranceProducts.objects()
    data['products'] = product_set
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            coupon = Coupon()
            coupon = bms_tools.validation_coupon(coupon)
            if request.POST.get('active', '') == 'show':
                coupon.is_hidden = False
            else:
                coupon.is_hidden = True
            coupon.save()
            request.session['message'] = '创建成功'
            return HttpResponseRedirect(reverse('bms:coupon_detail', args=[coupon.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            print(traceback.format_exc())
            message=str(e)
            if 'cannot parse date' in message:
                message="日期格式输入不正确，正确输入格式：2016-02-09"
            data['message'] = message
        return render_to_response('bms/product/coupon_create.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/product/coupon_create.html', data, context)


@login_required
@AdminRequired
def coupon_edit(request, coupon_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_coupon', '1')
    data['page_index'] = page_index
    product_set = InsuranceProducts.objects()
    data['products'] = product_set
    coupon = Coupon.objects.get(id=coupon_id)
    if coupon:
        data['coupon'] = coupon
    else:
        request.session['message'] = '未找到对应的优惠券'
        return HttpResponseRedirect(reverse('bms:coupon_detail', args=[coupon_id, ]))
    if request.method == 'POST':
        try:
            coupon = bms_tools.validation_coupon(coupon)
            if request.POST.get('active', '') == 'show':
                coupon.is_hidden = False
            else:
                coupon.is_hidden = True
            coupon.save()
            request.session['message'] = '编辑成功'
            return HttpResponseRedirect(reverse('bms:coupon_detail', args=[coupon_id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/product/coupon_edit.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/product/coupon_edit.html', data, context)


#   发送优惠券用户列表
@login_required
@AdminRequired
def coupon_send_list(request, coupon_id, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    data['coupon_id'] = coupon_id
    coupon = Coupon.objects.get(id=coupon_id)
    if coupon:
        data['coupon'] = coupon
    else:
        request.session['message'] = '未找到对应的优惠券'
        return HttpResponseRedirect(reverse('bms:coupon_detail', args=[coupon_id, ]))
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_coupon'] = search_keyword
        request.session['page_index_coupon'] = 1
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:coupon_send_list', args=[coupon_id, 1, ]) + get_parameter)

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_coupon', '')
        client_set = Client.objects()
        client_set = request_tool.client_filter(client_set=client_set, keyword=search_keyword)
        user_set = User.objects(is_active=True)
        client_set = client_set.filter(user__in=user_set)
        count = client_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_coupon'] = paging['page_index']
        client_set = client_set[paging['start_item']:paging['end_item']]
        data['clients'] = client_set
        # data['message'] = message
        data['count'] = count
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/product/coupon_send_list.html', data, context)


#   发送优惠券
@login_required
@AdminRequired
def coupon_send(request, coupon_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    data['coupon_id'] = coupon_id
    coupon = Coupon.objects.get(id=coupon_id)
    if coupon:
        data['coupon'] = coupon
        couponName =     coupon.name
        coupondescribe = coupon.describe
        couponrate = coupon.rate
    else:
        request.session['message'] = '未找到对应的优惠券'
        return HttpResponseRedirect(reverse('bms:coupon_detail', args=[coupon_id, ]))
    if request.method == 'POST':
        search_keyword = request_tool.get_parameter('modal_search', '')
        client_set = Client.objects()
        client_set = request_tool.client_sent_filter(client_set=client_set, keyword=search_keyword)
        user_set = User.objects(is_active=True)
        client_set = client_set.filter(user__in=user_set)
        
        if client_set:
            test_end='0'
            for client in client_set:
                use_coupon = UseCoupon()
                use_coupon.client = client
                use_coupon.coupon = coupon
                use_coupon.save()
                
                try:
                    content = "恭喜，您已获得"+str(coupondescribe)+",您可以在我的账户优惠券中查询详情，如有需要请联系运之宝客服15910731868"
                    touser = client.wx_id
                    send_wx_message(touser,content)
                except:
                    test_end='1'
            if test_end=='1':
                request_tool.set_message('发送优惠券成功,但由于某些用户未登陆公众号，微信推送发送失败')
            else:
                request_tool.set_message('发送优惠券成功')
            
#             request_tool.set_message('发送优惠券成功')

        else:
            request_tool.set_message('发送失败，请选择用户')
            return HttpResponseRedirect(reverse('bms:coupon_send_list', args=[coupon_id, '1', ]))
        return HttpResponseRedirect(reverse('bms:coupon_detail', args=[coupon_id, ]))

    elif request.method == 'GET':
        return HttpResponseRedirect(reverse('bms:coupon_send_list', args=[coupon_id,'1', ]))


#   发送优惠券记录
@login_required
@AdminRequired
def coupon_send_record(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_coupon_record'] = search_keyword
        request.session['page_index_coupon_record'] = 1
        # state = request_tool.get_parameter("state")
        # get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:coupon_send_record', args=[1, ]))

    elif request.method == 'GET':
        message = request_tool.check_message(data)
        # data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_coupon_record', '')
        coupon_record_set = UseCoupon.objects()
#         for  coupon_record in coupon_record_set:
# #             d1 = datetime.datetime.now()-datetime.timedelta(days = -100)
# #             d2 = coupon_record.coupon.end_date
#             d1 = datetime.datetime.now()
#             d2 = coupon_record.coupon.end_date
#             print((d2-d1).days)
#             if (d2-d1).days == 50:
#                 print(9999999)
#                 content = "您的运之宝账户优惠券还有5天到期，请在我的账户-优惠券查看详情，联系客服获取更多优惠券，运之宝客服15910731868"
#                 touser = coupon_record.client.wx_id
#                 send_wx_message(touser,content)
#             else:
#                 print(7777777)
#                 
        coupon_record_set = request_tool.coupon_record_filter(coupon_record_set=coupon_record_set, keyword=search_keyword)
        count = coupon_record_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_coupon_record'] = paging['page_index']
        coupon_record_set = coupon_record_set[paging['start_item']:paging['end_item']]
        data['coupon_records'] = coupon_record_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/product/coupon_list_record.html', data, context)
    
    

    
#   发送货物类型维护入口
@login_required
@AdminRequired
def cargo_intry(request, page_index):
    data={}
    context = RequestContext(request)
    page_index = int(page_index)
    cargo_set = Cargo.objects()
    #data["cargo_set"]=cargo_set
    bms_tools = DocumentBmsTools(request)
    request_tool = RequestTools(request)
#     #货物大类下拉菜单
#     ct_set=CargoType.objects(ct_state = True)
#     ct_list = ct_set.order_by('ct_priority')
#     data['ct_list'] = ct_list
    if request.method == 'POST':
        request_tool.save_log()
      #  search_keyword = request.POST.get('search_keyword', '')
      #  request.session['search_keyword_car'] = search_keyword
       # request.session['page_index_car'] = page_index
        try:
            data['posted_data'] = request.POST
            cargo_priority = request.POST.get('cargo_priority', '')
            cargo_number = request.POST.get('cargo_number', '')
            cargo_describe = request.POST.get('cargo_describe', '')
            page_index = request.POST.get('cargo_page', '')
            page_index =int(page_index)
            cargo=Cargo()
            cargo = bms_tools.validation_cargo(cargo)
            cargo.save()
            data['posted_data'] =""
            data["cargo_set"]=cargo_set
            return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
        except Exception as e:
            message=str(e)
            request.session['cargo_message'] = message
            return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
    else:
        request_tool.check_message(data)
#         ct_set = CargoType.objects()
#         data['ct_set'] = ct_set
#         count_ct = ct_set.count()
#         a=count_ct%2
#         count_ct1=""
#         if count_ct%2 == 0:
#             count_ct1 ="zero"
#         else:
#             count_ct1 ="one"
#         data["count_ct"]=count_ct1
        
        count = cargo_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_cargo'] = paging['page_index']
        cargo_set = cargo_set[paging['start_item']:paging['end_item']]
        data['paging'] = paging
        data["cargo_set"]=cargo_set
        message = request.session.get('cargo_message', '')
        #ct_detail = request.session.get('ct_detail', '')
        data["message"]=message
        #data["ct_detail"]=ct_detail
        request.session['cargo_message'] = ""
        #request.session['ct_detail'] = ""
    return render_to_response('bms/product/cargo_intry.html', data, context)
    

def cargo_delete(request,cargo_id):
    data={}
    context = RequestContext(request)
    cargo_set = Cargo.objects()
    data["cargo_set"]=cargo_set
#     page_index = request.session.get('page_index_campaign_driver', '1')
#     data['page_index'] = page_index
    if request.method == 'GET':
        cargo_list = Cargo.objects(id=cargo_id).first()
        if cargo_list:
            product_cargo_set = ProductCargo.objects(cargo=cargo_list)
            if product_cargo_set:
                producr_name=''
                for product_cargo_detail in product_cargo_set:
                    producr_name=producr_name+str(product_cargo_detail.product.name)+'、'
                data["message"]="货物与产品:"+producr_name+"已关联，无法删除，已隐藏"
                cargo_list.state=False
                cargo_list.save()
                return render_to_response('bms/product/cargo_intry.html', data, context)
            else:
                try:
                    cargo_list.delete()
                    data["message"]="删除数据成功"
                except Exception as e:
                    data["message"]=str(e)
                return render_to_response('bms/product/cargo_intry.html', data, context)
        else:
            data['message'] = '未找到对应的货物信息'
            return render_to_response('bms/product/cargo_intry.html', data, context)
    return HttpResponseRedirect(reverse('bms:insurance_product_list', args=[1, ]))  
#     return HttpResponseRedirect(reverse('bms:car_list', args=[page_index, ]))

def cargo_edit(request):
    data={}
    context = RequestContext(request)
    bms_tools = DocumentBmsTools(request)
    cargo_set = Cargo.objects()
    data["cargo_set"]=cargo_set
    if request.method == 'POST':
        cargo_id = request.POST.get('cargo_id_edit', '')
        try:
            page_index = request.POST.get('cargo_page', '1')
            page_index =int(page_index)
        except:
            page_index=1
        try:
            cargo = Cargo.objects(id=cargo_id).first()
            cargo = bms_tools.validation_cargo(cargo)
            cargo.save()
            request.session['cargo_message'] = "编辑成功"
            product_cargo_list = ProductCargo.objects(cargo=cargo)
            for product_cargo in product_cargo_list:
                product =product_cargo.product
                product_cargo.delete()
                product.save()
        except CustomError as e:
            request.session['cargo_message']  = e.message
            return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
#             return render_to_response('bms/product/cargo_intry.html', data, context)
        except ParameterError as e:
            request.session['cargo_message'] = e.message
            return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
        except Exception as e:
            request.session['cargo_message'] = str(e)
            return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
            
#     page_index = request.session.get('page_index_campaign_driver', '1')
#     data['page_index'] = page_index
    if request.method == 'GET':
        cargo_set = Cargo.objects()
        data["cargo_set"]=cargo_set
        
        return render_to_response('bms/product/cargo_intry.html', data, context)
    return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
#     return HttpResponseRedirect(reverse('bms:car_list', args=[page_index, ]))

def cargo_add_product(request):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_insurance_product', '1')
    data['page_index'] = page_index
    insurance_product_id = request.POST.get('product_id', '')
    good_type =  request.POST.get('product_rate_name', '')
    bms_tools = DocumentBmsTools(request)
    cargo_list = Cargo.objects(state = True)
    data['cargo_list'] = cargo_list
    product_cargo = ProductCargo.objects()
    data['product_cargo_list'] = product_cargo
    data['insurance_product']=""
    choose_cargo_list = request.REQUEST.getlist("choose_cargo")
    cargo_area_list = CargoArea.objects(level="1")
    data['cargo_area_list'] = cargo_area_list
    try:
        insurance_product = InsuranceProducts.objects(id=insurance_product_id).first()
        data['insurance_product'] = insurance_product
        #check_box_list = request.REQUEST.getlist("choose_cargo")
    except Exception as e:
        data['message'] = str(e)
        return  render_to_response('bms/product/insurance_product_detail.html', data, context)
    if insurance_product and len(choose_cargo_list)>0:
         product_cargo_list=ProductCargo.objects(state=good_type, product=insurance_product)
         product_cargo_list.delete()
         for  choose_cargo in choose_cargo_list:
            try:
                cargo_set = Cargo.objects(cargo_name=choose_cargo).first()
                if cargo_set:
                    product_cargo_set = ProductCargo()
                    product_cargo_set =bms_tools.validation_cargo_and_product(insurance_product,cargo_set,product_cargo_set)
                    product_cargo_set.save()    
                    insurance_product.save()#验证产品状态
                else:
                    data['message'] = '获取货物类型失败，请返回上一级刷新再试 '
                    return render_to_response('bms/product/insurance_product_detail.html', data, context)
            except CustomError as e:
                data['message'] = str(e)
                return render_to_response('bms/product/insurance_product_detail.html', data, context)
            except ParameterError as e:
                data['message'] = str(e)
                return render_to_response('bms/product/insurance_product_detail.html', data, context)
            except Exception as e:
                data['message'] = str(e)
                return render_to_response('bms/product/insurance_product_detail.html', data, context)
    else:
        data['message'] = '未找到对应产品数据 '
        return render_to_response('bms/product/insurance_product_detail.html', data, context)

    return render_to_response('bms/product/insurance_product_detail.html', data, context)



#众安同步地址   
@login_required
@AdminRequired
def cargoArea_sync(request):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_insurance_product', '1')

    #env = "prd"
    #env = "iTest"
    paper_id = settings.ZHONGAN_COMPANY_CODE
    company = InsuranceCompany.objects(paper_id = paper_id).first()
    insurancePlatform = InsurancePlatform.objects(company = company).first()
    for configobj in insurancePlatform.i_config:
               if configobj.c_key == "appKey":
                          appKey = configobj.c_value.strip()
               elif configobj.c_key == "env":
                          env = configobj.c_value.strip()
               elif configobj.c_key == "privatekey":
                          privateKey = configobj.c_value.strip()
               elif configobj.c_key == "version":
                          version = configobj.c_value.strip()
    
    #appKey = "3890efac7ece7a646b18095aa424a9f9"

    #privateKey = '/pss/zhonganUtil/rsa_private_key.pem'

    serviceName = "zhongan.cargo.getAllCargoArea"
    params ={}
    paramsdict = {"param":params
           }
    paramsjson = json.dumps(paramsdict) 
    client = ZhongAnApiClient (env, appKey, privateKey, serviceName, version) 
    response = client.call (paramsjson)
    cargoArea_set = CargoArea.objects()
    if cargoArea_set:
          cargoArea_set.delete()
    cargoAreaDTODict = json.loads(response['bizContent'])
    cargoAreaDTOList = cargoAreaDTODict["cargoAreaDTOList"]

    for cargoareaobj in cargoAreaDTOList:
        cargoarea = CargoArea ()        
        cargoarea.name = cargoareaobj['name']
        cargoarea.code = cargoareaobj["code"]
        cargoarea.level = cargoareaobj["level"]
        cargoarea.parentcode = cargoareaobj["parentcode"]
        cargoarea.save()
    
    request.session['message'] = '众安地址同步已经完成'
    return HttpResponseRedirect(reverse('bms:read_city_detail', args=[page_index, ]))
#     data={} 
#     data["response"]=cargoAreaDTOList
#     return render_to_response('bms/car/car_list.html', data, context)


# @login_required
# @AdminRequired
def read_city_detail(request, page_index):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = int(page_index)
    if request.method == 'POST':
        request_tools.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        city_type = request.POST.get('city_type', '')
        get_parameter = "?city_type={0}&search_keyword={1}".format(city_type, search_keyword)
        return HttpResponseRedirect(reverse('bms:read_city_detail', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        data["get_data"] = request.GET
        city_detail_list = CargoArea.objects()
        search_keyword = request.GET.get("search_keyword", "")
        city_type = request.GET.get("city_type", "")
        if city_type in ['1','2','3']:
            try:
                city_detail_list =city_detail_list.filter(Q(level=city_type))
            except:
                pass
        if search_keyword:
            try:
                city_detail_list =city_detail_list.filter(Q(name__contains=search_keyword) | Q(code__contains=search_keyword) | Q(parentcode__in=search_keyword))
            except:
                pass
        count = city_detail_list.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        city_detail_set = city_detail_list[paging['start_item']:paging['end_item']]
        data['city_detail_list'] = city_detail_set
        data['paging'] = paging
        message = request.session.get('city_message', '')
        data["message"]=message
        request.session['city_message'] = ""
        return render_to_response('bms/product/read_city_detail.html', data, context)



#编辑不保货物
def add_no_insurable_route(request):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_insurance_product', '1')
    data['page_index'] = page_index
    insurance_product_id = request.POST.get('insurable_id', '')
    insurance_product = InsuranceProducts.objects(id=insurance_product_id).first()
    cargo_list = Cargo.objects()
    data['cargo_list'] = cargo_list
    product_cargo = ProductCargo.objects()
    data['product_cargo_list'] = product_cargo
    cargo_area_list = CargoArea.objects(level = '1' )
    data['cargo_area_list'] = cargo_area_list
    if insurance_product:
        data['insurance_product'] = insurance_product
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:insurance_product_list', args=[page_index, ]))
    choose_prov_list = request.REQUEST.getlist("choose_pro")
    prov_list = []
    if len(choose_prov_list)>0:
        try:
#             insurance_product.no_insurable_route =prov_list
            for  prov in choose_prov_list:
                print(prov)
                prov_list.append(prov)
            insurance_product.no_insurable_route =prov_list
            insurance_product.save()
        except Exception as e:
            data['message'] = str(e)     
    elif len(choose_prov_list)==0:
        insurance_product.no_insurable_route =prov_list
        insurance_product.save()
        data['message'] = "已清空不保路线，现产品全国可保 " 
    else:
        data['message'] = '不保省份数据状态错误请稍后再试'
        return render_to_response('bms/product/insurance_product_detail.html', data, context)
    
    return render_to_response('bms/product/insurance_product_detail.html', data, context)

#   货物类型大类维护入口
@login_required
@AdminRequired
def cargo_type_intry(request, page_index):
    data={}
    context = RequestContext(request)
    page_index = int(page_index)
    bms_tools = DocumentBmsTools(request)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        try:
            ct_detail = request.POST
            ct_name = request.POST.get('ct_name', '')
            ct_state = request.POST.get('ct_state', '')
            ct_priority = request.POST.get('ct_priority', '')
            cargotype=CargoType()
            cargotype = bms_tools.validation_cargo_type(cargotype)
            cargotype.save()
            return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
        except Exception as e:
            message=str(e)
            request.session['ct_detail'] = ct_detail
            request.session['cargo_message'] = message
            return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
    else:
        return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
    
    
#   编辑货物大类
@login_required
@AdminRequired
def cargo_type_edit(request, page_index):
    data={}
    context = RequestContext(request)
    page_index = int(page_index)
    bms_tools = DocumentBmsTools(request)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        cargotype_id = request.POST.get('ct_detail_edit', '')
        if not cargotype_id:
            request.session['cargo_message'] = "网络不稳定，未获取到货物大类id信息。"
            return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
        try:
            ct_detail = request.POST
            ct_name = request.POST.get('ct_name', '')
            ct_state = request.POST.get('ct_state', '')
            ct_priority = request.POST.get('ct_priority', '')
            cargotype=CargoType.objects(id=cargotype_id).first()
            cargotype = bms_tools.validation_cargo_type(cargotype)
            cargotype.save()
            if cargotype.ct_state==False:
                cargo_set= Cargo.objects(cargo_type = cargotype)
                for cargo in cargo_set:
                    cargo.state = False
                    cargo.save()
                    product_cargo_list = ProductCargo.objects(cargo=cargo)
                    for product_cargo in product_cargo_list:
                        product =product_cargo.product
                        product_cargo.delete()
                        product.save()
            return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
        except Exception as e:
            message=str(e)
            request.session['ct_detail'] = ct_detail
            request.session['cargo_message'] = message
            return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))
    else:
        return HttpResponseRedirect(reverse('bms:cargo_intry', args=[page_index, ]))

#众安同步地址生成json文件，方便微信端访问
@login_required
@AdminRequired
def cargoArea_json(request):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = 1
    cargo_area_list = CargoArea.objects(level = '1' ).order_by("id")
    area = []
    for cargoareaObj  in cargo_area_list:
        proDict = getDict(cargoareaObj['name'],cargoareaObj["code"])
        cityList = CargoArea.objects(level = '2' ,parentcode=cargoareaObj['code']).order_by("id")
        citySub = []
        for cityObj in cityList:
            cityDict = getDict(cityObj['name'],cityObj["code"])
            areaList = CargoArea.objects(level = '3' ,parentcode=cityObj['code']).order_by("id")
            areaSub = []
            for areaObj in areaList:
                areaDict = getDict(areaObj['name'],areaObj["code"])
                areaSub.append(areaDict)
            cityDict['sub'] = areaSub
            citySub.append(cityDict)
        proDict['sub'] =  citySub
        area.append(proDict)
    file_path = "{0}/static/{1}".format(settings.BASE_DIR, 'cargo_area.json')
    with open(file_path, 'w') as f:
        f.write(json.dumps(area,ensure_ascii=False,indent=2))
    request.session['message'] = '生成json文件成功！'
    return HttpResponseRedirect(reverse('bms:read_city_detail', args=[1, ]))


def getDict(name,code):
    dict = {}
    dict.setdefault("name",name)
    dict.setdefault("code",code)
    return dict


#--------------------------------------------------------中介列表--------------------------------------------------------------------------------
@login_required
@AdminRequired
def intermediary_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_coupon'] = search_keyword
        request.session['page_index_coupon'] = 1
        state = request_tool.get_parameter("state")
        get_parameter = "?state={0}".format(state)
        return HttpResponseRedirect(reverse('bms:intermediary_list', args=[page_index, ]) + get_parameter)

    elif request.method == 'GET':
        message = request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_coupon', '')
        request.session['search_keyword_coupon'] = ''
        intermediary_set = Intermediary.objects()
        if search_keyword:
            intermediary_set = Intermediary.filter(Q(intermediary_name__contains=search_keyword) )
        #coupon_set = Coupon.objects()
        #coupon_set = request_tool.coupon_filter(coupon_set=coupon_set, keyword=search_keyword)
        count = intermediary_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_coupon'] = paging['page_index']
        intermediary_set = intermediary_set[paging['start_item']:paging['end_item']]
        data['intermediary_set'] = intermediary_set
        data['message'] = message
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/product/intermediary_list.html', data, context)
    
    
    
 
@login_required
@AdminRequired
def intermediary_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    tail_company_set = InsuranceCompany.objects.filter(is_hidden=False)
    data['tail_company_set'] = tail_company_set
    #2017添加车牌号和车辆类型
    #车牌号
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新","港","澳","台"]
    data["short_detail"] = short_detail
    #承包车辆类型
    order_car_type =InquiryInfo.ORDER_CAR_TYPE
    data["order_car_type"] = order_car_type
    
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            intermediary = Intermediary()
            intermediary = bms_tools.validation_intermediary(intermediary)
            if request.POST.get('active', '') == 'show':
                intermediary.state = True
            else:
                intermediary.state = False
            intermediary.save()
            request.session['message'] = '创建成功'
            if not intermediary.intermediary_company_list:
                intermediary.state = False
                intermediary.save()
                request.session['message'] = '中介渠道创建成功，由于未勾选承保公司，所以该中介状态只能为未激活状态'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            print(traceback.format_exc())
            message=str(e)
            data['message'] = message
        return render_to_response('bms/product/intermediary_create.html', data, context)
#         data['posted_data'] = request.POST
#         return render_to_response('bms/product/intermediary_detail.html', data, context)

    elif request.method == 'GET':
        return render_to_response('bms/product/intermediary_create.html', data, context)
    
    
@login_required
@AdminRequired
def intermediary_detail(request, intermediary_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    intermediary = Intermediary.objects(id=intermediary_id).first()
    if intermediary:
        data['intermediary'] = intermediary 
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:intermediary_list', args=[page_index, ]))
    #手续费比例回显
    intermediary_rate_list=''
    try:
        intermediary_rate_list = IntermediaryRate.objects(intermediary=intermediary)
    except:
        pass
    data['intermediary_rate_list']=intermediary_rate_list
    #创建中介人员失败信息回显
    posted_data = request.session.get('request_post_data', '')
    data['posted_data'] = posted_data
    #中介人员回显
    intermediary_people = ''
    try:
        intermediary_people = IntermediaryPeople.objects(intermediary = intermediary )
    except:
        intermediary_people = ''
    data['intermediary_people_list']=intermediary_people
    return render_to_response('bms/product/intermediary_detail.html', data, context)


@login_required
@AdminRequired
def intermediary_edit(request, intermediary_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_order', '1')
    data['page_index'] = page_index
    intermediary = Intermediary.objects(id=intermediary_id).first()
    tail_company_set = InsuranceCompany.objects.filter(is_hidden=False)
    data['tail_company_set'] = tail_company_set
    #2017添加车牌号和车辆类型
    #车牌号
    short_detail=["京", "津" ,"冀" ,"晋","蒙","辽","吉","黑","沪","苏","浙","皖","闽","赣","鲁","豫","鄂","湘","粤","桂","琼","川","贵","云","渝","藏","陕","甘","青","宁","新","港","澳","台"]
    data["short_detail"] = short_detail
    #承包车辆类型
    order_car_type =InquiryInfo.ORDER_CAR_TYPE
    data["order_car_type"] = order_car_type
    if intermediary:
        data['intermediary'] = intermediary
       # return render_to_response('bms/product/intermediary_edit.html', data, context)
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:intermediary_list', args=[page_index, ]))
    message1=""
    if request.method == 'POST':
        try:
            intermediary = bms_tools.validation_intermediary(intermediary)
            if request.POST.get('active', '') == 'show':
                intermediary.state = True
            else:
                intermediary.state = False
            intermediary.save()
            if not intermediary.intermediary_company_list:
                intermediary.state = False
                intermediary.save()
                message1="由于未勾选承保公司，"
            #根据中介渠道状态不同修改对应中介人员状态
            if intermediary.state == True:
                request.session['message'] = '编辑成功，可激活对应中介人员登陆权限'
            else:
                intermediary_people_list  = IntermediaryPeople.objects(intermediary=intermediary)
                if intermediary_people_list:
                    for intermediary_people_detail in intermediary_people_list:
                        intermediary_people_detail.user.is_active = False
                        intermediary_people_detail.user.save()
                    request.session['message'] = '编辑成功，'+message1+'当前中介渠道状态为隐藏。已取消其对应的中介人员登陆平台的权限。'
                else:
                    request.session['message'] = '编辑成功。'+message1+'当前中介状态为隐藏'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            print(traceback.format_exc())
            message=str(e)
            data['message'] = message
        return render_to_response('bms/product/intermediary_edit.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/product/intermediary_edit.html', data, context)
    


#中介下保险公司费率
@login_required
@AdminRequired
def intermediary_company_rate(request, intermediary_id):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    bms_tools = DocumentBmsTools(request)
    intermediary = Intermediary.objects(id=intermediary_id).first()
    #验证中介渠道
    if intermediary:
        data['intermediary'] = intermediary
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:intermediary_list', args=[1, ]))
    
    if request.method == 'POST':
        add_company_id=request.POST.get('add_company_id', '')
        liability_process_price=request.POST.get('liability_process_price', '')
        commercial_process_price=request.POST.get('commercial_process_price', '')
        #验证公司
        try:
            add_company_set = InsuranceCompany.objects(id=add_company_id).first()
        except:
            request.session['message'] = '网络延迟，公司信息获取失败，请稍后再试'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary.id, ]))
        #验证中间表个数（区别创建和编辑）
        intermediary_rate_count = IntermediaryRate.objects(intermediary=intermediary,company = add_company_set).count()
        if intermediary_rate_count == 0:
            intermediary_rate_set = IntermediaryRate()
        else:
            intermediary_rate_set = IntermediaryRate.objects(intermediary=intermediary,company = add_company_set).first()
        #验证交强险费率信息
        
        try:
            intermediary_rate_set = bms_tools.validation_intermediary_rate(intermediary_rate_set)
            intermediary_rate_set.intermediary =intermediary
            intermediary_rate_set.save()
            request.session['message'] = '编辑'+add_company_set.name+'手续费比例编辑成功'
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary.id, ]))
        except CustomError as e:
            request.session['message'] = str(e)
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary.id, ]))
        except Exception as e:
            request.session['message'] = str(e)
            return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary.id, ]))
    elif request.method == 'GET':
        return HttpResponseRedirect(reverse('bms:intermediary_detail', args=[intermediary.id, ]))


#－－－－－－－－－－－－－－－－－－－－－－－－－－     中介部分 end     －－－－－－－－－－－－－－－－－－－－－－－－－－

    