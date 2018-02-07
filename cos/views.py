from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.decorators import AdminRequired
from django.template import RequestContext
from django.shortcuts import render_to_response
from common.models import *


# Create your views here.
@login_required
@AdminRequired
def index(request):
    data = {}
    context = RequestContext(request)
    data['admin_count'] = User.objects(is_staff=True).count()

    return render_to_response('bms/index.html',data, context)