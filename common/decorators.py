import traceback

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from common.interface_helper import *
import json
from common.models import DException
from mongoengine.errors import ValidationError
from common.tools import RequestTools


#管理员装饰类，用于判定是否是管理员用户
class AdminRequired:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        # print("'{0}' is called @AdminRequired".format(self.func.__name__))
        request = args[0]
        user = request.user
        if user.is_staff:
            return self.func(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('authentic:login'))


#超级管理员装饰类，用于判定是否是超级管理员用户
class SuperAdminRequired:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        # print("'{0}' is called @SuperAdminRequired".format(self.func.__name__))
        request = args[0]
        if request.user.is_staff:
            if request.user.is_superuser:
                return self.func(*args, **kwargs)
        request.session['message'] = '您没有超级管理员权限，请重新登录'
        return HttpResponseRedirect(reverse('authentic:login'))


# 异常捕捉装饰类
class ExceptionRequired:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        request = args[0]
        path = request.META.get('PATH_INFO', '')
        try:
            return self.func(*args, **kwargs)
        except ParameterError as e:
            exception = DException(exception=e.message, traceback=traceback.format_exc(), post=json.dumps(request.POST),
                                   get=json.dumps(request.GET), type='ParameterError', path=path).save()
            data = {'exception': exception.data()}
            return JsonResult(code=e.code, message=e.message, data=data, request=request).response()
        except CustomError as e:
            exception = DException(exception=e.message, traceback=traceback.format_exc(), post=json.dumps(request.POST),
                                   get=json.dumps(request.GET), type='CustomError', path=path).save()
            data = {'exception': exception.data()}
            return JsonResult(code=e.code, message=e.message, data=data, request=request).response()
        except KeyError as e:
            exception = DException(exception=str(e), traceback=traceback.format_exc(), post=json.dumps(request.POST),
                                   get=json.dumps(request.GET), type='KeyError', path=path).save()
            data = {'exception': exception.data()}
            return JsonResult(code=CODE_KEY_ERROR, message=str(e), data=data, request=request).response()
        except ValueError as e:
            exception = DException(exception=str(e), traceback=traceback.format_exc(), post=json.dumps(request.POST),
                                   get=json.dumps(request.GET), type='ValueError', path=path).save()
            data = {'exception': exception.data()}
            return JsonResult(code=CODE_VALUE_ERROR, message=str(e), data=data, request=request).response()
        except TypeError as e:
            exception = DException(exception=str(e), traceback=traceback.format_exc(), post=json.dumps(request.POST),
                                   get=json.dumps(request.GET), type='TypeError', path=path).save()
            data = {'exception': exception.data()}
            return JsonResult(code=CODE_TYPE_ERROR, message=str(e), data=data, request=request).response()
        except ValidationError as e:
            exception = DException(exception=str(e), traceback=traceback.format_exc(), post=json.dumps(request.POST),
                                   get=json.dumps(request.GET), type='ValidationError', path=path).save()
            data = {'exception': exception.data()}
            return JsonResult(code=CODE_PARAMETER_ERROR, message=str(e), data=data, request=request).response()
        except Exception as e:
            exception = DException(exception=str(e), traceback=traceback.format_exc(), post=json.dumps(request.POST),
                                   get=json.dumps(request.GET), type='Exception', path=path).save()
            data = {'exception': exception.data()}
            return JsonResult(code=CODE_INTERNAL_SERVER_ERROR, message=str(e), data=data, request=request).response()


# 检测访问令牌
class CheckTokenRequired:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        request = args[0]
        path = request.META.get('PATH_INFO', '')
        try:
            if RequestTools(request).check_token():
                return self.func(*args, **kwargs)
            else:
                raise TokenError()
        except TokenError as e:
            exception = DException(exception=e.message, traceback=traceback.format_exc(), post=json.dumps(request.POST),
                                   get=json.dumps(request.GET), type='TokenError', path=path).save()
            data = {'exception': exception.data()}
            return JsonResult(code=CODE_TOKEN_ERROR, message=e.message, data=data, request=request).response()