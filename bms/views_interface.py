__author__ = 'mlzx'

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from common.decorators import AdminRequired, ExceptionRequired
from bms.tools import *


# @login_required
# @ExceptionRequired
def get_insurance_company_list(request):
    data = {}
    company_id = request.GET.get('company_id', '')
    insurance_type_key = request.GET.get('insurance_type_key', '')
    if company_id:
        company = InsuranceCompany.objects(id=company_id).first()
        if company:
            insurance_product_company_set = InsuranceProducts.objects(company=company)
            if insurance_type_key:
                insurance_product_company_set = insurance_product_company_set.filter(product_type=insurance_type_key)
            for insurance_product_company in insurance_product_company_set:
                data[str(insurance_product_company.id)] = insurance_product_company.name
        else:
            JsonResult(data=data, code=CODE_ERROR, message='未找到对应的公司').response()
    else:
        JsonResult(data=data, code=CODE_ERROR, message='你选择的公司不存在').response()
    return JsonResult(data=data, code=CODE_SUCCESS).response()


# @login_required
# @ExceptionRequired
def get_insurance_type_list(request):
    data = {}
    insurance_type_key = request.GET.get('insurance_type_key', '')
    if insurance_type_key:
        #测试只显示有效产品
        insurance_product_set = InsuranceProducts.objects(product_type=insurance_type_key , is_hidden=False)
#         insurance_product_set = InsuranceProducts.objects(product_type=insurance_type_key)
        company_id = request.GET.get('company_id', '')
        if company_id:
            company = InsuranceCompany.objects(id=company_id).first()
            if company:
                insurance_product_set = insurance_product_set.filter(company=company)
            else:
                JsonResult(data=data, code=CODE_ERROR, message='未找到对应的公司').response()
        for insurance_product in insurance_product_set:
            data[str(insurance_product.id)] = insurance_product.name
    else:
        JsonResult(data=data, code=CODE_ERROR, message='你选择的产品类型不存在').response()
    return JsonResult(data=data, code=CODE_SUCCESS).response()



# @login_required
# @ExceptionRequired
def get_insurance_product_list(request):
    data = {}
    insurance_product_key = request.GET.get('insurance_product_key', '')
    if insurance_product_key:
        try:
            insurance_product_set =InsuranceProducts.objects(id=insurance_product_key).first()
            print(insurance_product_set)
            for product_rate in insurance_product_set.product_rate_list:
                data[str(product_rate.good_type)] = product_rate.products_rate
#                 print("99999")
#                 print(product_rate.good_type)
        except Exception as e:
            message=str(e)
            JsonResult(data=data, code=CODE_ERROR, message=message).response()
        print(data)  
        return JsonResult(data=data, code=CODE_SUCCESS).response()

    else:
        return  JsonResult(data=data, code=CODE_ERROR, message='你选择的产品不存在').response()

# @login_required
# @ExceptionRequired
def get_pack_detail_list(request):
    data = {}
    pack_type = request.GET.get('pack_type', '')
    if pack_type:
        try:
            order = Ordering()
            pack_method_list=order.PACK_METHOD
            for pack_method in pack_method_list:
                a=pack_method
                print(a)
                if pack_method[0][0]==pack_type:
                    pack_detail=pack_method[1]
                    break
                
            data["pack_detail"]=pack_detail
        except:
            return  JsonResult(data=data, code=CODE_ERROR, message='您选择的包装类型无对应的包装详情').response()
        try:
            return JsonResult(data=data, code=CODE_SUCCESS).response()
        except Exception as e:
             a=str(e)
             return  JsonResult(data=data, code=CODE_ERROR, message=a).response()
    else:
        return  JsonResult(data=data, code=CODE_ERROR, message='您选择的包装类型不存在').response()

# @login_required
# @ExceptionRequired
def get_product_cargo_list(request):
    print(1111)
    data = {}
    product_id = request.GET.get('product_id', '')
    cargo_state = request.GET.get('cargo_state', '')
    #data["cargo"]=cargo_state
    cargo_list=[]
    try:
        product_set =InsuranceProducts.objects(id=product_id).first()
    except Exception as e:
        return  JsonResult(data=data, code=CODE_ERROR, message=str(e)  ).response()
    if not cargo_state:
        return  JsonResult(data=data, code=CODE_ERROR, message='未找到货物类型').response()
    try:
        product_cargo_list =ProductCargo.objects(product=product_set,state=cargo_state)
        aa=product_cargo_list.count()
        if product_cargo_list.count()==0:
            return  JsonResult(data=data, code=CODE_ERROR, message='此产品未找到对应货物类型').response()
        else:
            for product_cargo in product_cargo_list:
#                 name=product_cargo.cargo.cargo_name
#                 number=product_cargo.cargo.cargo_number
#                 ccc=str(product_cargo.cargo.cargo_number)
                data[str(product_cargo.cargo.id)] = product_cargo.cargo.cargo_name
        return JsonResult(data=data, code=CODE_SUCCESS).response()
    except Exception as e:
        b=str(e)
        print(b)
        return  JsonResult(data=data, code=CODE_ERROR, message='此产品未找到货物类型').response()
#     return JsonResult(data=data, code=CODE_SUCCESS).response()



# @login_required
# @ExceptionRequired
def get_city_list(request):
    data = {}
    prov_code = request.GET.get('prov_code', '')
    import logging
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/test.log',
                filemode='w')
    
    logging.debug('This is debug message')
    print (prov_code)
    if prov_code:
        try:
            city_list=CargoArea.objects( parentcode = prov_code)
            for city_detail  in city_list:
                data[str(city_detail.code)] = city_detail.name
            return JsonResult(data=data, code=CODE_SUCCESS).response()
        except:
            return  JsonResult(data=data, code=CODE_ERROR, message='您选择的包装类型无对应的包装详情').response()
    else:
        return  JsonResult(data=data, code=CODE_ERROR, message='省份不存在，或网络不稳定').response()


# @login_required
# @ExceptionRequired
def get_dist_list(request):
    data = {}
    city_code = request.GET.get('city_code', '')
    print (city_code)
    if city_code:
        try:
            dist_list=CargoArea.objects( parentcode = city_code)
            for dist_detail  in dist_list:
                data[str(dist_detail.code)] = dist_detail.name
            return JsonResult(data=data, code=CODE_SUCCESS).response()
        except:
            return  JsonResult(data=data, code=CODE_ERROR, message='网络不稳定，或您选择的城市无县区地址').response()
    else:
        return  JsonResult(data=data, code=CODE_ERROR, message='省份不存在，或网络不稳定').response()



# @login_required
# @ExceptionRequired
def get_cargo_detail_list(request):
    data = {}
    cargo_type = request.GET.get('cargo_type', '')
    if cargo_type:
        try:
            cargotype=CargoType.objects(ct_name = cargo_type).first()
        except:
            return  JsonResult(data=data, code=CODE_ERROR, message='网络不稳定，您选择的货物大类未找到对应内容').response()
        try:
            cargo_set = Cargo.objects(cargo_type = cargotype,state = True)
            count = cargo_set.count()
            if count == 0:
                return  JsonResult(data=data, code=CODE_ERROR, message='对不起，您选择的货物大类，暂未承保货物小类').response()
            for cargo in cargo_set:
                data[str(cargo.cargo_number)] = cargo.cargo_name
            return JsonResult(data=data, code=CODE_SUCCESS).response()
        except Exception as e:
            a=str(e)
            print(a)
            return  JsonResult(data=data, code=CODE_ERROR, message='您选择的货物类别无对应货物详情').response()
    else:
        return  JsonResult(data=data, code=CODE_ERROR, message='您选择的货物大类不存在').response()
    
#自动获取关联产品内容
def get_cargo_type_list(request):
    data = {}
    product_id = request.GET.get('product_id', '')
    good_type = request.GET.get('good_type', '')
    try:
        product_set =InsuranceProducts.objects(id=product_id).first()
    except Exception as e:
        return  JsonResult(data=data, code=CODE_ERROR, message="网络不稳定请稍后再试"  ).response()
    cargo_list = Cargo.objects(state = True).order_by('cargo_type.ct_priority')
    if not cargo_list:
        return  JsonResult(data=data, code=CODE_ERROR, message="网络不稳定请您稍后再试"  ).response()
    product_cargo_list =""
    if product_set:
        try:
            product_cargo_list = ProductCargo.objects(product=product_set)
        except Exception as e:
            return  JsonResult(data=data, code=CODE_ERROR, message="网络不稳定请您稍后再试。"  ).response()  
    if product_cargo_list:
        for cargo in cargo_list:
            state="0"
            for product_cargo in product_cargo_list:
                if  product_cargo.cargo ==cargo:
                    if product_cargo.state == good_type:
                        state ="1"
                        break
                    else:
                        state ="2"
                        break
            data[str(cargo.cargo_number)] = [cargo.cargo_name , state]
        return JsonResult(data=data, code=CODE_SUCCESS).response()
    else:
        state=0
        for cargo in cargo_list:
                data[str(cargo.cargo_number)] = [cargo.cargo_name , state]
        return JsonResult(data=data, code=CODE_SUCCESS).response()


def get_user_detail(request):
    data = {}
    user_id = request.GET.get('user_id', '')
    if user_id:
        try:
            client_set=Client.objects( id = user_id).first()
            #动态用户名
            if client_set.company_name:
                data['user_name'] = client_set.company_name
            elif client_set.name:
                data['user_name'] = client_set.name
            else:
                data['user_name'] = ''
            #动态证件号
            if client_set.organ:
                data['user_number'] = client_set.organ
            elif client_set.business_license_id:
                data['user_number'] = client_set.business_license_id    
            elif client_set.national_id:
                data['user_number'] = client_set.national_id
            else:
                data['user_number'] = ''
            print(data)
            return JsonResult(data=data, code=CODE_SUCCESS).response()
        except:
            print(data)
            return  JsonResult(data=data, code=CODE_ERROR, message='网络不稳定，未获取到用户信息请手动输入').response()
    else:
        return  JsonResult(data=data, code=CODE_ERROR, message='用户不存在，或网络不稳定').response()