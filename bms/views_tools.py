__author__ = 'mlzx'
from common.models import *
from bms.tools import RequestTools
from django.contrib.auth.decorators import login_required
from common.decorators import SuperAdminRequired, ExceptionRequired
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse


# Create your views here.
@login_required
def item_detail(request, item_id):
    if User.objects(id=item_id).first():
        user = User.objects(id=item_id).first()
        if user.is_staff:
            return HttpResponseRedirect(reverse('bms:admin_edit', args=[item_id, ]))
        else:
            return HttpResponseRedirect(reverse('bms:{0}_edit'.format(user.first_name), args=[item_id, ]))
    elif InsuranceCompanyParent.objects(id=item_id).first():
        return HttpResponseRedirect(reverse('bms:head_company_detail', args=[item_id, ]))
    elif InsuranceCompany.objects(id=item_id).first():
        return HttpResponseRedirect(reverse('bms:tail_company_detail', args=[item_id, ]))
    elif InsuranceDocument.objects(id=item_id).first():
        return HttpResponseRedirect(reverse('bms:insurance_document_detail', args=[item_id, ]))
    elif InsuranceProducts.objects(id=item_id).first():
        return HttpResponseRedirect(reverse('bms:insurance_product_detail', args=[item_id, ]))
    elif Client.objects(id=item_id).first():
        if Client.objects(id=item_id).first().user_type == 'registered':
            return HttpResponseRedirect(reverse('bms:registered_edit', args=[item_id, ]))
        if Client.objects(id=item_id).first().user_type == 'transport':
            return HttpResponseRedirect(reverse('bms:transport_detail', args=[item_id, ]))
        if Client.objects(id=item_id).first().user_type == 'driver':
            return HttpResponseRedirect(reverse('bms:driver_detail', args=[item_id, ]))
        if Client.objects(id=item_id).first().user_type == 'boss':
            return HttpResponseRedirect(reverse('bms:boss_detail', args=[item_id, ]))
    elif Certificate.objects(id=item_id).first():
        return HttpResponseRedirect(reverse('bms:certificate_detail', args=[item_id, ]))
    elif Claim.objects(id=item_id).first():
        return HttpResponseRedirect(reverse('bms:claim_detail', args=[item_id, ]))
    elif Lawyer.objects(id=item_id).first():
        return HttpResponseRedirect(reverse('bms:lawyer_detail', args=[item_id, ]))
    elif Coupon.objects(id=item_id).first():
        return HttpResponseRedirect(reverse('bms:coupon_detail', args=[item_id, ]))
    elif Ordering.objects(id=item_id).first():
        return HttpResponseRedirect(reverse('bms:order_detail', args=[item_id, ]))
    elif Compensate.objects(id=item_id).first():
        return HttpResponseRedirect(reverse('bms:compensate_detail', args=[item_id, ]))
    else:
        return HttpResponse("unknown id")