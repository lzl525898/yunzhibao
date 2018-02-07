__author__ = 'mlzx'
from mongoengine.django.auth import User
from mongoengine import *
import random
from datetime import datetime

# User隐型使用说明：
#   (1)first_name ，用于保存用户类型，支持instructor和audience
#   (2)last_name，保存了profile.nickname
#
###################    通用工具    ####################
DATE_STRING = '%Y-%m-%d'
TIME_STRING = '%H:%M'
DATETIME_STRING = '%Y-%m-%d %H:%M:%S'
SMALL_DATETIME_STRING = '%Y-%m-%d %H:%M'

PROVINCE_ENUM = (
    ('', '无'),
    ('beijing', '北京'),
    ('tianjin', '天津'),
    ('hebei', '河北'),
    ('neimenggu', '内蒙古'),
    ('shanxijin', '山西晋'),
    ('shanghai', '上海'),
    ('anhui', '安徽'),
    ('jiangsu', '江苏'),
    ('zhejiang', '浙江'),
    ('shandong', '山东'),
    ('fujian', '福建'),
    ('jiangxi', '江西'),
    ('guangdong', '广东'),
    ('guangxi', '广西'),
    ('hainan', '海南'),
    ('henan', '河南'),
    ('hubei', '湖北'),
    ('hunan', '湖南'),
    ('heikongjiang', '黑龙江'),
    ('jilin', '吉林'),
    ('liaoning', '辽宁'),
    ('shanxishan', '陕西'),
    ('gansu', '甘肃'),
    ('ningxia', '宁夏'),
    ('qinghai', '青海'),
    ('xinjiang', '新疆'),
    ('chongqing', '重庆'),
    ('sichuan', '四川'),
    ('yunnan', '云南'),
    ('guizhou', '贵州'),
    ('xizang', '西藏'),
    ('xianggang', '香港'),
    ('aomen', '澳门'),
    ('taiwan', '台湾'),
)


class FormatTools(object):

    @staticmethod
    def get_random_paper_id():
        code = "{0}{1}".format(datetime.now().strftime("%Y%m%d%H%M%S%f"), str(random.randint(100000, 999999)))
        return code[2:22]

    @staticmethod
    def get_random_referee_code():
        code = str(random.randint(100000, 999999))
        return code

    @staticmethod
    def get_random_product_paper_id():
        code = str(random.randint(1, 999999))
        return code

    # #总公司的paper_id
    # @staticmethod
    # def get_random_head_company_paper_id():
    #     code = str(random.randint(1, 99))
    #     if len(code) == 1:
    #         code = '0' + code
    #     return code

    @staticmethod
    def get_value(language_code, values, spare_code='en'):
        if isinstance(values, dict):
            if language_code in values:
                return values[language_code]
            if spare_code and spare_code in values:
                return values[spare_code]
            else:
                for key in values:
                    return values[key]
        return ''

    @staticmethod
    def validate_choices(value, choices):
        if choices:
            if isinstance(choices[0], (list, tuple)):
                option_keys = [k for k, v in choices]
                option_values = [v for k, v in choices]
                return value in option_keys or value in option_values
            else:
                return value in choices
        else:
            return False


class DataTools(object):

    def detail_data(self):
        return DataTools.auto_data(self, self._fields.items())

    @staticmethod
    def auto_data(obj, items):
        data = dict()
        for name, cls in list(items):
            if not name.startswith("_"):
                value = getattr(obj, name, None)
                key, value = DataTools.get_data(name, cls, value)
                data[key] = value
        return data

    @staticmethod
    def get_value(cls, value):
        if isinstance(cls, (ReferenceField, GenericReferenceField)):
            return value.list_data() if hasattr(value, 'list_data') else value.detail_data() if hasattr(value, 'detail_data') else str(value.id) if value else dict()
            # return str(value.id) if value else ""
        elif isinstance(cls, StringField):
            return value if value else ""
        elif isinstance(cls, BooleanField):
            return bool(value) if value else False
        elif isinstance(cls, FloatField):
            return float(value) if value else 0.0
        elif isinstance(cls, IntField):
            return int(value) if value else 0
        elif isinstance(cls, DateTimeField):
            return value.strftime(DATETIME_STRING) if value else ""
        elif isinstance(cls, (EmbeddedDocumentField, GenericEmbeddedDocumentField, DynamicEmbeddedDocument)):
            if value is None:
                return dict()
            elif hasattr(value, 'data'):
                return value.data()
            elif hasattr(value, 'list_data'):
                return value.list_data()
            elif hasattr(value, 'detail_data'):
                return value.detail_data() if value else dict()
            else:
                return dict()
        elif isinstance(cls, ObjectIdField):
            return str(value) if value else ""
        elif isinstance(cls, UUIDField):
            return str(value) if value else ""
        elif isinstance(cls, ListField):
            return [item.list_data() if hasattr(item, 'list_data') else
                    item.detail_data() if hasattr(item, 'detail_data') else DataTools.get_value(type(item), item)
                    for item in value] if value else []
        elif isinstance(cls, str.__class__):
            return value
        else:
            print(str(cls) + ":" + str(value))
            return str(value) if value else ""

    @staticmethod
    def get_data(name, cls, value):
        if isinstance(cls, (ReferenceField, GenericReferenceField)):
            return name, DataTools.get_value(cls, value)
        else:
            return name, DataTools.get_value(cls, value)


###################    设置    ####################
# 系统设置
class BaseSettings(Document):
    max_list_count = IntField(default=100)          # 最大列表长度
    default_list_count = IntField(default=10)       # 默认列表长度
    image_max_size = IntField(default=3600)         # 图片最大大小
    file_max_size = IntField(default=50000)         # 文件最大大小
    document_max_size = IntField(default=50000)     # 文档最大大小

    meta = {
        'allow_inheritance': True,
    }

    @ staticmethod
    def get_settings():
        setting, created = BaseSettings.objects.get_or_create()
        return setting

    @staticmethod
    def get_setting_name():
        result = dict()
        result['max_list_count'] = '最大列表长度'
        result['default_list_count'] = '默认列表长度'
        result['image_max_size'] = '最大图片大小'
        result['document_max_size'] = '最大图片大小'
        return result


###################    用户认证    ####################


# 验证码
class VerificationCode(Document, DataTools):
    TYPE = (
        ('register', '注册'),
        ('reset_password', '重置密码'),
        ('delete', '删除信息'),
        ('change', '修改信息'),
    )
    code = StringField(default='', max_length=6)    # 校验码
    telephone = StringField(default='', max_length=20)  # 手机号
    used = BooleanField(default=False)  # 校验码已经被使用
    type = StringField(default='', choices=TYPE)    # 校验码的用途
    create_time = DateTimeField(default=datetime.now)  # 仅用于排序
    meta = {
        'ordering': ['-create_time']
    }


# 访问控制码
class AccessToken(Document, DataTools):
    user = ReferenceField(User, reverse_delete_rule=CASCADE)  # 用户，其中User已经具有的属性包括：username, password, email, first_name
    create_time = DateTimeField(default=datetime.now)  # 仅用于排序
    overdue = BooleanField(default=False)  # 访问控制码已过期
    token = UUIDField()
    meta = {
        'ordering': ['-create_time']
    }


###################    调试工具    ####################
# 异常信息
class DException(Document):
    exception = StringField(default="")
    traceback = StringField(default="")
    type = StringField(default='Exception')
    post = StringField(default='')
    get = StringField(default='')
    cookie = StringField(default='')
    path = StringField(max_length=200, default='')
    create_time = DateTimeField(default=datetime.now)
    meta = {
        'ordering': ['-create_time']
    }

    def data(self):
        result = {}
        if self.id:
            result['id'] = str(self.id)
        result['exception'] = self.exception.replace('"', "'")
        result['type'] = self.type
        result['create_time'] = self.create_time.strftime(DATETIME_STRING)
        result['post'] = self.post.replace('"', "'")
        result['get'] = self.get.replace('"', "'")
        result['cookie'] = self.cookie.replace('"', "'")
        result['path'] = self.path.replace('"', "'")
        return result


# 日志信息
class Log(Document):
    LOG_TYPE = (
        ('login', '登录'),
        ('logout', '注销'),
        ('search', '搜索'),
        ('create', '新增'),
        ('delete', '删除'),
        ('edit', '编辑'),
        ('unknown', '不明'),
    )
    content = StringField(max_length=2000, default='')
    ip = StringField(max_length=15, default='')
    type = StringField(max_length=50, choices=LOG_TYPE, default='unknown')
    path = StringField(max_length=200, default='')
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    create_time = DateTimeField(default=datetime.now)
    meta = {
        'ordering': ['-create_time']
    }


# 用于极光推送的工具类
class Notification(Document, DataTools):
    alert = StringField(default="")
    title = StringField(default="")
    extras = StringField(default="")
    tag = StringField(default="")
    alias = StringField(default="")
    is_read = BooleanField(default=False)
    create_time = DateTimeField(default=datetime.now)
    meta = {
        'ordering': ['-create_time']
    }