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
from bms.tools import DocumentBmsTools
from django.shortcuts import render_to_response, HttpResponse
import traceback
import math
from common.tools_legoo import DocumentTools, DocumentFolderType, ImageTools, ImageFolderType
from common.tools import RequestTools
from common.tools_excel_export import ExcelExportTools
# from openpyxl.reader.excel import load_workbook
# import openpyxl
from django.contrib.staticfiles.templatetags.staticfiles import static
import collections
from common.driver_dict import *
import os
from InsuranceSite import settings
import datetime
#－－－－－－－－－－－－－－－－－－－－－－－－－－     订单列表      －－－－－－－－－－－－－－－－－－－－－－－－－－

@login_required
@AdminRequired
def logistics_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_logistics'] = search_keyword
        request.session['page_index_logistics'] = 1

        start = request.POST.get('start', '')
        end = request.POST.get('end', '')
        request.session['start'] = start
        request.session['end'] = end

        return HttpResponseRedirect(reverse('bms:logistics_list', args=[1, ]))

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_logistics', '')
        logistics_set = LogisticsCompany.objects()
        logistics_set = request_tool.logistics_filter(logistics_set=logistics_set, keyword=search_keyword)

        # for logistics in logistics_set:


        count = logistics_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_logistics'] = paging['page_index']
        logistics_set = logistics_set[paging['start_item']:paging['end_item']]

        data['logisticss'] = logistics_set
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/campaign/logistics_list.html', data, context)


@login_required
@AdminRequired
def logistics_detail(request, logistics_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_logistics_id', '1')
    data['page_index'] = page_index
    logistics = LogisticsCompany.objects(id=logistics_id).first()
    if logistics:
       
        data['logistics'] = logistics
        #处理照片
        a=len(logistics.logistics_image_list)
        i=0
        temp=[]
        temp2=[]
        for logistics_image in logistics.logistics_image_list:
            i=i+1
            temp.append(logistics_image)
            if i%4 == 0:
                temp2.append(temp)
                print(temp2)
                temp=[]
        temp2.append(temp)
        data["logistics_image_list"]=temp2
        if logistics.person:
             contacts = logistics.person.split(";")
             data['contacts'] = contacts
        else:
             data['contacts'] = ''
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:logistics_list', args=[page_index, ]))
    return render_to_response('bms/campaign/logistics_detail.html', data, context)


@login_required
@AdminRequired
def logistics_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_logistics', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            logistics = LogisticsCompany()
            logistics = bms_tools.validation_logistics(logistics)
            logistics.save()
            request.session['message'] = '创建成功'
        except CustomError as e:
            # request.session['message'] = e.message
            data['message'] = e.message
            return render_to_response('bms/campaign/logistics_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            # request.session['message'] = str(e)
            return render_to_response('bms/campaign/logistics_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/campaign/logistics_create.html', data, context)


@login_required
@AdminRequired
def logistics_edit(request, logistics_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_logistics', '1')
    data['page_index'] = page_index
    logistics = LogisticsCompany.objects(id=logistics_id).first()
    if logistics:
        if logistics.person1 or logistics.phone1:
            flag = 1
        else:
             flag = 0
        data['logistics'] = logistics
        data['flag'] = flag
#         data['contacts'] = dict_set
#         data['other_contact'] = dict_jian
        data['special_line_list'] = '-'.join(logistics.special_line_list)
    else:
        request.session['message'] = '未找到对应的物流公司'
        return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics_id, ]))
    if request.method == 'POST':
        try:
            logistics = bms_tools.validation_logistics(logistics)
            logistics.save()
            request.session['message'] = '编辑成功'
            return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/campaign/logistics_edit.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/campaign/logistics_edit.html', data, context)




@login_required
@AdminRequired
def logistics_delete(request, logistics_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_logistics', '1')
    data['page_index'] = page_index
    logistics = LogisticsCompany.objects(id=logistics_id).first()
    if logistics:
        try:
            logistics.delete()
            request.session['message'] = '删除成功'
            return HttpResponseRedirect(reverse('bms:logistics_list', args=[1, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics.id, ]))
    else:
        request.session['message'] = '未找到对应的物流公司'
        return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics_id, ]))
    
    
    
    
    
# 添加物流公司号
@login_required
@AdminRequired
def add_logistics_pic(request, logistics_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    bms_tools = DocumentBmsTools(request)
    logistics = LogisticsCompany.objects(id=logistics_id).first()
    if not logistics:
        request_tools.set_message("未找到对应订单")
        return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics_id, ]))
    if request.method == 'POST':
        try:
            image_tool = ImageTools()
            logistics_image_list = request.FILES.getlist('add_logistics_image_pic', '')
            if logistics_image_list:
                for logistics_image in logistics_image_list:
                    logistics_image_url = image_tool.save(request_file=logistics_image, file_folder=ImageFolderType.logistics, old_file='')
                    if not logistics_image_url:
                        request_tools.set_message(logistics.paper_id+'生成图片地址失败')
                        return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics_id, ]))
                    else:
                        logistics.logistics_image_list.append(logistics_image_url)
            else:
                request_tools.set_message('请选择物流公司图片')
                return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics_id, ]))
            logistics.save()
            request_tools.set_message("操作成功")
            return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics.id, ]))
        except ParameterError as e:
            # 初始化错误信息
            request_tools.set_message(e.message)
            return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics.id, ]))
    elif request.method == 'GET':
        request_tools.check_message(data)
        data['logistics'] = logistics
        data['logistics_id'] = logistics_id
        return render_to_response('bms/campaign/logistics_detail.html', data, context)




# 修改物流公司图片
@login_required
@AdminRequired
def edit_logistics_pic(request, logistics_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    bms_tools = DocumentBmsTools(request)
    logistics = LogisticsCompany.objects(id=logistics_id).first()
    if logistics:
        try:
            logistics_image = request.FILES.get('logistics_image_edit', '')
            old_url = request.POST.get('image_url_edit')
            position = -1
            for i in range(len(logistics.logistics_image_list)):
                if str(logistics.logistics_image_list[i]) == old_url:
                    position = i
                    break
            if position < 0:
                raise ParameterError('要修改图片不存在')
            if logistics_image:
                image_tool = ImageTools()
                logistics_image_url = image_tool.save(request_file=logistics_image, file_folder=ImageFolderType.insurance, old_file=old_url)
                if logistics_image_url:
                    logistics.logistics_image_list[position] = logistics_image_url
                else:
                    raise ParameterError('生成图片地址失败')
            else:
                raise ParameterError('未选择图片，请选择图片')
            logistics.save()
            # 创建成功
            request.session['message'] = '编辑成功'
        except ParameterError as e:
            request.session['message'] = '编辑图片失败:{0}'.format(e.message)
            return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics.id, ]))
        return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics.id, ]))
    else:
        request.session['message'] = '未找到对应保险公司'
        return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics.id, ]))
    
    
    #删除物流公司图片
def delete_logistics_pic(request, logistics_id):
    context = RequestContext(request)
    image_url = request.POST.get('image_detail_url_delete', '')
    if image_url:
        try:
            image_tools = ImageTools()
            image_tools.delete(image_url)
            logistics = LogisticsCompany.objects(id=logistics_id).first()
            logistics.logistics_image_list.remove(image_url)
            logistics.save()
        except Exception as e:
            request.session['message'] = '删除失败：{0}'.format(e)
    else:
        request.session['message'] = '未找到对应图片'
    return HttpResponseRedirect(reverse('bms:logistics_detail', args=[logistics_id, ]))






@login_required
@AdminRequired
def campaign_lawyer_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        request.session['search_keyword_campaign_lawyer'] = search_keyword
        request.session['page_index_campaign_lawyer'] = 1
        return HttpResponseRedirect(reverse('bms:campaign_lawyer_list', args=[1, ]))

    elif request.method == 'GET':
        request_tool.check_message(data)
        data["get_data"] = request.GET
        search_keyword = request.session.get('search_keyword_campaign_lawyer', '')
        campaign_lawyer_set = CampaignLawyer.objects()
        campaign_lawyer_set = request_tool.campaign_lawyer_filter(campaign_lawyer_set=campaign_lawyer_set, keyword=search_keyword)

        count = campaign_lawyer_set.count()
        page = PageTools()
        paging = page.get_paging(5, page_index, count)
        request.session['page_index_campaign_lawyer'] = paging['page_index']
        campaign_lawyer_set = campaign_lawyer_set[paging['start_item']:paging['end_item']]

        data['campaign_lawyers'] = campaign_lawyer_set
        data['search_keyword'] = search_keyword
        data['paging'] = paging
        return render_to_response('bms/campaign/campaign_lawyer_list.html', data, context)


@login_required
@AdminRequired
def campaign_lawyer_detail(request, campaign_lawyer_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_campaign_lawyer_id', '1')
    data['page_index'] = page_index
    campaign_lawyer = CampaignLawyer.objects(id=campaign_lawyer_id).first()
    if campaign_lawyer:
        data['campaign_lawyer'] = campaign_lawyer
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:campaign_lawyer_list', args=[page_index, ]))
    return render_to_response('bms/campaign/campaign_lawyer_detail.html', data, context)


@login_required
@AdminRequired
def campaign_lawyer_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_campaign_lawyer', '1')
    data['page_index'] = page_index
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            campaign_lawyer = CampaignLawyer()
            campaign_lawyer = bms_tools.validation_campaign_lawyer(campaign_lawyer)
            campaign_lawyer.save()
            request.session['message'] = '创建成功'
        except CustomError as e:
            # request.session['message'] = e.message
            data['message'] = e.message
            return render_to_response('bms/campaign/campaign_lawyer_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            # request.session['message'] = str(e)
            return render_to_response('bms/campaign/campaign_lawyer_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:campaign_lawyer_detail', args=[campaign_lawyer.id, ]))

    elif request.method == 'GET':
        return render_to_response('bms/campaign/campaign_lawyer_create.html', data, context)


@login_required
@AdminRequired
def campaign_lawyer_edit(request, campaign_lawyer_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_campaign_lawyer', '1')
    data['page_index'] = page_index
    campaign_lawyer = CampaignLawyer.objects(id=campaign_lawyer_id).first()
    if campaign_lawyer:
        data['campaign_lawyer'] = campaign_lawyer
    else:
        request.session['message'] = '未找到对应的物流公司'
        return HttpResponseRedirect(reverse('bms:campaign_lawyer_detail', args=[campaign_lawyer_id, ]))
    if request.method == 'POST':
        try:
            campaign_lawyer = bms_tools.validation_campaign_lawyer(campaign_lawyer)
            campaign_lawyer.save()
            request.session['message'] = '编辑成功'
            return HttpResponseRedirect(reverse('bms:campaign_lawyer_detail', args=[campaign_lawyer.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/campaign/campaign_lawyer_edit.html', data, context)
    elif request.method == 'GET':
        return render_to_response('bms/campaign/campaign_lawyer_edit.html', data, context)




@login_required
@AdminRequired
def campaign_lawyer_delete(request, campaign_lawyer_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_campaign_lawyer', '1')
    data['page_index'] = page_index
    campaign_lawyer = CampaignLawyer.objects(id=campaign_lawyer_id).first()
    if campaign_lawyer:
        try:
            campaign_lawyer.delete()
            request.session['message'] = '删除成功'
            return HttpResponseRedirect(reverse('bms:campaign_lawyer_list', args=[1, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return HttpResponseRedirect(reverse('bms:campaign_lawyer_detail', args=[campaign_lawyer.id, ]))
    else:
        request.session['message'] = '未找到对应的物流公司'
        return HttpResponseRedirect(reverse('bms:campaign_lawyer_detail', args=[campaign_lawyer_id, ]))
    
    
@login_required
@AdminRequired
def driver_list(request, page_index):
    context = RequestContext(request)
    data = {}
    page_index = int(page_index)
    request_tool = RequestTools(request)
    data['car_type'] = Trucker.Driver_Car_Type
    data['car_length'] = Trucker.Driver_Car_Length
    #获取激活状态的认证司机
    user_set = User.objects(is_active=True)
    driver_set = Client.objects(user_type='driver').filter(user__in=user_set)
    if request.method == 'POST':
        request_tool.save_log()
        search_keyword = request.POST.get('search_keyword', '')
        car_type = request.POST.get('car_type', '')
        car_length = request.POST.get('car_length', '')
        trucker_set = Trucker.objects()
#         roadList = RoadList.objects.filter(start_line=keyword end_line=keyword)
        if search_keyword or car_type or car_length:
            trucker_set = request_tool.wx_driver_filter(trucker_set=trucker_set, keyword=search_keyword,car_type=car_type,car_length=car_length)
        data['search_keyword'] = search_keyword
    elif request.method == 'GET':
        trucker_set = Trucker.objects()
    count = trucker_set.count()
    page = PageTools()
    paging = page.get_paging(5, page_index, count)
    trucker_set = trucker_set[paging['start_item']:paging['end_item']]
    data['campaign_trucker'] = trucker_set
    data['driver_set'] = driver_set
    data['paging'] = paging
    return render_to_response('bms/campaign/driver_list.html', data, context)
    
@login_required
@AdminRequired
def driver_create(request):
    context = RequestContext(request)
    data = {}
    page_index = request.session.get('page_index_campaign_driver', '1')
    data['page_index'] = page_index
    data['car_type'] = Trucker.Driver_Car_Type
    data['car_length'] = Trucker.Driver_Car_Length
    bms_tools = DocumentBmsTools(request)
    bms_tools.check_message(data)
    if request.method == 'POST':
        data['posted_data'] = request.POST
        try:
            truckers = Trucker()
            trucker = bms_tools.validation_campaign_truckers(truckers)
            trucker.save()
            request.session['message'] = '创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/campaign/driver_create.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            # request.session['message'] = str(e)
            return render_to_response('bms/campaign/driver_create.html', data, context)
        return HttpResponseRedirect(reverse('bms:campaign_driver_list', args=[page_index, ]))
    elif request.method == 'GET':
        return render_to_response('bms/campaign/driver_create.html', data, context)
    
@login_required
@AdminRequired
def driver_delete(request, driver_id):
    data = {}
    page_index = request.session.get('page_index_campaign_driver', '1')
    data['page_index'] = page_index
    driver = Trucker.objects(id=driver_id).first()
    if driver:
        try:
            if driver.user_image:           #删除头像
                path = settings.MEDIA_ROOT +"/"+ driver.user_image
                if os.path.exists(path):
                    os.remove(path)
            driver.delete()
            request.session['message'] = '删除成功'
            return HttpResponseRedirect(reverse('bms:campaign_driver_list', args=[page_index]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return HttpResponseRedirect(reverse('bms:campaign_driver_list', args=[page_index]))
    else:
        request.session['message'] = '未找到对应的货车司机'
        return HttpResponseRedirect(reverse('bms:campaign_driver_list', args=[page_index]))
    
    
@login_required
@AdminRequired
def driver_detail(request, driver_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    request_tools.check_message(data)
    page_index = request.session.get('page_index_campaign_driver', '1')
    data['page_index'] = page_index
    trucker = Trucker.objects(id=driver_id).first()
    if trucker:
        for k,v in Trucker.Driver_Car_Type:
            if int(k) == int(trucker.car_type):
                data['car_type_text']  = v
        for k,v in  Trucker.Driver_Car_Length:
            if int(k) == int(trucker.car_length):
                data['car_length_text']  = v       
        data['campaign_trucker'] = trucker
        car_age=CountCarAge(trucker.car_init_date)
        data['car_age']=car_age
    else:
        request.session['message'] = '未找到对应数据'
        return HttpResponseRedirect(reverse('bms:campaign_driver_list', args=[page_index]))
    return render_to_response('bms/campaign/driver_detail.html', data, context)
#计算车龄
def  CountCarAge(test):
    try:
        date = test.split('-')
        now = datetime.datetime.now()
        oneYearAgo = (datetime.datetime.now() - datetime.timedelta(days = 365)).strftime("%Y-%m-%d ")
        i=0
        for  num in range(0,70):
            IYearAgo=(datetime.datetime.now() - datetime.timedelta(days = 365*num )).strftime("%Y-%m-%d ")
            if test >IYearAgo:
                age=num-1
                if age<0:
                    age=0
                return age
    except:
        return "计算车龄出错，\n请检查初次登记日期，\n格式应为2015-01-08"
                
# #计算车龄
# def CalculateCarAge( date):
#         '''Calculates the age'''
#         try:
#             date = date.split('-')
#             initDate = datetime.date(int(date[0]), int(date[1]), int(date[2]))
#             Today = datetime.date.today()
#             if (Today.getFullYear()==initDate[1] and  (Today.getMonth()+1)== initDate[3] and Today.getDate()==initDate[4]) : 
#                       curyear   =   myDate.getFullYear();   
#                       year = curyear - initDate[1]; 
#                       curmonth = myDate.getMonth()+1;
#                       month = curmonth-initDate[3];
#                       curdate = myDate.getDate();
#                       date = curdate-initDate[4];
#                       if (year == 0):
#                             document.getElementById("id_car_age").value = 0;
#                       elif (year >=1):
#                             if (month == 0):
#                                 if (date<0):
#                                           document.getElementById("id_car_age").value = year-1
#                                 else:
#                                          document.getElementById("id_car_age").value = year
#                             elif(month <0) :
#                                 document.getElementById("id_car_age").value = year-1
#                             else:
#                                 document.getElementById("id_car_age").value = year
#         except:
#             return 'Wrong date format'
        
@login_required
@AdminRequired
def driver_edit(request, driver_id):
    context = RequestContext(request)
    data = {}
    bms_tools = DocumentBmsTools(request)
    page_index = request.session.get('page_index_campaign_driver', '1')
    data['page_index'] = page_index
    data['car_type'] = Trucker.Driver_Car_Type
    data['car_length'] = Trucker.Driver_Car_Length
    truckers = Trucker.objects(id=driver_id).first()
    if not truckers:
        request.session['message'] = '未找到对应的司机信息'
        return HttpResponseRedirect(reverse('bms:campaign_driver_list', args=[page_index ]))
    data['posted_data'] = truckers
    str = ""
    for special_line in truckers.special_line_list:
        str = str+ special_line.start_line+"-"+special_line.end_line+" "
    data['posted_data']['special_line_list'] =  str
    data['car_age'] = CountCarAge(truckers.car_init_date)
    if request.method == 'POST':
        try:
            truckers = bms_tools.validation_campaign_truckers(truckers)
            truckers.save()
            request.session['message'] = '编辑成功'
            return HttpResponseRedirect(reverse('bms:campaign_driver_detail', args=[truckers.id, ]))
        except CustomError as e:
            data['message'] = e.message
        except Exception as e:
            data['message'] = str(e)
        return render_to_response('bms/campaign/driver_create.html', data, context)
    elif request.method == 'GET':
        data['driver_id'] = driver_id

        return render_to_response('bms/campaign/driver_create.html', data, context)
    
@login_required
@AdminRequired
def related_user(request):
    page_index = request.session.get('page_index_campaign_driver', '1')
    if request.method == 'POST':
        id = request.POST.get('id')
        urz = request.POST.get('urz')
    truckers = Trucker.objects(id=id).first()
    if not truckers:
        request.session['message'] = '未找到对应的司机信息'
        return HttpResponseRedirect(reverse('bms:campaign_driver_list', args=[page_index ]))
    client = Client.objects(id=urz).first()
    truckers.client = client
    truckers.save()
    return HttpResponseRedirect(reverse('bms:campaign_driver_list', args=[page_index ]))
    
    
@login_required
@AdminRequired
def cancel_related_user(request):
    page_index = request.session.get('page_index_campaign_driver', '1')
    if request.method == 'POST':
        id = request.POST.get('id')
        urz = request.POST.get('urz')
    truckers = Trucker.objects(id=id).first()
    if not truckers:
        request.session['message'] = '未找到对应的司机信息'
        return HttpResponseRedirect(reverse('bms:campaign_driver_list', args=[page_index ]))
    truckers.client = client
    truckers.save()
    return HttpResponseRedirect(reverse('bms:campaign_driver_list', args=[page_index ]))


















