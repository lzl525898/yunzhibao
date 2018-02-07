from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from common.tools import RequestTools, DocumentTools, ConvertTools


def user_login(request):
    result = dict()
    context = RequestContext(request)
    if request.user.is_authenticated():
        print('已登陆用户被注销：{0}'.format(request.user.username))
        logout(request)
    tools_request = RequestTools(request)
    tools_request.check_message(result)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                #return HttpResponseRedirect(request.session['login_from'])
                #认证过程：（1）检查user的first_name字段的类型是否正确；（2）检查是否有对应类型的文档再数据库中存在。
                #这样可以保证，经过认证的用户，user中的first_name字段正确，也就是说，根据这个字段，一定可以取出对应类型的文档；
                #其次，数据库一定存在这个类型的文档实例。
                if user.is_superuser:
                    return HttpResponseRedirect(reverse('bms:index'))
                elif user.is_staff:
                    return HttpResponseRedirect(reverse('bms:index'))
                # 此处处理非管理员用户登录
                else:
                    # 非法的用户类型，取消登录并提示失败
                    logout(request)
                    result['message'] = '登录失败，用户类型错误'
            else:
                result['message'] = '登录失败，用户未激活或被冻结'
                # return render_to_response('authentic/login.html', {'alert': '登录失败，用户未激活或被冻结'}, context)
        else:
            # Django登录失败，尝试使用客户登陆流程
            user, entity = DocumentTools.multi_authenticate(username, ConvertTools.get_sha1_string(password))
            if user and entity:
                login(request, user)
                print(user)
                print(user.username)
                if user.first_name == 'claim':
                    get_parameter = "?phone={0}".format(username)
                    return HttpResponseRedirect(reverse('cos:order_list', args=[1,])+get_parameter)
                elif user.first_name == 'intermediary':
                    get_parameter = "?phone={0}".format(username)
                    return HttpResponseRedirect(reverse('cos:cos_jdclbx_list', args=[1,])+get_parameter)
                else:
                    logout(request)
                    result['message'] = '登录失败，用户类型错误'
            else:
                result['message'] = '登录失败，用户名、密码错误'
    elif request.method == 'GET':
        pass
    return render_to_response('authentic/login.html', result, context)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('authentic:login'))