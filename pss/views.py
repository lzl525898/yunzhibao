__author__ = 'mlzx'
from django.views.decorators.csrf import csrf_exempt
from common.models import *
from common.decorators import *
from common.tools import RequestTools
from pss.tools import DocumentPssTools
from common.tools_taikang import TkHelper
import hashlib
import math

@csrf_exempt
@ExceptionRequired
def logistics_get_key(request):
    result = dict()
    if request.method == "POST":
        pss_tools = DocumentPssTools(request)
    else:
        raise InvalidAccessError()


@csrf_exempt
@ExceptionRequired
def logistics_company_order(request):
    result = dict()
    if request.method == "POST":
        pss_tools = DocumentPssTools(request)
        order = Ordering()
        order = pss_tools.validation_logistics_order(order)

        order.submit_style = 'platform'
        order.save()
        if order.product_type =='car':
            order.pay_money()
        order.save()
#下面三行是源代码
#         if order.client.balance < order.price:
#             raise UserBalanceError()
#         order.save()
        # insurance_product = order.insurance_product
        # company = order.company
        # if company == '':
        #     tai_kang_Helper=TkHelper(order)
        # # # elif chanpin == chanpin2:
        # # #     baoxianHelper=C2Helper()
        # else:
        #     raise ValidationError()
        # result = baoxianHelper.sendToCompany()
        # if result.is_success:
        #     return JsonResult(code=CODE_SUCCESS, message='成功').response()
        # else:
        #     raise ValidationError('提交到保险公司失败。错误码：{}'.format(result.code))
        result['order_id'] = str(order.id)
        return JsonResult(data=result, code=CODE_SUCCESS, message='成功').response()
    else:
        raise InvalidAccessError()
