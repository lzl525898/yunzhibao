__author__ = 'mlzx'
from common.decorators import ExceptionRequired, CheckTokenRequired
from common.interface_helper import *
from django.views.decorators.csrf import csrf_exempt
from common.models import *
from mongoengine.django.auth import User, make_password
from common.tools import DocumentTools, PageTools
from authentic.tools import AuthRequestTools


# Create your views here.
@csrf_exempt
@ExceptionRequired
def register(request):
    if request.method == 'POST':
        result = dict()
        # 获取参数
        nickname = request.POST.get('nickname', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone', '').strip()
        verification_code = request.POST.get('verification_code', '').strip()
        sex = request.POST.get('sex', 'secret')
        address = request.POST.get('address', '')
        user_type = 'client'            # 仅提供客户的注册
        # 校验手机验证码
        DocumentTools.check_code(code=verification_code, phone=phone, code_type='register')
        # 校验参数正确性
        if not password:
            raise ParameterError('密码不能为空')
        if not FormatTools.validate_choices(sex, UserProfile.SEX_TYPE):
            raise ParameterError('非法的性别')
        # 验证用户是否已存在
        user = get_user(nickname)
        if user is not None:
            raise UserExistsError('昵称已存在')
        user = get_user(phone)
        if user is not None:
            raise PhoneExistsError('手机号已存在')
        username = DocumentTools.get_username()
        # 创建User
        user = User(username=username, password=make_password(password), first_name=user_type, last_name=nickname)
        user.save()
        profile = UserProfile(nickname=nickname, phone=phone, user_type=user_type, user_id=user.id)
        profile.address = address
        profile.sex = sex
        if user_type == 'client':
            entity = Client(user=user, profile=profile).save()
            # TODO:为新用户赋予默认积分
            # config = get_config()
            # entity.cumulative_score = config.cumulative_score_config.base_score
            entity.save()
            result['entity'] = entity.detail_data()
        else:
            raise ParameterError('用户类型错误')
        return JsonResult(data=result, request=request).response()
    else:
        return JsonResult(code=CODE_INVALID_ACCESS, message='非法访问', request=request).response()


##
# 无效：此项目不支持第三方登录
# ##
@csrf_exempt
@ExceptionRequired
def third_login(request):
    result = dict()
    if request.method == 'POST':
        # 获取参数
        third_part_id = request.POST.get('third_part_id', '')
        third_part_type = request.POST.get('third_part_type', '')
        # 校验参数正确性
        if not third_part_type in ['wx', 'qq', 'weibo', 'twitter', 'facebook']:
            raise ParameterError('非法的第三方类型')

        client = Client.objects(__raw__={third_part_type + '_id': third_part_id}).first()
        if client:
            # 用户存在，进入登录流程
            # TODO:检查用户头像变化
            # 生成token
            _token = DocumentTools.make_third_part_token(client)
            result['token'] = _token.data()
            result['client'] = client.data()
            return JsonResult(message='登录成功', data=result, request=request).response()
        else:
            return JsonResult(code=CODE_AUTHENTICATE_ERROR, message='用户不存在', data=result, request=request).response()
    else:
        return JsonResult(code=CODE_INVALID_ACCESS, message='非法访问', request=request).response()


##
# 无效：此项目不支持第三方登录
# ##
@csrf_exempt
@ExceptionRequired
def third_register(request):
    result = dict()
    if request.method == 'POST':
        # 获取参数
        third_part_id = request.POST.get('third_part_id', '')
        third_part_type = request.POST.get('third_part_type', '')
        # 校验参数正确性
        if not third_part_type in ['wx', 'qq', 'weibo', 'twitter', 'facebook']:
            raise ParameterError('非法的第三方类型')
        client = Client.objects(__raw__={third_part_type + '_id': third_part_id}).first()
        if client:
            # 用户存在，请直接登录
            raise UserExistsError('用户已存在，请直接登录')
        else:
            # 用户不存在，进入注册流程
            nickname = request.POST.get('nickname', '').strip()
            headimgurl = request.POST.get('headimgurl', '').strip()
            sex = request.POST.get('sex', 'secret')
            # 校验参数正确性
            if nickname == '':
                raise ParameterError('用户名不能为空')
            if not FormatTools.validate_choices(sex, UserProfile.SEX_TYPE):
                raise ParameterError('非法的性别')
            # 验证昵称是否已存在
            count = 0
            old_nickname = nickname
            while count < 100 and get_user(nickname):
                nickname = old_nickname + str(random.randint(100000, 999999))
            username = DocumentTools.get_username()
            # 创建User
            user_type = 'client'
            user = User(username=username, password=make_password(third_part_id), first_name=user_type, last_name=nickname)
            user.save()
            profile = UserProfile(nickname=nickname, user_type=user_type, user_id=user.id)
            profile.sex = sex
            entity = Client(user=user, profile=profile).save()   # 只可以注册普通用户
            setattr(entity, third_part_type + '_id', third_part_id)
            # TODO:初始化用户积分
            # config = DocumentTools.get_config()
            # entity.cumulative_score = config.cumulative_score_config.base_score
            entity.has_password = False
            entity.save()
            _token = DocumentTools.make_third_part_token(entity)
            result['token'] = _token.data()
            result['client'] = entity.data()
            return JsonResult(data=result, request=request).response()
    else:
        return JsonResult(code=CODE_INVALID_ACCESS, message='非法访问', request=request).response()


##
# 无效：此项目不支持第三方登录
# ##
@csrf_exempt
@ExceptionRequired
def third_bind(request):
    result = dict()
    if request.method == 'POST':
        # 获取参数
        third_part_id = request.POST.get('third_part_id', '')
        third_part_type = request.POST.get('third_part_type', '')
        # 校验参数正确性
        if not third_part_type in ['wx', 'qq', 'weibo', 'twitter', 'facebook']:
            raise ParameterError('非法的第三方类型')
        client = Client.objects(__raw__={third_part_type + '_id': third_part_id}).first()
        if client:
            raise UserExistsError('绑定失败：第三方平台已绑定了帐号，请先进行解绑。')
        user = AuthRequestTools.get_user_with_token(request)
        if user is None:
            nickname = request.POST.get('nickname', '')
            password = request.POST.get('password', '')
            user, client = DocumentTools.multi_authenticate(nickname=nickname, password=password)
        else:
            client = Client.objects(user=user).first()
        if user is None or not user.is_active:
            raise NewError(CODE_USER_ACTIVE_ERROR, '用户认证失败：用户状态异常')
        if client is None:
            raise AuthenticateError('用户认证失败，请重新登录')
        if getattr(client, third_part_type + '_id', '') != '':
            raise UserExistsError('绑定失败：用户已绑定第三方平台，请先进行解绑。')
        setattr(client, third_part_type + '_id', third_part_id)
        client.save()
        _token = DocumentTools.make_third_part_token(client)
        result['token'] = _token.data()
        result['client'] = client.data()
        return JsonResult(data=result, request=request).response()
    else:
        return JsonResult(code=CODE_INVALID_ACCESS, message='非法访问', request=request).response()


##
# 无效：此项目不支持第三方登录
# ##
@csrf_exempt
@ExceptionRequired
def third_unbind(request):
    result = dict()
    if request.method == 'POST':
        # 获取参数
        third_part_id = request.POST.get('third_part_id', '')
        third_part_type = request.POST.get('third_part_type', '')
        # 校验参数正确性
        if not third_part_type in ['wx', 'qq', 'weibo', 'twitter', 'facebook']:
            raise ParameterError('非法的第三方类型')
        if third_part_id == '':
            raise ParameterError('第三方平台帐号id不能为空')
        nickname = request.POST.get('nickname', '')
        password = request.POST.get('password', '')
        user, client = DocumentTools.multi_authenticate(nickname, password)
        if client is None:
            raise AuthenticateError('用户认证失败：没有找到对应用户')
        if user is None or not user.is_active:
            raise NewError(CODE_USER_ACTIVE_ERROR, '用户认证失败：用户状态异常')
        if not client.has_password:
            raise NewError(CODE_PASSWORD_NOT_FOUND_ERROR, '解绑失败：请先设置密码')
        if getattr(client, third_part_type + '_id', '') == '':
            raise NewError(code=CODE_USER_ACTIVE_ERROR, message='解绑失败：用户未绑定该平台帐号')
        elif getattr(client, third_part_type + '_id', '') != third_part_id:
            raise NewError(CODE_PERMISSION_DENIED_ERROR, '解绑失败：第三方平台帐号错误')
        setattr(client, third_part_type + '_id', '')
        client.save()
        result['client'] = client.data()
        return JsonResult(data=result, request=request).response()

    else:
        return JsonResult(code=CODE_INVALID_ACCESS, message='非法访问', request=request).response()


##
# nickname
# password
# #
@csrf_exempt
@ExceptionRequired
def login(request):
    result = {}
    if request.method == 'POST':
        request_tools = AuthRequestTools(request)
        token, user = request_tools.make_token()
        result['user_type'] = user.first_name
        result['token'] = token.detail_data()
        if user.first_name == 'client':
            entity = Client.objects(user=user).first()
        else:
            raise ParameterError('用户类型错误')
        result['entity'] = entity.detail_data()
        return JsonResult(message='登录成功', data=result, request=request).response()
    else:
        return JsonResult(code=CODE_INVALID_ACCESS, message='非法访问', request=request).response()


##
# phone
# verification_type('register','reset_password')
#   #
@csrf_exempt
@ExceptionRequired
def send_code(request):
    # result = {}
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        user=""
        if phone :
            user = DocumentTools.get_user(phone)
#             if user:
#                 return JsonResult(code=CODE_PHONE_EXISTS, message='手机号已注册，请更换', request=request).response()
        else:
             return JsonResult(code=CODE_ERROR, message='手机号码不能为空', request=request).response()
        verification_type = request.POST.get('verification_type', '').strip()
        if verification_type == "register":
             if user:
                 return JsonResult(code=CODE_PHONE_EXISTS, message='手机号已注册，请更换', request=request).response()
        verification_code = DocumentTools.make_code(phone=phone, verification_type=verification_type)
        print("接口"+verification_type)
        print("接口"+str(verification_code.type))
        if DocumentTools.send_phone_message(phone=phone, verification_type=verification_type, verification_code=verification_code.code):
            return JsonResult(data={'test': verification_code.detail_data(),'verification_code':verification_code.code}, request=request).response()
        else:
            return JsonResult(code=CODE_ERROR, message='发送验证码失败', request=request).response()
    else:
        return JsonResult(code=CODE_INVALID_ACCESS, message='非法访问', request=request).response()


###
# nickname
# new_password
# phone
# verification_code
# 暂无效：用户认证方式变更
# ###
@csrf_exempt
@ExceptionRequired
def reset_password(request):
    # result = {}
    if request.method == 'POST':
        password = request.POST.get('new_password', '')
        phone = request.POST.get('phone', '')
        verification_code = request.POST.get('verification_code').strip()
        DocumentTools.check_code(code=verification_code, phone=phone, code_type='reset_password')
        user, entity = DocumentTools.multi_get_user(phone)
        if entity.profile.phone != phone:
            raise ParameterError('手机号错误')
        if user is None:
            raise ParameterError('无效的用户名')
        if user.is_active:
            user.password = make_password(password)
            user.save()
            return JsonResult(request=request).response()
        else:
            return JsonResult(code=CODE_AUTHENTICATE_ERROR, message='用户状态异常', request=request).response()
    else:
        return JsonResult(code=CODE_INVALID_ACCESS, message='非法访问', request=request).response()


###
# nickname
# password
# new_password
# ###
@csrf_exempt
@ExceptionRequired
@CheckTokenRequired
def change_password(request):
    # result = {}
    if request.method == 'POST':
        request_tools = AuthRequestTools(request)
        nickname = request.POST.get('nickname', '').strip()
        password = request.POST.get('password', '')
        new_password = request.POST.get('new_password', '')
        user, entity = DocumentTools.multi_authenticate(account=nickname, password=password)
        token_user = request_tools.get_user_with_token()
        if user:
            if user != token_user:
                raise ParameterError("只能修改自己的密码")
            if user.is_active:
                user.password = make_password(new_password)
                user.save()
                return JsonResult(request=request).response()
            else:
                raise NewError(message='用户状态异常', code=CODE_USER_ACTIVE_ERROR)
        else:
            raise AuthenticateError('用户名或密码错误')
    else:
        raise InvalidAccessError()


@csrf_exempt
@ExceptionRequired
@CheckTokenRequired
def change_profile(request):
    result = {}
    if request.method == 'POST':
        request_tools = AuthRequestTools(request)
        token = request_tools.check_token()
        user = token.user
        entity = None
        user_type = request.POST.get('user_type', '')
        if user_type == 'client':
            entity = Client.objects(user=user).first()
        else:
            raise ParameterError('unknown user type')
        profile = entity.profile
        profile = request_tools.validation_profile(profile, user)
        entity.profile = profile
        entity.user.last_name = profile.nickname
        entity.save()
        result['profile'] = profile.data()
        return JsonResult(data=result, request=request).response()
    else:
        raise InvalidAccessError()


@csrf_exempt
@ExceptionRequired
@CheckTokenRequired
def change_client(request):
    result = {}
    if request.method == 'POST':
        request_tools = AuthRequestTools(request)
        token = request_tools.check_token()
        user = token.user
        entity = None
        user_type = request.POST.get('user_type', '')
        if user_type == 'client':
            entity = Client.objects(user=user).first()
            entity = request_tools.validation_client(entity)
        else:
            raise ParameterError('unknown user type')
        entity.save()
        return JsonResult(request=request).response()
    else:
        raise InvalidAccessError()


###
# nickname
# password
# ###
@csrf_exempt
@ExceptionRequired
def get_access_token(request):
    # result = {}
    if request.method == 'POST':
        try:
            request_tools = AuthRequestTools(request)
            token, user = request_tools.make_token()
            return JsonResult(code=CODE_SUCCESS, message='令牌已生成', data={'token': token.detail_data()}, request=request).response()
        except ParameterError as e:
            return JsonResult(code=CODE_ERROR, message=e.message, request=request).response()
    else:
        raise InvalidAccessError()


@csrf_exempt
@ExceptionRequired
@CheckTokenRequired
def refresh_access_token(request):
    # result = {}
    if request.method == 'POST':
        try:
            request_tools = AuthRequestTools(request)
            token = request_tools.refresh_token()
            return JsonResult(code=CODE_SUCCESS, message='令牌已生成', data={'token': token.detail_data()}, request=request).response()
        except ParameterError as e:
            return JsonResult(code=CODE_ERROR, message=e.message, request=request).response()
    else:
        return JsonResult(code=CODE_INVALID_ACCESS, message='非法访问', request=request).response()


