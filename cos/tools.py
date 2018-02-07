__author__ = 'mlzx'

from common.tools_legoo import DocumentTools, DocumentFolderType, ImageTools, ImageFolderType
from common.tools import RequestTools
from common.tools import ConvertTools
from common.models import *
from django.contrib.auth import authenticate
from datetime import timedelta
from common.interface_helper import *
from uuid import uuid1
from mongoengine.django.auth import User


class DocumentBmsTools(RequestTools):

#   验证优惠券
    def validation_coupon(self, coupon):
        name = self.get_parameter("name").strip()
        if name:
            coupon.name = name
        else:
            raise ParameterError('姓名不能为空')

        describe = self.get_parameter("describe").strip()
        if describe:
            coupon.describe = describe

        # 产品
        product_id = self.get_parameter('product_id').strip()
        if product_id:
            insurance_product = InsuranceProducts.objects(id=product_id).first()
            if insurance_product:
                coupon.product = insurance_product
            else:
                raise ParameterError('产品不存在')
        else:
            raise ParameterError('产品不能为空')

        end_date = self.get_parameter("end_date").strip()
        if end_date:
            coupon.end_date = end_date
        else:
            raise ParameterError('截至日期不能为空')

        # max_count = self.get_parameter("max_count").strip()
        # try:
        #     if max_count:
        #         max_count = int(max_count)
        #         coupon.max_count = max_count
        # except Exception:
        #     raise ParameterError("数据类型错误，请填写整数")
        #
        # min_price = self.get_parameter("min_price").strip()
        # try:
        #     if min_price:
        #         min_price = int(min_price)
        #         coupon.min_price = min_price
        # except Exception:
        #     raise ParameterError("数据类型错误，请填写整数")
        #
        # max_price = self.get_parameter("max_price").strip()
        # try:
        #     if max_count:
        #         max_price = int(max_price)
        #         coupon.max_price = max_price
        # except Exception:
        #     raise ParameterError("数据类型错误，请填写整数")

        rate = self.get_parameter("rate").strip()
        try:
            if rate:
                rate = float(rate)
                coupon.rate = rate
        except Exception:
            raise ParameterError("数据类型错误，请填写整数")
        return coupon

