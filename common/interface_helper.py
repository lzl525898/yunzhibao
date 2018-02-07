__author__ = 'mlzx'
from django.http import JsonResponse
from django.conf import settings


#   错误代码
# Base Error Code
CODE_UNKNOWN_ERROR = -1     # 未知错误
CODE_SUCCESS = 0     # 访问成功
CODE_ERROR = 1     # 访问失败
CODE_PARAMETER_ERROR = 2      # 参数错误
# 50+ Parameter Error Code
CODE_KEY_ERROR = 50      # 沒找到對應參數
CODE_VALUE_ERROR = 51      # 转换值失败
CODE_IMAGE_TYPE_ERROR = 52     # 图片类型错误
CODE_IMAGE_SIZE_ERROR = 53     # 图片大小错误
CODE_IMAGE_NOT_EXISTS = 54     # 图片不存在
CODE_TYPE_ERROR = 55       # 类型错误
CODE_INVALID_DATE = 56     # 日期格式错误
# 100+ Authentic Error Code
CODE_TOKEN_ERROR = 101      # 访问令牌错误
CODE_TOKEN_TIMEOUT_ERROR = 102      # 访问令牌已过期
CODE_AUTHENTICATE_ERROR = 103       # 用户认证错误
CODE_USER_ACTIVE_ERROR = 104        # 用户状态错误
CODE_PERMISSION_DENIED_ERROR = 105      # 用户权限不足
CODE_USER_BALANCE_ERROR = 106      # 用户余额不足
# 120+ User Register and Edit Error Code
CODE_USER_EXISTS = 121      # 昵称已存在
CODE_PHONE_EXISTS = 122     # 手机号已存在
CODE_PASSWORD_NOT_FOUND_ERROR = 123        # 密码不能为空
CODE_VERIFICATION_CODE_TOO_FAST_ERROR = 124     # 发送验证码的频率过快
# Other Error Code
CODE_INVALID_ACCESS = 403       # 非法的访问：访问方法错误
CODE_NOT_IMPLEMENTED = 404      # 接口尚未实现
CODE_INTERNAL_SERVER_ERROR = 500        # 未知服务器错误


# 用于外部接口的服务器通讯
class JsonResult():
    def __init__(self, code=CODE_SUCCESS, message='success', data="", request=None):
        self.code = code               # 错误编码，非0时即代表有错误
        self.message = message          # 提示信息
        self.data = data               # 数据
        if request:
            tag = request.POST.get('tag', "")
            if tag == "":
                tag = request.GET.get('tag', "")
            self.tag = tag
        else:
            self.tag = ""

    def response(self):
        if settings.DEBUG:
            print(str(self.__dict__).replace("'", '"').replace("False", "false"))
        return JsonResponse(self.__dict__)


class CustomError(Exception):

    def __init__(self, code=CODE_ERROR, message='无效的参数'):
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)


class ParameterError(CustomError):
    def __init__(self, message='无效的参数'):
        self.message = message
        self.code = CODE_PARAMETER_ERROR


class UserBalanceError(CustomError):
    def __init__(self, message='用户余额不足'):
        self.message = message
        self.code = CODE_USER_BALANCE_ERROR


class NewError(CustomError):
    def __init__(self, code=CODE_UNKNOWN_ERROR, message='新异常'):
        self.message = message
        self.code = code


class InternalServerError(CustomError):
    def __init__(self, message='服务器内部错误'):
        self.message = message
        self.code = CODE_INTERNAL_SERVER_ERROR


class TokenError(CustomError):
    def __init__(self, message="非法的访问令牌"):
        self.message = message
        self.code = CODE_TOKEN_ERROR


class TokenTimeoutError(TokenError):
    def __init__(self, message="访问令牌已过期"):
        self.message = message
        self.code = CODE_TOKEN_TIMEOUT_ERROR


class AuthenticateError(CustomError):
    def __init__(self, message='用户认证失败'):
        self.message = message
        self.code = CODE_AUTHENTICATE_ERROR


class UserExistsError(AuthenticateError):
    def __init__(self, message="用户已存在"):
        self.message = message
        self.code = CODE_USER_EXISTS


class PermissionDeniedError(AuthenticateError):
    def __init__(self, message="用户权限不足"):
        self.message = message
        self.code = CODE_PERMISSION_DENIED_ERROR


class PhoneExistsError(AuthenticateError):
    def __init__(self, message="手机号已存在"):
        self.message = message
        self.code = CODE_PHONE_EXISTS


class InvalidAccessError(CustomError):
    def __init__(self, message="非法访问"):
        self.message = message
        self.code = CODE_INVALID_ACCESS


class FileTypeError(ParameterError):
    def __init__(self, message="文件类型错误"):
        self.message = message
        self.code = CODE_IMAGE_TYPE_ERROR


class FileSizeError(ParameterError):
    def __init__(self, message="文件大小错误"):
        self.message = message
        self.code = CODE_IMAGE_SIZE_ERROR


class ImageTypeError(FileTypeError):
    def __init__(self, message="图片类型错误"):
        self.message = message
        self.code = CODE_IMAGE_TYPE_ERROR


class ImageSizeError(FileSizeError):
    def __init__(self, message="图片大小错误"):
        self.message = message
        self.code = CODE_IMAGE_SIZE_ERROR