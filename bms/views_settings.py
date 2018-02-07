__author__ = 'mlzx'
from django.contrib.auth.decorators import login_required
from common.decorators import SuperAdminRequired
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
import traceback
from common.tools import RequestTools, ConvertTools
# try:
#     from common.models import SiteSettings
# except ImportError:
#     from common.models import BaseSettings as SiteSettings
from common.models import SiteSettings
from common.interface_helper import *
from django.shortcuts import render_to_response, HttpResponse
from common.models import *
from bms.tools import DocumentBmsTools
from django.views.decorators.csrf import csrf_exempt 
from common.tools_legoo import DocumentTools, DocumentFolderType, ImageTools, ImageFolderType
import json

# Create your views here.
@login_required
@SuperAdminRequired
def settings_index(request):
    context = RequestContext(request)
    data = {}
    return render_to_response('bms/settings/settings.html', data, context)


@login_required
@SuperAdminRequired
def settings_base(request):
    context = RequestContext(request)
    data = {}
    data['SERVER_URL'] = getattr(settings, 'SERVER_URL', "")
    data['APP_NAME'] = getattr(settings, 'APP_NAME', "")
    data['COPYRIGHT'] = getattr(settings, 'COPYRIGHT', "")
    data['HTTP_CONNECTION_TIME_OUT'] = getattr(settings, 'HTTP_CONNECTION_TIME_OUT', "")
    data['DEBUG'] = getattr(settings, 'DEBUG', "")
    return render_to_response('bms/settings/settings/django.html', data, context)


@login_required
@SuperAdminRequired
def settings_database(request):
    context = RequestContext(request)
    data = {}
    tools_request = RequestTools(request)
    setting = SiteSettings.get_settings()
    data['setting'] = setting
    settings_type = tools_request.get_parameter("type")
    data["settings_type"] = settings_type
    data['setting_name'] = SiteSettings.get_setting_name()
    debug = ConvertTools.is_boolean(tools_request.get_parameter("debug"))
    data["debug"] = debug
    data["product_list"]=[]
    if settings_type == "push":
        data["title"] = "推送设置"
        data["attrs"] = SiteSettings.get_push_attrs(debug)
    elif settings_type == "sms":
        data["title"] = "短信设置"
        data["attrs"] = SiteSettings.get_sms_attrs(debug)
    elif settings_type == "pay":
        data["title"] = "支付设置"
        data["attrs"] = SiteSettings.get_pay_attrs(debug)
    elif settings_type == "other":
        data["title"] = "其他设置"
        data["attrs"] = SiteSettings.get_other_attrs(debug)
        #2017/11/14添加筛选产品部分
        try:
            insurance_product_set = InsuranceProducts.objects()
            insurance_product_set = insurance_product_set.filter(is_hidden=False,product_type='car',create_way="yzb")
            data["product_list"]=insurance_product_set
        except:
            pass
    elif settings_type == "email":
        data["title"] = "邮件设置"
        data["attrs"] = SiteSettings.get_email_attrs(debug)
    else:
        return HttpResponseRedirect(reverse("bms:settings"))
    return render_to_response('bms/settings/settings/database.html', data, context)


@login_required
@SuperAdminRequired
def settings_database_save(request):
    context = RequestContext(request)
    data = {}
    tools_request = RequestTools(request)
    setting = SiteSettings.get_settings()
    if request.method == "POST":
        tools_request.save_log()
        value = request.POST.get('value')
        setting_attr = request.POST.get('attr')
        setting_type = request.POST.get('type')
        try:
            attr = getattr(setting, setting_attr, None)
            if isinstance(attr, bool):
                if value in ['True', 'true', 'TRUE', '1', 'on', '是', '开', '开启']:
                    value = True
                else:
                    value = False
                    print(value)
            elif isinstance(attr, float):
                value = float(value)
            elif isinstance(attr, int):
                value = int(value)
            setattr(setting, setting_attr, value)
            setting.save()
        except Exception as e:
            print(traceback.format_exc())
            return JsonResult(code=CODE_ERROR, message='参数错误', data=data).response()
        data['value'] = ConvertTools.show_value(getattr(setting, setting_attr, None))
        return JsonResult(code=CODE_SUCCESS, data=data).response()
    else:
        return HttpResponseRedirect(reverse("bms:settings"))


@login_required
@SuperAdminRequired
def debug_model(request):
    context = RequestContext(request)
    data = {}
    data['DEBUG'] = getattr(settings, 'DEBUG', "")
    return render_to_response('bms/settings/developer/debug_model.html', data, context)



@login_required
@SuperAdminRequired
def user_protocol(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    site_settings = SiteSettings.get_settings()
    data['setting'] = site_settings
    if request.method == 'POST':
        try:
            request_tool.save_log()
            content = request_tool.get_parameter("content")
            if content:
                site_settings.update(set__user_protocol=content)
            else:
                raise ParameterError("html不能为空")
        except CustomError as e:
            request.session['message'] = e.message
        except Exception as e:
            request.session['message'] = str(e)
        return HttpResponseRedirect(reverse('bms:settings_user_protocol'))
    return render_to_response('bms/settings/settings/user_protocol.html', data, context)


def user_protocol_preview(request):
    site_settings = SiteSettings.get_settings()
    return HttpResponse(site_settings.user_protocol)


#物流平台
@login_required
@SuperAdminRequired
def settings_platform(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    platform_set = Logistics.objects()
    data['platforms'] = platform_set
    if request.method == 'POST':
        try:
            logistics = Logistics()
            platform_name = request_tool.get_parameter('platform_name', '')
            if platform_name:
                logistics.name = platform_name
            else:
                raise ParameterError('物流平台名称不能为空')
            platform_key = request_tool.get_parameter('platform_key', '')
            if platform_key:
                logistics.platform_key = platform_key
            else:
                raise ParameterError('物流平台key不能为空')
            secret = request_tool.get_parameter('platform_secret', '')
            if secret:
                logistics.platform_secret = secret
            else:
                raise ParameterError('物流平台secret不能为空')
            logistics.save()
        except CustomError as e:
            request.session['message'] = e.message
        except Exception as e:
            request.session['message'] = str(e)
        return HttpResponseRedirect(reverse('bms:settings_platform'))
    else:
        return render_to_response('bms/settings/settings/platform.html', data, context)


#编辑物流平台
@login_required
@SuperAdminRequired
def edit_platform(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    platform_set = Logistics.objects()
    data['platforms'] = platform_set
    if request.method == 'POST':
        try:
            platform_id = request_tool.get_parameter('platform_modal', '')
            print(platform_id)
            # print(1111111111111111111111111)
            # 5711f24eb431cc12b5730699
            if platform_id:
                logistics = Logistics.objects(id=platform_id).first()
                if not logistics:
                    raise ParameterError('物流平台不存在')
            else:
                raise ParameterError('未找到对应的物流平台')
            platform_name = request_tool.get_parameter('platform_name_edit', '')
            if platform_name:
                logistics.name = platform_name
            else:
                raise ParameterError('物流平台名称不能为空')
            platform_key = request_tool.get_parameter('platform_key_edit', '')
            if platform_key:
                logistics.platform_key = platform_key
            else:
                raise ParameterError('物流平台key不能为空')
            secret = request_tool.get_parameter('platform_secret_edit', '')
            if secret:
                logistics.platform_secret = secret
            else:
                raise ParameterError('物流平台secret不能为空')
            logistics.save()
        except CustomError as e:
            request.session['message'] = e.message
        except Exception as e:
            request.session['message'] = str(e)
        return HttpResponseRedirect(reverse('bms:settings_platform'))
    else:
        return render_to_response('bms/settings/settings/platform.html', data, context)
    
    
    
    
    
    
#添加保险平台配置
@login_required
@SuperAdminRequired
def insurance_platform(request):
    context = RequestContext(request)
    data = {}
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    tail_company_set = InsuranceCompany.objects()
    data['tail_companys'] = tail_company_set
    insurance_set = InsurancePlatform.objects()
    data['platforms'] = insurance_set
    if request.method == 'POST':
        print(999999999999999)
        try:
            insurancePlatform = InsurancePlatform()
            insurance_name = request_tool.get_parameter('insurance_name', '')
            if insurance_name:
                    insuranceCompany= InsuranceCompany.objects(id=insurance_name).first()
                    insurance_same = InsurancePlatform.objects(company=insuranceCompany).first()
                    if insurance_same:
                        raise ParameterError('保险公司配置已经存在')
                    else:
                        insurancePlatform.company = insuranceCompany
            else:
                raise ParameterError('保险公司名称不能为空')
            position_list = request.POST.getlist('position')
            if len(position_list) > 0:
                    for position in position_list:
                        try:
                            configkey = request.POST.get("configkey_" + position)
                            configvalue = request.POST.get("configvalue_" + position)
                            configures = ConfigureList()
                            if configkey:
                                configures.c_key = configkey
                            else:
                                raise ParameterError('配置项不能为空')
                            if configvalue:
                                configures.c_value = configvalue
                            else:
                                raise ParameterError('配置项的值不能为空')
                           
                            insurancePlatform.i_config.append(configures)
                        except ParameterError as e:
                            raise e
                        except Exception as e:
                            pass
            insurancePlatform.save()
        except CustomError as e:
            request.session['message'] = e.message
        except Exception as e:
            request.session['message'] = str(e)
        return HttpResponseRedirect(reverse('bms:insurance_platform'))
    else:
        return render_to_response('bms/settings/settings/insurance.html', data, context)
    
#编辑保险公司平台
@login_required
@SuperAdminRequired
def edit_insurance(request,platform_id):
    context = RequestContext(request)
    data = {}
    platform_id=platform_id
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    insurance_set = InsurancePlatform.objects()
    data['platforms'] = insurance_set
    if request.method == 'POST':
        try:
            insurance_id = request_tool.get_parameter('insurance_modal', '')
            print(insurance_id)
            if insurance_id:
                insurances = InsurancePlatform.objects(id=insurance_id).first()
                if not insurances:
                    raise ParameterError('保险平台不存在')
            else:
                raise ParameterError('未找到对应的保险平台')
            insurance_name = request_tool.get_parameter('insurance_name_edit_'+insurance_id, '')
            if insurance_name:
                insurances.i_name = insurance_name
#             else:
#                 raise ParameterError('保险公司名称不能为空')
            insurances.i_config=[]
            test='position_edit_'+insurance_id
            position_list = request.POST.getlist(test)
            if len(position_list) > 0:
                    print(" len(position_list) "+str( len(position_list)) )
                    for position in position_list:
                        try:
                            configkey = request.POST.get("configkey_" +insurance_id+"_"+ position)
                            configvalue = request.POST.get("configvalue_" +insurance_id+"_"+ position)
                            configures = ConfigureList()
                            if configkey:
                                configures.c_key = configkey
                            else:
                                raise ParameterError('配置项不能为空')
                            if configvalue:
                                configures.c_value = configvalue
                            else:
                                raise ParameterError('配置项的值不能为空')
                            insurances.i_config.append(configures)
                        except ParameterError as e:
                            raise e
                        except Exception as e:
                            pass
            insurances.save()
        except CustomError as e:
            request.session['message'] = e.message
        except Exception as e:
            request.session['message'] = str(e)
        return HttpResponseRedirect(reverse('bms:insurance_platform'))
    else:
        return render_to_response('bms/settings/settings/insurance.html', data, context)
    
    

#删除保险公司平台
@login_required
@SuperAdminRequired
def insurance_delete(request,platform_id):
    context = RequestContext(request)
    data = {}
    platform_id=platform_id
    request_tool = RequestTools(request)
    request_tool.check_message(data)
    tail_company_set = InsuranceCompany.objects()
    data['tail_companys'] = tail_company_set
    insurance_set = InsurancePlatform.objects()
    data['platforms'] = insurance_set
    if request.method == 'GET':
        insurances = InsurancePlatform.objects(id=platform_id).first()
        if insurances:
            insurances.delete()
        else:
            raise ParameterError('未找到对应的保险平台')
    return render_to_response('bms/settings/settings/insurance.html', data, context)

#平台产品维护
@login_required
@SuperAdminRequired
def platform_product(request):
    context = RequestContext(request)
    data = {}
    data['product_types'] = PlatformProducts.PRODUCT_TYPE
    bms_tools = DocumentBmsTools(request)
    if  request.method == 'GET':
        platformProducts_set = PlatformProducts.objects()
        data['platformProducts_set'] = platformProducts_set
        return render_to_response('bms/settings/settings/platform_product.html', data, context)

#创建平台产品
@login_required
@SuperAdminRequired
def platform_product_create(request):
    context = RequestContext(request)
    data = {}
    data['product_types'] = PlatformProducts.PRODUCT_TYPE
    bms_tools = DocumentBmsTools(request)
    if request.method == 'POST':
        content = request.POST.get("content" )
        data['posted_data'] = request.POST
        try:
            platformProducts = PlatformProducts()
            product = bms_tools.validation_platform_products(platformProducts,content)
            platformProducts = PlatformProducts.objects(product_type=product.product_type).first()
            if platformProducts:
                if product.product_type !='ywx':
                    data['message'] = '产品类型已存在，不允许重复'
                    return render_to_response('bms/settings/settings/platform_product_add.html', data, context)
            priorityProducts = PlatformProducts.objects(priority=product.priority).first()
            if priorityProducts:
                data['message'] = '优先级已使用，不允许重复，请更换！'
                return render_to_response('bms/settings/settings/platform_product_add.html', data, context)
            product.save()
            request.session['message'] = '创建成功'
        except CustomError as e:
            data['message'] = e.message
            return render_to_response('bms/settings/settings/platform_product_add.html', data, context)
        except Exception as e:
            print(traceback.format_exc())
            data['message'] = str(e)
            return render_to_response('bms/settings/settings/platform_product_add.html', data, context)
        return HttpResponseRedirect(reverse('bms:platform_product_list', args=[ ]))
    elif request.method == 'GET':
         return render_to_response('bms/settings/settings/platform_product_add.html', data, context)
     
#删除平台产品
@login_required
@SuperAdminRequired
def platform_product_delete(request,product_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    platformProducts = PlatformProducts.objects(id=product_id).first()
    if platformProducts:
            platformProducts.delete()
            return HttpResponseRedirect(reverse('bms:platform_product_list', args=[]))
    else:
        request.session['message'] = '未找到待删除对象！'
        return HttpResponseRedirect(reverse('bms:platform_product_list', args=[]))
    
#查看平台产品
@login_required
@SuperAdminRequired
def platform_product_detail(request,product_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    platformProducts = PlatformProducts.objects(id=product_id).first()
    if platformProducts:
        data['platformProducts'] = platformProducts
        return render_to_response('bms/settings/settings/platform_product_detail.html', data, context)
    else:
        request.session['message'] = '未找到待查看对象！'
        return HttpResponseRedirect(reverse('bms:platform_product_list', args=[]))
    
#编辑平台产品
@login_required
@SuperAdminRequired
def platform_product_edit(request,product_id):
    context = RequestContext(request)
    data = {}
    request_tools = RequestTools(request)
    platformProducts = PlatformProducts.objects(id=product_id).first()
    if platformProducts:
        data['product_types'] = PlatformProducts.PRODUCT_TYPE
        data['platformProducts'] = platformProducts
        bms_tools = DocumentBmsTools(request)
        if request.method == 'POST':
            content = request.POST.get("content" )
            try:
                product = bms_tools.validation_platform_products(platformProducts,content)
                pself = PlatformProducts.objects(product_type=product.product_type,id=product_id)
                print (product.product_type)
                if  product.product_type != 'ywx':
                    platformProductList = PlatformProducts.objects(product_type=product.product_type)
                    if platformProductList.count() - pself.count() == 1:
                        data['message'] = '产品类型已存在，不允许重复'
                        return render_to_response('bms/settings/settings/platform_product_edit.html', data, context)
                
                priorityself = PlatformProducts.objects(priority=product.priority,id=product_id)
                priorityProductList = PlatformProducts.objects(priority=product.priority)
                if priorityProductList.count() - priorityself.count() == 1:
                    data['message'] = '优先级已使用，不允许重复，请更换！'
                    return render_to_response('bms/settings/settings/platform_product_edit.html', data, context)
                product.save()
                request.session['message'] = '修改成功'
            except CustomError as e:
                data['message'] = e.message
                return render_to_response('bms/settings/settings/platform_product_edit.html', data, context)
            except Exception as e:
                print(traceback.format_exc())
                data['message'] = str(e)
                return render_to_response('bms/settings/settings/platform_product_edit.html', data, context)
            data['platformProducts'] = platformProducts
            return render_to_response('bms/settings/settings/platform_product_detail.html', data, context)
           # return HttpResponseRedirect(reverse('bms:platform_product_list', args=[ ]))
        elif request.method == 'GET':
             return render_to_response('bms/settings/settings/platform_product_edit.html', data, context)
                                                            
@csrf_exempt
def uploadImg(request):
     if request.method=='POST':        
        dict_tmp = {}                                                           #kindeditor定义了返回的方式是json，                                         
        try:
            image_tool = ImageTools()
            pro_image = request.FILES.get('imgFile', '')
            if pro_image:
                    image_url = image_tool.save(request_file=pro_image, file_folder=ImageFolderType.proeditor, old_file='')
            else:
                dict_tmp['error']="1"                                              #失败{ "error":0, "message": "初始化错误信息"}
                dict_tmp['message']="请选择要上传的图片"                                              
                return HttpResponse(json.dumps(dict_tmp))
            dict_tmp['error']=0                                                     #成功{ "error":0, "url": "/static/image/filename"}
            dict_tmp['url']="/static/"+image_url
            return HttpResponse(json.dumps(dict_tmp))
        except ParameterError as e:
            dict_tmp['error']="1"                                              #失败{ "error":0, "message": "初始化错误信息"}
            dict_tmp['message']="初始化错误信息"                                              
            return HttpResponse(json.dumps(dict_tmp))