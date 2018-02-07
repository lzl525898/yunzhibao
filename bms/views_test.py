__author__ = 'mlzx'
import hashlib
from django.contrib.auth.decorators import login_required
from common.decorators import AdminRequired
from common.decorators import SuperAdminRequired
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from mongoengine.django.auth import User, make_password
# from common.tools_legoo import *
from common.tools import *



def test(request):
    context = RequestContext(request)
    data = {}
    # Certificate.objects(state='init').delete()
#     certificate.client = Client.objects(profile__phone='18646457878').first()
#     # 物流公司
#     certificate.user_type = 'transport'
#     # certificate.user_classify = 'singleLine'
#     certificate.user_classify = 'multiLine'
#     certificate.national_id = '230882199007292310'
#     certificate.national_image = 'static/pic/certificate/4.jpg'
#     certificate.operating_permit_image = '/static/pic/certificate/1.jpg'
#     certificate.business_license_image = '/static/pic/certificate/6.jpg'
#     certificate.operating_permit_id = '230103100995334'
#     certificate.business_license_id = '150021011013'
#     certificate.name = '王老五'

    # # # 司机
    # certificate.user_type = 'driver'
    # certificate.national_id = '230882199007292323'
    # certificate.national_image = '/static/pic/certificate/4.jpg'
    # certificate.driver_id = '23156464646146'
    # certificate.driver_image = '/static/pic/certificate/7.jpg'
    # certificate.plate_number = '黑A13464'
    # certificate.plate_image = '/static/pic/certificate/7.jpg'
    # certificate.transportation_license_id = '15646413131'
    # certificate.transportation_image = '/static/pic/certificate/1.jpg'
    # certificate.name = '张三'

    # 货主
    # certificate.user_type = 'boss'
    # certificate.national_id = '230882192290072923'
    # certificate.national_image = '/static/pic/certificate/4.jpg'
    # certificate.user_classify = 'individuals'
    # # certificate.user_classify = 'units'
    # certificate.business_license_id = '110115000000'
    # certificate.business_license_image = '/static/pic/certificate/6.jpg'
    # certificate.name = '小淘气'
    # certificate.save()
    # return HttpResponse('success')
    return render_to_response('bms/test.html', data, context)