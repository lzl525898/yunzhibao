from common.models_legoo import *
import math
from django.conf import settings
#connect('InsuranceDB')

connect('InsuranceDB919')



###################    程序逻辑文档    ####################


###################    系统功能    ####################
class SiteSettings(BaseSettings):
    # 极光推送
    jpush_debug_app_key = StringField(default="")
    jpush_debug_master_secret = StringField(default="")
    jpush_app_key = StringField(default="")
    jpush_master_secret = StringField(default="")
    # 美联软通短信平台
    meilian_username = StringField(default="")
    meilian_password = StringField(default="")
    meilian_api_key = StringField(default="")
    # 电子邮件
    email_server = StringField(default="")
    email_from = StringField(default="")
    email_account = StringField(default="")
    email_password = StringField(default="")
    # ping++支付
    pingpp_api_key = StringField(default="")
    pingpp_app_id = StringField(default="")
    # 微信
    wechat_app_id = StringField(default="")
    wechat_app_secret = StringField(default="")
    we_chat_token = StringField(default='')
    #物流平台key
    logistics_key = StringField(default='')
    #用户协议
    user_protocol = StringField(default="", verbose_name='用户协议')
    #其他设置中默认产品设置
    product_code=StringField(default='')

    @ staticmethod
    def get_settings():
        setting, created = SiteSettings.objects.get_or_create()
        return setting

    @staticmethod
    def get_push_attrs(debug=False):
        result = []
        if debug:
            result.append("jpush_debug_app_key")
            result.append("jpush_debug_master_secret")
        else:
            result.append("jpush_app_key")
            result.append("jpush_master_secret")
        return result

    @staticmethod
    def get_sms_attrs(debug=False):
        result = []
        if debug:
            pass
        else:
            result.append("meilian_username")
            result.append("meilian_password")
            result.append("meilian_api_key")
        return result

    @staticmethod
    def get_email_attrs(debug=False):
        result = []
        if debug:
            pass
        else:
            result.append("email_server")
            result.append("email_from")
            result.append("email_account")
            result.append("email_password")
        return result

    @staticmethod
    def get_pay_attrs(debug=False):
        result = []
        if debug:
            pass
        else:
            result.append("pingpp_api_key")
            result.append("pingpp_app_id")
            result.append("wechat_app_id")
            result.append("wechat_app_secret")
        return result

    @staticmethod
    def get_other_attrs(debug=False):
        result = []
        if debug:
            pass
        else:
            result.append("max_list_count")
            result.append("default_list_count")
            result.append("image_max_size")
            result.append("we_chat_token")
            # result.append("logistics_key")
            #2017/10/23添加的默认产品编码
            result.append("product_code")
        return result

    @staticmethod
    def get_setting_name():
        result = dict()
        result['pingpp_api_key'] = 'Ping++密钥'
        result['pingpp_app_id'] = 'Ping++ID'
        result['meilian_username'] = '美联软通用户名'
        result['meilian_password'] = '美联软通密码'
        result['meilian_api_key'] = '美联软通密钥'
        result['wechat_app_id'] = '微信应用ID'
        result['wechat_app_secret'] = '微信应用密钥'
        result['we_chat_token'] = '微信交互密钥'
        result['jpush_app_key'] = '极光推送AppKey'
        result['jpush_master_secret'] = '极光推送MasterSecret'
        result['jpush_debug_app_key'] = '极光推送调试AppKey'
        result['jpush_debug_master_secret'] = '极光推送调试MasterSecret'
        result['email_server'] = '电子邮件服务器地址'
        result['email_from'] = '电子邮件发件人'
        result['email_account'] = '电子邮件帐号'
        result['email_password'] = '电子邮件密码'
        result['max_list_count'] = '最大列表长度'
        result['default_list_count'] = '默认列表长度'
        result['image_max_size'] = '图片最大大小'
        # result['logistics_key'] = '物流平台Key'
        #2017/10/23添加的默认产品编码
        result['product_code'] = '砖头投保默认产品编码'
        return result


#物流平台
class Logistics(Document, DataTools):
    name = StringField(max_length=16, default='')  # 物流平台名称
    platform_key = StringField(max_length=512, default='')  # 物流平台key值
    platform_secret= StringField(max_length=512, default='')  # 物流平台secret值


###################    用户功能    ####################
#用户信息
class UserProfile(EmbeddedDocument, DataTools):

    SEX_TYPE = (
        ('male', '男'),
        ('female', '女'),
        ('secret', '保密'),
    )



    #相关信息
    user_id = ObjectIdField()  # 用户ID

    icon = StringField(max_length=512, default='')  # 头像链接
    sex = StringField(max_length=30, default='secret', choices=SEX_TYPE)  # 性别
    phone = StringField(max_length=16, default='')  # 手机号码

    def data(self):
        return {
            'icon': self.icon, 'sex': self.sex, 'phone': self.phone
        }


# 保险公司 总公司
class InsuranceCompanyParent(Document, DataTools):
    # 基本信息
    name = StringField(max_length=20, default='')               # 总公司名称
    description = StringField(max_length=500, default='')       # 保险公司介绍
    paper_id = StringField(default='')                          # 编号（编码）
    phone = StringField(default='')                             # 全国统一报案电话

    # 平台控制项
    create_time = DateTimeField(default=datetime.now)           # 创建时间，主要用于排序
    is_hidden = BooleanField(default=False)             # 已隐藏，用于控制保险公司的有效性

    meta = {
        'ordering': ['-create_time']
    }

    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None,  cascade=None, cascade_kwargs=None,
             _refs=None, **kwargs):
        # 自动生成总公司编号
        if not self.paper_id:
            self.head_company_paper()
        return Document.save(self,  force_insert=force_insert, validate=validate, clean=clean,
                             write_concern=write_concern,  cascade=cascade, cascade_kwargs=cascade_kwargs,
                             _refs=_refs, **kwargs)

    def head_company_paper(self):
        self.paper_id = str(InsuranceCompanyParent.objects().count() + 1).zfill(2)
        # self.update(paper_id=str(InsuranceCompanyParent.objects().count() + 1).zfill(2))


# 保险公司 分公司
class InsuranceCompany(Document, DataTools):
    # 基本信息
    name = StringField(max_length=20, default='')               # 分公司名称
    simple_name = StringField(max_length=10, default='')        # 分公司简称
    parent = ReferenceField(InsuranceCompanyParent, reverse_delete_rule=CASCADE)        # 父类型
    paper_id = StringField(default='')                          # 编号

    # 统计信息：应在赔案中自动更新
    avg_project_time = FloatField(default=0)                    # 案均处理时效
    avg_project_pay = FloatField(default=0)                     # 案均赔款

    # 平台控制项
    create_time = DateTimeField(default=datetime.now)           # 创建时间，主要用于排序
    is_hidden = BooleanField(default=False)             # 已隐藏，用于控制保险公司的有效性

    meta = {
        'ordering': ['-create_time']
    }

    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None,  cascade=None, cascade_kwargs=None,
             _refs=None, **kwargs):
        # 自动生成分公司编号
        if not self.paper_id:
            self.tail_company_paper()
        return Document.save(self,  force_insert=force_insert, validate=validate, clean=clean,
                             write_concern=write_concern,  cascade=cascade, cascade_kwargs=cascade_kwargs,
                             _refs=_refs, **kwargs)

    def tail_company_paper(self):
        if self.parent.paper_id:
            self.paper_id = self.parent.paper_id + str(InsuranceCompany.objects(parent=self.parent).count() + 1).zfill(2)
        else:
            raise ValidationError("请先建立总公司")


# 保险文档
class InsuranceDocument(Document, DataTools):
    name = StringField(max_length=50, default='')               # 文档名称
    simple_name = StringField(max_length=10, default='')        # 文档名简称
    note = StringField(max_length=50, default='')               # 文档备注，用于区别文档
    content = StringField(max_length=15000, default='')           # 文档内容，HTML格式文档内容
    file_url = StringField(max_length=100, default='')          # 文档的下载地址
    company = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)     # 保险公司

    # 平台控制项
    create_time = DateTimeField(default=datetime.now)           # 创建时间，主要用于排序
    is_hidden = BooleanField(default=False)             # 已隐藏，用于控制保险文档是否显示在用户界面
    meta = {
        'ordering': ['-create_time']
    }

SUBMIT_STYLE = (
    ('platform', '平台上传'),
    ('input', '系统录入'),
    ('submit', '手动提交'),
)
    #添加中介渠道
class Intermediary(Document, DataTools):
    intermediary_name = StringField(max_length=16, default='')               # 中介名称
    intermediary_introduce = StringField(default='')  #中介介绍
    intermediary_phone = StringField(default='')#中介电话
    intermediary_profit_point = FloatField(default=0.0)                     # 中介渠道利润点（例如5个利润点，就是5%）2017修改为浮点型可保存8.88%类数据
    #intermediary_company_list = ListField(StringField(max_length=100, default=""), default=[])          # 包含的子公司列表
    intermediary_company_list = ListField(ReferenceField(InsuranceCompany,reverse_delete_rule=PULL), default=[])        # 包含的子公司列表
    state = BooleanField(default=True)             #1True-显示， 0False-隐藏 
    create_time = DateTimeField(default=datetime.now)           # 创建时间，主要用于排序
    #2017新添加字段
    plate_number_list = ListField(StringField(max_length=100, default=""), default=[])          # 可保车牌号
    order_car_type = ListField(StringField(max_length=100, default=""), default=[])         #可保货物种类九座一下客车和货车

    meta = {
        'ordering': ['-create_time']
    }

# 产品货物费率清单
class ProductsRateList(EmbeddedDocument):
    good_type = StringField(default='')       #货物类型（货物大类）
    products_rate = FloatField(default=0.0)           # 产品费率
    insurance_rate = FloatField(default=0.0)           # 保险费率
    commission_ratio =FloatField(default=0.0)      #产品手续费比例
#产品
class InsuranceProducts(Document, DataTools):
    PRODUCT_TYPE = (
        ('car', '运单保险'),
        ('batch', '车次保险'),
        ('ticket', '单票保险'),
        ('wlgsqnwlzrx', '物流公司全年物流责任险'),
        ('dcqnwlzrx', '单车全年物流责任险'),
        ('gzzrx', '雇主责任险'),
        ('jdclbx', '机动车辆保险'),
        ('ywx', '人身险'),
    )
    INSURANCE_TYPE = (
         ('', '未选择'),             
        ('transport', '货物运输保险'),
        ('freight', '物流责任保险'),
        ('car', '车次保险'),
    )
    #添加货物类型
    GOOD_TYPE = (
       ('ordinary_good', '普通货物'),
       ('fragile_articles', '易碎品'),
       ('equipment', '普通机器设备'),
       ('precision_instrument', '精密仪器'),
       ('fresh', '水果、蔬菜'),
       ('second_hand', '二手货'),
       ('drug', '药品（疫苗除外）'),
       #2017/6/19添加字段
       ('commodity_car', '商品车'),
       ('used_car', '二手车'),
       ('furniture', '家具（红木家具除外）'),
#        ('frozen_product', '冷藏冷冻品'),

   
    )
    #2017/5/22添加产品来源渠道
    CREATE_WAY =(
                 ("yzb","运之宝"),
                 ("hjb","汇聚宝")
                 
    )
    USER_TYPE =(
                 ("person","货主"),
                 ("company","物流公司")
                 
    )

    # 基本信息
    name = StringField(max_length=16, default='')               # 产品名称
    paper_id = StringField(default='')                      # 编号
    company = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)        # 保险公司
    product_type = StringField(choices=PRODUCT_TYPE)                # 产品类型
    insurance_type = StringField(choices=INSURANCE_TYPE)                # 险种类型
    rate = FloatField(default=0.0)                              # 费率（车次保险产品费率）
    documents = ListField(ReferenceField(InsuranceDocument, reverse_delete_rule=PULL), default=[])         # 保险文档
    #添加字段
    product_rate_list = ListField(EmbeddedDocumentField(ProductsRateList), default=[])              #货物类型费率清单
    product_introduce = StringField(default='')  #产品介绍
    product_characteristic = StringField(default='')#产品特点
    commission_ratio = FloatField(default=0.0) #产品手续费比例（车次保险产品）
    insurance_company_rate = FloatField(default=0.0)           # 保险公司费率（车次保险产品）
    #2016/09/12添加字段
    priority = IntField(default=50)    # 优先级，默认为50，建议值为1~100之间
    no_insurable_route = ListField(StringField(max_length=100, default=""), default=[])                         # 不可保路线
    insurance_price_min = IntField(default=0)                    # 可保货物价值最小值
    insurance_price_max = IntField(default=0)                        #  可保货物价值最小值
    #2016/11/03添加字段
    intermediarys = ListField(ReferenceField(Intermediary,reverse_delete_rule=PULL), default=[])         # 中介渠道
    
    #2017/5/22添加与汇聚宝对接适配参数
    create_way = StringField(max_length=20, choices=CREATE_WAY, default='yzb')          # 渠道来源
    third_party_url = StringField(max_length=2048,  default='')          # 渠道对接链接
    third_product_number = StringField(max_length=20,  default='')          # 第三方产品编号
    merchant_number = StringField(max_length=200,  default='') #渠道商户编号
    user_type_list = ListField(StringField(max_length=100, default=""), default=['person','company'])                         # 产品可保订单类别
    lowest_price = IntField(default=0)                    # #产品最低保费单位分
    insurance_lowest_price = IntField(default=0)              # 保险公司最低保费单位分
    
    #20170630添加免赔额度
    deductible = StringField(max_length=1000,  default='')  #免赔额度
    risks = StringField(max_length=1000,  default='')  #险别
    
    

    # 平台控制项
    create_time = DateTimeField(default=datetime.now)           # 创建时间，主要用于排序
    is_hidden = BooleanField(default=False)                     # 已隐藏，用于控制产品的有效性

    meta = {
        'ordering': ['-create_time']
    }

    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None,  cascade=None, cascade_kwargs=None,
             _refs=None, **kwargs):
        # 自动生成分产品编号
        if not self.paper_id:
            self.product_paper()
        else:
            self.test_cargo()
            print(self.no_insurable_route)
        return Document.save(self,  force_insert=force_insert, validate=validate, clean=clean,
                             write_concern=write_concern,  cascade=cascade, cascade_kwargs=cascade_kwargs,
                             _refs=_refs, **kwargs)

    def product_paper(self):
        self.paper_id = str(InsuranceProducts.objects().count() + 1).zfill(2)
   
   #验证产品是否关联货物     
    def test_cargo(self):
        if self.product_type == "ticket":
            rate_list=[]
            state=""
            for product_rate in self.product_rate_list:
                product_cargo_set = ProductCargo.objects(state=product_rate.good_type, product=self)
                rate_list.append(product_rate.good_type)
                print(rate_list)
                if not  product_cargo_set:
                    state = True
            if state == True:
                self.is_hidden = True
#             else:
#                  self.is_hidden = False    
                   
            product_cargo_list = ProductCargo.objects(product=self)
            for product_cargo_detail in product_cargo_list:
                if product_cargo_detail.state in rate_list:
                    continue
                else:
                    product_cargo_detail.delete()
                    
        else:
            product_cargo_list = ProductCargo.objects(product=self)
            for product_cargo_detail in product_cargo_list:
                product_cargo_detail.delete()


#客户
class Client(Document, DataTools):
    USER_TYPE = (
        ('registered', '注册用户'),
        ('transport', '物流公司'),
        ('driver', '司机'),
        ('boss', '货主'),
        # 废弃数据
        ('insurance', '理赔人员'),
        ('lawyer', '律师'),
        # 废弃数据结束
        #2016/12/01添加客户身份
        ('owner', '车主'),
    )
    USER_CLASSIFY = (
        ('', '无'),
        ('singleLine', '专线'),
        ('multiLine', '货代'),
        ('individuals', '个人'),
        ('units', '单位'),
    )
    # 基本信息
    paper_id = StringField(default='')                          # 编号
    balance = IntField(default=0)                   # 账户余额
    user = ReferenceField(User, reverse_delete_rule=CASCADE)  # 用户，其中User已经具有的属性包括：password, email, first_name, last_name
    profile = EmbeddedDocumentField(UserProfile, default=UserProfile)  # 属性（内嵌文档）
    create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序
    certificate_time = DateTimeField()  # 认证时间
    password = StringField(default='')          # 用户密文密码：Sha1加密

    # 第三方登录
    has_password = BooleanField(default=False)          # 标记是否有密码，如果没有密码则不支持原始登录方式
    wx_id = StringField(max_length=50, default='')      # 微信id，若有则表示该用户已绑定微信帐号。

    # 推荐系统
    referee = ReferenceField(User, reverse_delete_rule=NULLIFY)     # 推荐人，可以为空
    referee_code = StringField(default="")          # 推荐码，自动生成

    # 实名认证信息
    user_type = StringField(max_length=30, choices=USER_TYPE, default='registered')  # 用户类型
    # 用户分类，仅用于物流公司和货主，其中物流公司的合法值为'singleLine','multiLine'
    # 货主的合法值为'individuals','units'
    user_classify = StringField(max_length=20, choices=USER_CLASSIFY, default='')
    # 人
    name = StringField(max_length=16, default='')                   # 姓名
    national_id = StringField(max_length=18, default='')            # 身份证号
    national_image = StringField(default='')                        # 身份证照片
    national_image_down = StringField(default='')                        # 身份证照片下面
    national_effective_time = DateTimeField()                          # 身份证有效时间
    driver_id = StringField(max_length=18, default='')              # 驾驶证号
    driver_image = StringField(default='')                          # 驾驶证照片
    # 车
    plate_number = StringField(max_length=10, default='')            # 车牌号
    plate_number_plus = StringField(max_length=10, default='')            # 挂车牌号
    plate_image = StringField(default='')                           # 行驶证照片
    car_type = StringField()                    # 车辆类型
    holder = StringField()                      # 所有人
    use_property = StringField()                # 使用性质
    brand_digging = StringField()               # 品牌型号
    engine_number = StringField()               # 发动机号
    issue_date = DateTimeField()                # 发证日期
    transportation_license_id = StringField(max_length=30, default='')         # 营运证，车的运输许可证
    transportation_image = StringField(default='')                  # 营运证照片
    transportation_start = StringField(max_length=20, choices=PROVINCE_ENUM, default='')                 # 运输起始省份
    transportation_end = StringField(max_length=20, choices=PROVINCE_ENUM, default='')                   # 运输终点省份
    # 公司
    company_name = StringField(default='')                          # 公司名称
    operating_permit_id = StringField(default='')                      # 道路运输经营许可证，业户的运输许可证
    operating_permit_image = StringField(default='')                      # 道路运输经营许可证照片
    business_license_id = StringField(max_length=30, default='')        # 营业执照
    business_license_image = StringField(default='')        # 营业执照照片
    organ = StringField(max_length=20, default='')                   # 组织机构代码
    organ_image = StringField(default='')                   # 组织机构代码照片
    tax_id = StringField(max_length=20, default='')                   # 税务登记码
    tax_image = StringField(default='')                   # 税务登记证照片

    # 设置
    is_show_image = BooleanField(default=True)  # 是否在手机网络下显示图片
    is_show_alert = BooleanField(default=True)  # 是否接收活动推送、订单提醒
    is_location_service = BooleanField(default=True)  # 是否接受位置服务

    #设置默认投保的产品
    product = ReferenceField(InsuranceProducts, reverse_delete_rule=CASCADE)        #--------------------------- 默认运单产品
    product_car = ReferenceField(InsuranceProducts, reverse_delete_rule=CASCADE)        # 默认运单产品
    product_batch = ReferenceField(InsuranceProducts, reverse_delete_rule=CASCADE)        # 默认车次产品
    product_ticket = ReferenceField(InsuranceProducts, reverse_delete_rule=CASCADE)        # 默认单票 产品
    
    #二维码图片
    QR_code_image = StringField(default='')                  # 二维码图片

    meta = {
        'ordering': ['-create_time', 'license_time']
    }
   
    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None,  cascade=None, cascade_kwargs=None,
             _refs=None, **kwargs):
        # 自动生成推荐码
        if not hasattr(self, 'id') or not self.referee_code:
            need_referee_code = True
            referee_code = ""
            count = 0
            client_set = Client.objects()
            while count < 100 and need_referee_code:
                referee_code = FormatTools.get_random_referee_code()
                if client_set.filter(referee_code=referee_code).count() > 0:
                    count += 1
                else:
                    need_referee_code = False
            if need_referee_code:
                exception = DException(trackback="tools_document DocumentTools get_paper_id line 190 count > 50")
                exception.exception = 'too many paper id'
                exception.type = "获取推荐码失败"
                exception.save()
            else:
                self.referee_code = referee_code

        return Document.save(self,  force_insert=force_insert, validate=validate, clean=clean,
                             write_concern=write_concern,  cascade=cascade, cascade_kwargs=cascade_kwargs,
                             _refs=_refs, **kwargs)

# 认证记录，用于提交用户实名认证申请
class Certificate(Document, DataTools):
    CERTIFICATE_STATE = (
        ('init', '待审核'),
        ('success', '已审核'),
        ('fail', '已退回'),
    )

    TRANSPORT_REQUIRED = (
#         ("product_car", "运单保险"),
#         ("product_batch", "车次保险"),
#         ("product_ticket", "单票保险"),
        ("name", "姓名"),
        ("national_id", "身份证号"),
        ("national_image", "身份照片上"),
        ("national_image_down", "身份照片下"),
        ("national_effective_time", "身份证有效期"),
        ("company_name", "单位名称"),
        ("business_license_id", "营业执照编号"),
        ("business_license_image", "营业执照"),
        ("organ", "组织机构代码"),
        # ("organ_image", "组织机构证"),
        # ("tax_id", "税务登记码"),
        # ("tax_image", "税务登记证"),
        ("operating_permit_id", "道路运输经营许可证编号"),
        ("operating_permit_image", "道路运输经营许可证"),
    )
    DRIVER_REQUIRED = (
#         ("product_car", "运单保险"),
#         ("product_batch", "车次保险"),
#         ("product_ticket", "单票保险"),
        ("name", "姓名"),
        ("national_id", "身份证号"),
        ("national_image", "身份照片上"),
        ("national_image_down", "身份照片下"),
        ("national_effective_time", "身份证有效期"),
        ("driver_id", "驾驶证号"),
        ("driver_image", "驾驶证"),
        ("plate_image", "行驶证"),
        ("plate_number", "车牌号"),
        ("car_type", "车辆类型"),
        ("holder", "所有人"),
        ("use_property", "使用性质"),
        ("brand_digging", "品牌型号"),
        ("engine_number", "发动机号"),
        ("issue_date", "发证日期"),
        ("transportation_license_id", "营运证号"),
        ("transportation_image", "营运证"),
    )
    INDIVIDUALS_REQUIRED = (
#         ("product_car", "运单保险"),
#         ("product_batch", "车次保险"),
#         ("product_ticket", "单票保险"),
        ("name", "姓名"),
        ("national_id", "身份证号"),
        ("national_image", "身份照片上"),
        ("national_image_down", "身份照片下"),
        ("national_effective_time", "身份证有效期"),
    )
    UNIT_REQUIRED = (
#         ("product_car", "运单保险"),
#         ("product_batch", "车次保险"),
#         ("product_ticket", "单票保险"),
        ("name", "姓名"),
        ("national_id", "身份证号"),
        ("national_image", "身份照片上"),
        ("national_image_down", "身份照片下"),
        ("national_effective_time", "身份证有效期"),
        ("company_name", "单位名称"),
        ("business_license_id", "营业执照编号"),
        ("business_license_image", "营业执照"),
        ("organ", "组织机构代码"),
    )

    FAIL_REASON = (
        ('absence', '缺少证件信息'),
        ('breezing', '证件信息不清晰'),
        ('truth', '证件真实性不足'),
        ('equal', '证件信息与提交的认证信息不符'),
        ('timeout', '证件过期'),
        ('false', '证件真实性不足'),
    )

    IDENTIFICATION_TYPE = (
        ('national', '身份证'),
        ('driver', '驾驶证'),
        ('plate', '行驶证'),
        ('transportation', '营运证'),
        ('operating', '道路运输经营许可证'),
        ('business', '营业执照'),
        ('organ', '组织机构'),
        # ('tax', '税务登记证'),
    )
    state = StringField(max_length=20, choices=CERTIFICATE_STATE, default='init')          # 认证状态
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 需要认证的用户
    # 需要认证的目标
    user_type = StringField(max_length=30, choices=Client.USER_TYPE, default='registered')  # 用户类型
    # 用户分类，仅用于物流公司和货主，其中物流公司的合法值为'singleLine','multiLine'
    # 货主的合法值为'individuals','units'
    user_classify = StringField(max_length=20, choices=Client.USER_CLASSIFY, default='')
    # 实名认证信息
    # 人
    name = StringField(max_length=16, default='')                   # 姓名
    national_id = StringField(max_length=18, default='')            # 身份证号
    national_image = StringField(default='')                        # 身份证照片
    national_image_down = StringField(default='')                        # 身份证照片下面
    national_effective_time = DateTimeField()                          # 身份证有效时间
    driver_id = StringField(max_length=18, default='')              # 驾驶证号
    driver_image = StringField(default='')                          # 驾驶证照片
    driver_image_list = ListField(StringField(max_length=100, default=""), default=[])                         # 驾驶证照片列表
    qualification_image_list = ListField(StringField(max_length=100, default=""), default=[])                  # 从业资格证照片
    # 车
    plate_number = StringField(max_length=10, default='')            # 车牌号
    plate_number_plus = StringField(max_length=10, default='')            # 挂车牌号
    plate_image = StringField(default='')                           # 行驶证照片
    plate_image_list = ListField(StringField(max_length=100, default=""), default=[])                   # 行驶证照片
    car_type = StringField()                    # 车辆类型
    holder = StringField()                      # 所有人
    use_property = StringField()                # 使用性质
    brand_digging = StringField()               # 品牌型号
    engine_number = StringField()               # 发动机号
    issue_date = DateTimeField()                # 发证日期
    transportation_license_id = StringField(max_length=30, default='')         # 营运证，车的运输许可证
    transportation_image = StringField(default='')                  # 营运证照片
    transportation_image_list = ListField(StringField(max_length=100, default=""), default=[])                  # 营运证照片列表
    transportation_start = StringField(max_length=20, choices=PROVINCE_ENUM, default='')            # 运输起始省份
    transportation_end = StringField(max_length=20, choices=PROVINCE_ENUM, default='')            # 运输终点省份
    # 公司
    company_name = StringField(default='')                          # 公司名称
    operating_permit_id = StringField(default='')                      # 道路运输经营许可证，业户的运输许可证编号
    operating_permit_image = StringField(default='')                      # 道路运输经营许可证照片
    business_license_id = StringField(max_length=30, default='')        # 营业执照编号
    business_license_image = StringField(default='')        # 营业执照照片
    organ = StringField(max_length=20, default='')                   # 组织机构代码
    organ_image = StringField(default='')                   # 组织机构代码照片
    tax_id = StringField(max_length=20, default='')                   # 税务登记码
    tax_image = StringField(default='')                   # 税务登记证照片

    #设置默认投保的产品
    product_car = ReferenceField(InsuranceProducts, reverse_delete_rule=CASCADE)        # 默认运单产品
    product_batch = ReferenceField(InsuranceProducts, reverse_delete_rule=CASCADE)        # 默认车次产品
    product_ticket = ReferenceField(InsuranceProducts, reverse_delete_rule=CASCADE)        # 默认单票 产品

    create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序
    certificate_time = DateTimeField()  # 认证时间

    # 认证结果
    failed_reason = StringField(choices=FAIL_REASON)                # 认证失败的原因
    failed_fields = ListField(StringField(choices=IDENTIFICATION_TYPE), default=[])            # 认证失败的类型
    note = StringField(max_length=100, default='')                  # 认证结果的备注，将会提供给用户查看认证失败的具体原因

    meta = {
        'ordering': ['-create_time']
    }

    def verify_success(self):
        if not self.client.paper_id:
            self.client_paper()
        else:
            raise ValidationError("已认证用户无法二次认证")
        self.state = 'success'
        self.certificate_time = datetime.now()
        self.save()
        self.client.user_type = self.user_type
        self.client.user.first_name = self.user_type
        self.client.user.save()
        self.client.certificate_time = self.certificate_time
        self.client.user_classify = self.user_classify
        self.client.organ_image = self.organ_image
        self.client.save()

    def verify1(self):
        if self.user_type == 'transport':
            fields = Certificate.TRANSPORT_REQUIRED
        elif self.user_type == 'driver':
            fields = Certificate.DRIVER_REQUIRED
        elif self.user_type == 'boss':
            if self.user_classify == 'units':
                fields = Certificate.UNIT_REQUIRED
            else:
                fields = Certificate.INDIVIDUALS_REQUIRED
        elif self.user_type == 'owner':
            fields = Certificate.INDIVIDUALS_REQUIRED
        else:
            raise ValidationError("无法识别的认证目标")
        for field, name in fields:
            if not getattr(self, field):
                raise ValidationError("{0}不能为空".format(name))
        for field, name in fields:
            setattr(self.client, field, getattr(self, field))
        self.verify_success()
        
    def verify(self):
        if self.user_type == 'transport':
            fields = Certificate.TRANSPORT_REQUIRED
        elif self.user_type == 'driver':
            fields = Certificate.DRIVER_REQUIRED
        elif self.user_type == 'boss':
            if self.user_classify == 'units':
                fields = Certificate.UNIT_REQUIRED
            else:
                fields = Certificate.INDIVIDUALS_REQUIRED
        elif self.user_type == 'owner':
            fields = Certificate.INDIVIDUALS_REQUIRED
        elif self.user_type == 'registered':
            fields = Certificate.DRIVER_REQUIRED
        else:
            raise ValidationError("无法识别的认证目标")
        for field, name in fields:
            if  getattr(self, field):
                setattr(self.client, field, getattr(self, field))

        self.verify_success()

    def client_paper(self):
        self.client.paper_id = str(Client.objects(user_type='transport').count() + Client.objects(user_type='driver').count() + Client.objects(user_type='boss').count() +Client.objects(user_type='owner').count()+ 1).zfill(4)


#理赔人员
class Claim(Document, DataTools):
    # 基本信息
    user = ReferenceField(User, reverse_delete_rule=CASCADE)  # 用户，其中User已经具有的属性包括：password, email, first_name, last_name
    profile = EmbeddedDocumentField(UserProfile, default=UserProfile)  # 属性（内嵌文档）
    company = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)         # 保险公司
    name = StringField(max_length=16, default='')                   # 姓名
    create_time = DateTimeField(default=datetime.now)               # 创建时间，主要用于排序

    # 第三方登录
    has_password = BooleanField(default=False)          # 标记是否有密码，如果没有密码则不支持原始登录方式
    wx_id = StringField(max_length=50, default='')      # 微信id，若有则表示该用户已绑定微信帐号。

    meta = {
        'ordering': ['-create_time']
    }


#律师
class Lawyer(Document, DataTools):
    # 基本信息
    user = ReferenceField(User, reverse_delete_rule=CASCADE)  # 用户，其中User已经具有的属性包括：password, email, first_name, last_name
    profile = EmbeddedDocumentField(UserProfile, default=UserProfile)  # 属性（内嵌文档）
    name = StringField(max_length=16, default='')                   # 姓名
    create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序

    # 第三方登录
    has_password = BooleanField(default=False)          # 标记是否有密码，如果没有密码则不支持原始登录方式
    wx_id = StringField(max_length=50, default='')      # 微信id，若有则表示该用户已绑定微信帐号。

    meta = {
        'ordering': ['-create_time']
    }


# 优惠卷
class Coupon(Document, DataTools):
    name = StringField(default='')              # 优惠卷的名称
    describe = StringField(default='')          # 优惠卷的描述，向用户详细描述优惠卷的适用范围及使用限制
    product = ReferenceField(InsuranceProducts, reverse_delete_rule=CASCADE)        # 产品

    end_date = DateTimeField()          # 优惠卷使用的截止日期
    max_count = IntField(default=-1)            # 优惠卷使用次数上限，若为负数则表示不限制使用次数
    min_price = IntField(default=0)             # 优惠券使用要求的费用下限，即最低消费，若为负数则表示不限制
    max_price = IntField(default=-1)            # 优惠卷优惠的金额上限，即最大优惠金额，若为负数则表示不限制
    # 注意：此值为优惠比例而不是应付比例，应在创建优惠卷界面中着重强调！！！
    rate = FloatField(default=0)                # 优惠卷的优惠比例，值为0~1之间的浮点数。如8折卷(20% Off)此值应为:0.2

    # 平台控制项
    create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序
    # 当优惠卷无效时应自动设置为True以保证用户界面足够简洁
    is_hidden = BooleanField(default=False)             # 已隐藏，用于控制优惠卷是否出现在用户界面中

    meta = {
        'ordering': ['-create_time']
    }


#  优惠描述
class UseCoupon(Document, DataTools):
    coupon = ReferenceField(Coupon, reverse_delete_rule=CASCADE)         # 优惠券
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 对应的用户
    count = StringField()             # 优惠券使用次数
    user_time = DateTimeField()           # 使用时间
    create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序
    meta = {
        'ordering': ['-create_time']
    }


# 车次清单
class BatchList(EmbeddedDocument):
    transport_id = StringField(max_length=50, default='')           # 运单号
    startSiteName = StringField(default='')           # 起运地
    targetSiteName = StringField(default='')          # 目的地
    commodityName = StringField()           # 货物名称
    commodityCases = IntField()           # 货物数量

#货物大类（弃用）
class CargoType (Document, DataTools):
    ct_name = StringField(max_length=20, default='')            # 货物大类
    ct_state = BooleanField(default=True)             #1True-显示， 0False-隐藏 ，用于控制货物是否显示在用户界面 
    ct_priority = IntField(default=50)    # 货物优先级
#货物类型
class Cargo (Document, DataTools):
    #cargo_type = StringField(max_length=20, default='')            # 货物大类
    #cargo_type = ReferenceField(CargoType, reverse_delete_rule=CASCADE)     # 货物大类  
    cargo_number = StringField(max_length=20, default='')            # 货物编码
    cargo_name = StringField(max_length=200, default='')            # 货物名称
    cargo_priority = IntField(default=50)    # 货物优先级
    state = BooleanField(default=True)             #True-显示， False-隐藏 ，用于控制货物是否显示在用户界面 
    
#货物类型与产品关联表
class ProductCargo (Document, DataTools):
    product = ReferenceField(InsuranceProducts, reverse_delete_rule=CASCADE)     # 对应产品          
    cargo = ReferenceField(Cargo, reverse_delete_rule=CASCADE)     # 对应货物
    state = StringField(max_length=200, default='')            # 货物类型  (订单货物大类：普通货物等)
    
    
# 订单
class Ordering(Document, DataTools):
    ORDER_TYPE = (
        ('wait', '待提交'),         
        ('init', '未支付'),
        ('paid', '已支付'),
        ('done', '已完成'),
    )
    FIELD_TUPLE = (
        ('paper_id', '订单号'),
        ('insurance_product', '产品名称'),
        ('insured', '被保险人姓名'),
        ('startSiteName', '起运地'),
        ('targetSiteName', '目的地'),
        ('pay_time', '保险起期'),
        ('insurance_price', '货物价值'),
        ('transport_id', '运单号'),
        ('plate_number', '车牌号'),
        ('commodityName', '货物名称'),
        ('commodityCases', '货物数量'),
        ('batch_url', '车次清单的下载地址'),
        ('batch_image_list', '车次清单的图片'),
        ('batch_list', '车次清单'),
    )
    INSURANCE_FIELD_TUPLE = (
        ('submit_style', '业务来源'),
        ('paper_id', '订单号'),
        ('insurance_id', '保单号'),
        ('insurance_product', '产品名称'),
        ('company', '保险公司'),
        ('client', '投保人'),
        ('insured', '被保险人姓名'),
        ('client', '推荐人'),
        ('startSiteName', '起运地'),
        ('targetSiteName', '目的地'),
        ('expectStartTime', '保险起期'),
        ('insurance_price', '货物价值'),
        ('insurance_rate', '保险费率'),
        ('pay_price', '保费'),
        ('transport_id', '运单号'),
        ('plate_number', '车牌号'),
        ('commodityName', '货物名称'),
        ('commodityCases', '货物数量'),
    )
    TRANSPORT_TYPE=(
#         ('1','陆运'),
#         ('2','空运'),
#         ('3','海运'),
#         ('4','铁运'),
#         ('5','联运'),   
            ('1','汽运'),   
            ('3','水运'),   
            ('5','联运'),   
            ('2','空运'),   
            ('4','铁路'),   
            
    )
    
    COMMON_GOOD=(
             "纺织品","非危险品农药",
             "金属（不含贵金属）","木制品",
             "皮革","食品、饮料",
             "塑料","鞋帽",
             "油脂","杂物",
             "纸制品","其他全新普通货物",
             "一般化工类产品（非危化品）"           
    )
    
    PICTURE_UPLOAD_PATH=(
             "","历史数据",
             "yzb","运至宝",
            "hjb","汇聚宝",
    )
    
    
    PACK_METHOD=(
            (("托盘",'101'),( 
                     ("1001","托盘(Pallet)"),
                      )
             ) , 
#     2017/6/7汇聚宝对接        
            (("桶装",'801'),( 
                     ("8001","桶装"),
                      )
             ) , 
            (("袋装",'901'),( 
                     ("9001","袋装"),
                      )
             ) , 
            (("散装",'1001'),( 
                     ("10001","散装"),
                      )
             ) , 
            (("纸箱",'1101'),( 
                     ("11001","纸箱"),
                      )
             ) , 
            (("木箱",'1201'),( 
                     ("12001","木箱"),
                      )
             ) , 
            (("裸装",'1301'),( 
                     ("13001","裸装"),
                      )
             ) ,      
            
#             (("捆包状包装",'201'),(
#                       ("2001","包、捆（Bale）B/S"),
#                       )
#              ),
#             (("袋装包装",'301'),(
#                      ("3001","袋(Bag)Bgs"),
#                      ("3002","麻袋(GunnyBag)Bgs"),
#                      ("3003","纸袋(PaperBag)Bgs"),
#                      ("3004","布袋(Sack)Sks"),
#                      ("3005","人造革袋(LeatheroidBag)Bgs"),
#                      )
#              ),
#             (("箱状包装",'401'),(
#                      ("4001","各种木箱(Case)C/S"),
#                      ("4002","纸箱(Carton)Ctns"),
#                      ("4003","胶板箱(Plywood)C/S,/CS"),
#                      ("4004","板条、亮格箱(Crate)Crts"),
#                      )
#              ),    
#             (("桶状包装",'501'),(
#                      ("5001","各种金属桶(IronDrums)Drms,D/S"),
#                      ("5002","塑料桶(PlasticDrums)"),
#                      ("5003","鼓形木桶(Barrel)Brls"),
#                      ("5004","大木桶(Hogshead)Hghds"),
#                      ("5005","小木桶(Keg)Kgs"),
#                      ("5006","纸板桶(FibreDrum)"),
#                      )
#              ),   
#             (("其他形状包装",'601'),(
#                      ("6001","捆扎(Bundle)Bdle"),
#                      ("6002","卷筒等(Roll,Reel,Coil)"),
#                      ("6003","篓筐(Basket)Bkts"),
#                      ("6004","坛、甏(Jar)"),
#                      ("6005","瓶(Bottle)"),
#                      ("6006","钢瓶(Cylinder)"),
#                      ("6007","罐(Can)"),
#                      )
#              ),
#             (("裸状包装",'701'),(
#                      ("7001","锭(Ingot)Igts"),
#                      ("7002","块(Pig)"),
#                      ("7003","管(Pipe)"),
#                      ("7004","条、棒(Bar)"),
#                      ("7005","张(Sheet)Shts"),
#                      ("7006","个、件(Piece)Pcs"),
#                      ("7007","头、匹(Head)Hds"),
#                      ("7008","裸装(Unpacked)"),
#                      )
#              ),    
                 
                 
                 
                 
    )
    
    UP_STATE = (
        ('picture', '图片'),
        ('pdf', 'pdf文件'),
        ('web_url', 'web网址'),
    )
    
    PAPER_STATE=(
         ('', '未选择'),
         ('TY', '统一社会信用代码'),
         ('Z', '组织机构代码'),
     )

    # 基本信息
    paper_id = StringField(max_length=50, default='')           # 订单号
    insurance_id = StringField(default='')                # 保单号
    insurance_image = StringField(default='')                   # 电子保单图片地址--------------------------已弃用
    insurance_image_list = ListField(StringField(max_length=1000, default=""), default=[])          # 电子保单图片地址列表,
    submit_style = StringField(choices=SUBMIT_STYLE, default='platform')                # 提交类型
    product_type = StringField(choices=InsuranceProducts.PRODUCT_TYPE)                # 产品类型
    insurance_type = StringField(choices=InsuranceProducts.INSURANCE_TYPE)                # 险种类型
    #无用
    name = StringField(max_length=16, default='')                   # 被保险人姓名-----------------------
    insured = StringField(max_length=100, default='')                   # 被保险人姓名（正在用）
    organ = StringField(max_length=16, default='')                   # 被保险人组织机构代码-----------------------

    state = StringField(choices=ORDER_TYPE, default='init')            # 订单状态

    company = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)         # 保险公司
    insurance_product = ReferenceField(InsuranceProducts, reverse_delete_rule=CASCADE)     # 对应产品
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 对应的用户
#     client_insured = ReferenceField(Client, reverse_delete_rule=CASCADE)  #被保人带出认证用户 12.26
    
    #与大东对接添加字段
    good_type=StringField(default='')                # 对应产品的货物类型("普通货物、易碎品等)
    transport_type=StringField(choices=TRANSPORT_TYPE, default="1")            #运输方式
    common_good_detail=StringField( default="")            #普通货物类别（弃用现在改用cargo字段）
    pack_method = StringField( default="")            #货物包装方式
    cargo = ReferenceField(Cargo, reverse_delete_rule=CASCADE)     # 对应货物(货物类型对象)

    transport_id = StringField(max_length=50, default='')           # 运单号
    plate_number = StringField(max_length=10, default='')                # 车牌号
    plate_number_plus = StringField(max_length=10, default='')            # 挂车牌号

    batch_url = StringField(max_length=100, default='')          # 车次清单的下载地址
    batch_image = StringField(default='')                           # 车次清单的图片-----------------------------------------
    batch_image_list = ListField(StringField(max_length=100, default=""), default=[])          # 车次清单的图片地址列表,
    batch_list = ListField(EmbeddedDocumentField(BatchList), default=[])           # 车次清单

    #物流公司更新字段
    startSiteName = StringField(default='')           # 起运地
    targetSiteName = StringField(default='')          # 目的地
    commodityName = StringField(max_length=200)           # 货物名称
    commodityCases = StringField(max_length=10)          # 货物数量
    expectStartTime = DateTimeField()           # 提交订单时间

    # blNo = StringField(default='')          # 提单号
    # departGroup = StringField()             # 发车批次
    # itemdetailcode = StringField()          # 标的物代码
    # kindCode = StringField()            # 险别代码
    # goodsValue = StringField()          # 货物价值
    # packing = StringField(default='')           # 包装
    # quantity = StringField(default='')          # 件数
    # transportType = StringField()           # 运输方式
    # loadType = StringField()            # 装载方式
    # saleCount = StringField()           # 预计营业收入
    # expectStartTime = DateTimeField()           # 预计起运时间
    # deliveryPayment = StringField()         # 代收货款
    # actualCost = StringField()          # 实际运费
    # consignee = StringField()           # 收货人
    # consigneeTel = StringField()            # 收货人电话
    # consignor = StringField()           # 托运人
    # consignorTel = StringField()            # 托运人电话
    # driverName = StringField()          # 司机姓名
    # driverTel = StringField()           # 司机电话
    # remark = StringField()              # 备注
    # weight = StringField()              # 重量

    start_date = DateTimeField()                            # 投保日期-----------------------------
    effective_date = DateTimeField()                            # 生效日期---------------------------------
    insurance_rate = FloatField(default=0.0)                # 保险折后费率
    insurance_price = IntField(default=0)                   # 货物价值,即保险中承诺的最大赔付金额，单位为分
    price = IntField(default=0)                             # 应缴纳保费   保费金额，即需要用户缴纳的保险费用的金额，单位为分
    pay_price = IntField(default=0)                         # 实付保费金额，即用户实际缴纳的保险费用，单位为分
    pay_time = DateTimeField()           # 保险起期
    old_price = IntField(default=0)                         # 不打折之前的保费（订单费用）
    coupon = ReferenceField(Coupon, reverse_delete_rule=CASCADE)        # 使用的优惠卷
    #后台详情界面新增字段
    insurance_company_rate = FloatField(default=0.0)                # 保险公司费率
    insurance_company_price = IntField(default=0)                 # 保险公司费用（保费）
    real_profit = IntField(default=0)                 # 实际利润=实付保费-保险公司费用+手续费
    commission_ratio = FloatField(default=0.0) #产品手续费比例
    commission_price = IntField(default=0)                 # 产品手续费费用（保险公司费用×产品手续费比例）

    # 平台控制项
    create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序
    is_hidden = BooleanField(default=False)             # 已隐藏，用于控制保单是否显示在用户界面
    is_compensate = BooleanField(default=False)             # 已理赔，用于分类显示保单，冗余数据，在发起理赔时自动改写
    #10/25添加和乐卡对接字段
    log_certificate_number = StringField(default='')           # 乐卡对接保存证件号（公司保存营业执照号，个人保存身份证号码）
    
    #2017/3/22添加投保人姓名身份证号，被保人身份证号码
    client_name = StringField(max_length=100, default='')                   # 投保险人姓名
    client_id_card = StringField(max_length=19, default='')                   # 投保险人身份证号码
    insured_id_card = StringField(max_length=19, default='')                   # 被保险人身份证号码
    
    #20175/23汇聚宝对接补充信息
    note_detail = StringField(max_length=1600, default='')                   # 备注信息
    third_paper_id = StringField(max_length=100, default='')                   # 第三方订单号
    client_type = StringField(max_length=160, default='')                   # 被保用户身份
    #2017/11/28添加投保人身份
    tb_client_type = StringField(max_length=160, default='')                   # 投保用户身份
    #2017/07/17添加保单上传路径
    picture_upload_path = StringField(choices=PICTURE_UPLOAD_PATH, default='yzb') 
    #2017/08/03添加砖头对接字段
    car_startSiteName = StringField(default='')           # 起运地
    car_targetSiteName = StringField(default='')          # 目的地
    
    #2017/10/29添加保单上传素材。与机动车保险一致可以上传三种保单
    #添加保单上传状态
    insurance_up_state = StringField(max_length=20, choices=UP_STATE, default='picture')               # 交强险上传状态
    
    #2017/11/28添加投保人身份(汇聚宝众安传值)
    tb_client_type = StringField(max_length=20, default='')                   # 投保用户身份
    holderCertNo = StringField(max_length=18, default='')                   # 投保人证件号
    taxpayerRegNum = StringField(max_length=20, default='')                   # 纳税人识别号 
    #车次保险添加
    tb_holderCertType = StringField(max_length=50,choices=PAPER_STATE, default='')#投保人证件类型
    bb_insureCertType = StringField(max_length=50, choices=PAPER_STATE,default='')#被保人证件类型
    bb_insureCertNo = StringField(max_length=18, default='')#被保人证件号

    meta = {
        'ordering': ['-create_time']
    }

    # 生成订单号
    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None,  cascade=None, cascade_kwargs=None,
             _refs=None, **kwargs):
        # 自动订单号编号
        if not self.paper_id:
            if self.state=='init':
                self.product_paper()
        #2017/6/20修改流程
        if self.state=='init':
            self.count_coupon()
            self.count_commission()
        return Document.save(self,  force_insert=force_insert, validate=validate, clean=clean,
                             write_concern=write_concern,  cascade=cascade, cascade_kwargs=cascade_kwargs,
                             _refs=_refs, **kwargs)
#         计算产品手续费
    def count_commission(self):
        product=self.insurance_product
        if self.product_type=='batch' or self.product_type=='car'  :
            self.commission_ratio =product.commission_ratio
        elif self.product_type == 'ticket':
            for product_rate in product.product_rate_list:
                if product_rate.good_type == self.good_type:
                    self.commission_ratio = product_rate.commission_ratio
                    break
        else:
            self.commission_ratio =0.0
        
#         产品优惠卷使用情况
    def count_coupon(self):
        use_coupon_set = UseCoupon.objects(client=self.client)#优惠卷
        #old_price
        if self.product_type=='batch' or self.product_type=='car'  :
            insurance_rate=self.insurance_product.rate
            self.insurance_company_rate = self.insurance_product.insurance_company_rate
            self.insurance_company_price = round( self.insurance_company_rate * 1000000 / 1000000 * self.insurance_price)
        else:
            for product_rate in self.insurance_product.product_rate_list: 
                a=self.good_type
                b=product_rate.good_type
                if product_rate.good_type==self.good_type:
                    insurance_rate=product_rate.products_rate
#                     self.insurance_rate = insurance_rate
                    self.insurance_company_rate = product_rate.insurance_rate
                    self.insurance_company_price = round( self.insurance_company_rate * 1000000 / 1000000 * self.insurance_price)
                    break
#         if insurance_rate==0:
#             data=[]
#             data['message'] = '您选择的保险产品，不包含您选择的投保货物'
            #raise ParameterError('您选择的保险产品，不包含您选择的投保货物')
        old_price = math.ceil(insurance_rate*1000000000 * float(self.insurance_price)/1000000000)
        #2017/6/7汇聚宝对接添加部分
        insurance_lowest_price =  self.insurance_product.insurance_lowest_price
        if self.insurance_company_price<insurance_lowest_price:
            self.insurance_company_price=insurance_lowest_price
        #2017/6/7汇聚宝对接添加部分end
        #众安5元处理
        a=self.company.paper_id
        if self.company.paper_id == settings.ZHONGAN_COMPANY_CODE:
           if self.insurance_company_price <500:
               self.insurance_company_price =500
               old_price=1000
                            
        pay_price = 0
        self.insurance_rate = insurance_rate
        if use_coupon_set:
            temp = 1.0
            item = None
            for use_coupon in use_coupon_set:
                if use_coupon.coupon.product == self.insurance_product:
                    if use_coupon.coupon.rate < temp:
                        if use_coupon.coupon.end_date > datetime.now():
                            temp = use_coupon.coupon.rate
                            item = use_coupon.coupon
            if temp and item:
                self.coupon = item
                self.insurance_rate = insurance_rate * 1000000 * temp / 1000000
                pay_price = round(old_price* 1000000 / 1000000 * temp )
            else:
                pay_price = round(old_price* 1000000 / 1000000 * temp )
        else:
            pay_price = round(old_price * 1000000 / 1000000 )
        #2017/6/7汇聚宝对接添加部分
        test_lowest_state='0'
        if  pay_price<self.insurance_product.lowest_price:
            pay_price=self.insurance_product.lowest_price
            test_lowest_state='1'
            
        if  old_price<self.insurance_product.lowest_price:
            old_price=self.insurance_product.lowest_price
            test_lowest_state='1'
        if test_lowest_state=='1':
            self.note_detail= '由于您投保的保费低于我们最低保费，我们按最低保费收取'
        self.price = pay_price
        self.old_price = old_price      

    def count_coupon1(self):
        use_coupon_set = UseCoupon.objects(client=self.client)
        old_price = math.ceil(self.insurance_product.rate * self.insurance_price)
        pay_price = 0
        if use_coupon_set:
            temp = 1.0
            item = None
            for use_coupon in use_coupon_set:
                if use_coupon.coupon.end_date > datetime.now():
                    if use_coupon.coupon.product == self.insurance_product:
                        if use_coupon.coupon.rate < temp:
                            temp = use_coupon.coupon.rate
                            item = use_coupon.coupon
            if temp and item:
                pay_price = round(self.insurance_product.rate * 1000000 / 1000000 * temp * self.insurance_price)
                self.coupon = item
                self.insurance_rate = self.insurance_rate * 1000000 * temp / 1000000
            else:
                pay_price = round(self.insurance_product.rate * 1000000 / 1000000 * self.insurance_price)

        else:
            pay_price = round(self.insurance_product.rate * 1000000 / 1000000 * self.insurance_price)
        self.price = pay_price
        self.old_price = old_price
        # self.price = self.insurance_price * self.insurance_rate
        # self.pay_price = self.insurance_price * self.insurance_rate

    def pay_money(self):
        if self.client.balance >= self.price:
            self.state = 'paid'
            self.pay_price = self.price
            self.pay_time = datetime.now()
            #2017/7/19后天点击付款直接付款2017/10/24打开扣余额部分
            self.client.balance -= self.price
            self.client.save()
            e=self.insurance_company_price
            if self.insurance_company_price>0:
                self.commission_price = self.insurance_company_price * self.commission_ratio
                self.real_profit = self.pay_price - self.insurance_company_price+self.commission_price 


    def product_paper(self):
        product_paper_id = self.insurance_product.paper_id
        company_paper_id = self.insurance_product.company.paper_id
        date_time = datetime.now().strftime("%Y%m%d")[2:]

        need_paper_id = True
        paper_id = ""
        count = 0
        order_set = Ordering.objects()
        while count < 100 and need_paper_id:
            random_number = FormatTools.get_random_product_paper_id().zfill(6)
            paper_id = product_paper_id+company_paper_id+date_time+random_number
            if order_set.filter(paper_id=paper_id).count() > 0:
                count += 1
            else:
                need_paper_id = False
        if need_paper_id:
            exception = DException(trackback="tools_document DocumentTools get_paper_id line 190 count > 50")
            exception.exception = 'too many paper id'
            exception.type = "生成订单号失败"
            exception.save()
        else:
            self.paper_id = paper_id


#交易纪录（充值、扣费）
class Transaction(Document):

    TRANSACTION_TYPE = (
        ('add', '收款'),
        ('minus', '退款'),
    )

    TRANSACTION_STATUS = (
        ('init', '未完成'),
        ('success', '成功'),
        ('failure', '失败'),
    )
    
    type = StringField(max_length=20, default='add', choices=TRANSACTION_TYPE)         # 交易类型
    status = StringField(max_length=20, default='init', choices=TRANSACTION_STATUS)         # 交易状态
    user = ReferenceField(User, reverse_delete_rule=CASCADE)            # 付款人
    amount = FloatField(default=0.0)            # 操作额度，单位fen
    create_time = DateTimeField(default=datetime.now)           # 时间
    channel = StringField(max_length=16, default='')            # 渠道
    order_no = StringField(max_length=32, default='')           # 订单号
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)    # 所属人
    result = StringField(max_length=2000, default='')            # 异步通知结果
    transaction_no = StringField(max_length=60, default='')          # 渠道交易号
    pingpp_no = StringField(max_length=60, default='')          # PING++订单号
    note = StringField(max_length=1024, default='')         # 备注
    p_type = StringField(max_length=20, default='')         #付款类型，是支付还是预存
    order_id = StringField(max_length=24, default='')         # 关联订单
    
    meta = {
        'ordering': ['-create_time']
    }

    def detail_data(self):
        return DataTools(self).detail_data(self._fields.items())


# 赔案
class Compensate(Document, DataTools):
    COMPENSATE_STATE = (
        ('init', '报案'),
        ('accept', '已受理'),
        ('done', '已结束'),
    )
    order = ReferenceField(Ordering, reverse_delete_rule=CASCADE)          # 保单
    state = StringField(choices=COMPENSATE_STATE, default='init')               # 赔单状态

    # 平台控制项
    create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 对应的用户
    is_hidden = BooleanField(default=False)             # 已隐藏，用于控制理赔单是否显示在用户界面

    meta = {
        'ordering': ['-create_time']
    }


#意见和建议
class Suggestions(Document, DataTools):
    description = StringField(max_length=200, default='')  # 描述
    create_time = DateTimeField(default=datetime.now)  # 创建时间

    meta = {
        'ordering': ['-create_time']
    }


#杨帆保险学堂
class InsuranceSchool(Document, DataTools):
    personal_profile = StringField(max_length=1000, default='')  # 个人简介
    school_profile = StringField(max_length=1000, default='')  # 学堂简介
    audio_url = StringField(max_length=100, default='')              # 视频的下载地址
    create_time = DateTimeField(default=datetime.now)  # 创建时间

    meta = {
        'ordering': ['-create_time']
    }


# #运输专线
# class SpecialLine(EmbeddedDocument, DataTools):
#     line = StringField(default='')  # 路线



#-------------微信宣传推广
#微信 物流公司
class LogisticsCompany(Document, DataTools):
    company_name = StringField(default='')  # 公司名称
    person = StringField(default='')  # 联系人
    person1 = StringField(default='')  # 联系人
    phone = StringField(default='')  # 公司电话
    phone1 = StringField(default='')  # 公司电话
    phone2 = StringField(default='')  # 公司电话
    logistics_image_list = ListField(StringField(max_length=100, default=""), default=[])          # 公司图片,
    description = StringField(max_length=5000, default='')       # 物流公司介绍

    special_line_list = ListField(StringField(default=""), default=[])           # 运输专线

    priority = IntField(default=50)    # 商品优先级，默认为50，建议值为1~100之间

    create_time = DateTimeField(default=datetime.now)  # 创建时间

    meta = {
        'ordering': ['-create_time']
    }


#微信 律师
class CampaignLawyer(Document, DataTools):
    name = StringField(default='')  # 姓名
    icon = StringField(max_length=512, default='')  # 头像链接
    phone = StringField(default='')  # 联系电话
    phone1 = StringField(default='')  # 联系电话
    address = StringField(default='')   # 办公地址

    qualified = StringField(default='')  # 律师资格证书
    practice = StringField(default='')  # 律师执业证号

    description = StringField(max_length=5000, default='')       # 律师介绍
    priority = IntField(default=50)    # 商品优先级，默认为50，建议值为1~100之间

    create_time = DateTimeField(default=datetime.now)  # 创建时间

    meta = {
        'ordering': ['-create_time']
    }
# 路线
class RoadList(EmbeddedDocument):
    start_line = StringField(default='')       #开始路线
    end_line = StringField(default='')           # 保费
    
class Trucker(Document):
        #车辆类型
        Driver_Car_Type= (
                         ('1', '高栏车'),
                          ('2','半封闭货车'),  
                          ('3', '平板车'),
                          ('4','全封闭厢式货车'),
                           ('5', '其他'),
                           ('6', '冷藏车'),
                          )
        Driver_Car_Length = (
                            ('1','4.2米'),
                            ('2', '5.0米'),
                            ('3', '6.2米'),
                            ('4', '6.3米'),
                            ('5', '6.8米'),
                            ('6', '7.2米'),
                            ('7', '7.5米'),
                            ('8', '7.7米'),
                            ('9', '7.8米'),
                            ('10', '8.0米'),
                            ('11', '8.7米'),
                            ('12', '9.6米'),
                            ('13', '12.0米'),
                            ('14', '12.5米'),
                            ('15', '13.0米'),
                            ('16', '13.5米'),
                            ('17', '16.0米'),
                            ('18', '17.5米'),
                            ('19', '其他')
                     )
        user_name = StringField(default='')  # 司机姓名
        user_age = StringField(default='')  #年龄
        user_phone = StringField(default='')  # 联系电话
        user_image = StringField(max_length=100, default="")      # 头像
#         car_type = StringField(default='')  # 车辆类型
        car_type = StringField(max_length=10, choices=Driver_Car_Type)          # 车辆类型
        car_type_other = StringField(default='')  # 车辆类型为其他时，手动输入
#         car_length = StringField(default='')  # 车长
        car_length = StringField(max_length=10, choices=Driver_Car_Length)          # 车长
        car_length_other = StringField(default='')  # 车长为其他时，手动输入
#         car_age = StringField(default='')  # 车龄
        car_num_head = StringField(default='')  # 车号(头)
        car_num_foot = StringField(default='')  # 车号(挂)
        car_ton = StringField(default='')  # 吨位
        description = StringField(max_length=5000, default='')       # 介绍
#         special_line_list = ListField(StringField(default=""), default=[])           # 常走线路
        special_line_list=ListField(EmbeddedDocumentField(RoadList), default=[])              # 常走线路
        priority = IntField(default=50)    # 优先级，默认为50，建议值为1~100之间
        create_time = DateTimeField(default=datetime.now)  # 创建时间
        car_init_date = StringField(default='') # 初始登记时间
        plate_image_list =  ListField(StringField(max_length=100, default=""), default=[])                        # 行驶证照片正页正面
        insurance_image_list = ListField(StringField(max_length=100,default=""),default=[])                         # 保单照片正页正面
        car_image_list = ListField(StringField(max_length=100,default=""),default=[])                         # 车辆照片已弃用
        client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 关联已认证用户
        meta = {
            'ordering': ['-create_time']
        }

#预存统计
class DepositStatistical(Document, DataTools):
    balance = IntField(default=0)                   # 预存余额
    amount = IntField(default=0)            # 操作额度，单位fen
    create_time = DateTimeField(default=datetime.now)   
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)    # 所属人
    meta = {
            'ordering': ['-create_time']
        }
# 商险清单
class TaxList(EmbeddedDocument):
    com_kind = StringField(default='')       #险种
    com_price = IntField(default=0)           # 保费
    com_notice = StringField(default='')       #备注（保额）
# 认证记录，用于提交车辆认证申请
class CarCertificate(Document, DataTools):
    CERTIFICATE_STATE = (
        ('init', '待审核'),
        ('success', '已认证'),
        ('fail', '已驳回'),
    )
    UP_STATE = (
        ('picture', '图片'),
        ('pdf', 'pdf文件'),
        ('web_url', 'web网址'),
    )
    CAR_STATE= (
        ('0', '平台上传'),
        ('1', '车险自动保存'),
    )
#行驶证
    PERMIT_REQUIRED = (
        ("plate_number", "行驶证车牌号"),
        ("plate_expiration_periods", "行驶证校验有效期"),
        ("car_type", "车辆类型"),
        ("holder", "所有人"),
        ("use_property", "使用性质"),
        ("brand_digging", "品牌型号"),
        ("car_number", "车辆识别代码"),
        ("engine_number", "发动机号"),
        ("issue_date", "注册日期"),
        ("people_number", "核载人数"),
        ("load_weight", "核载质量"),
        ("plate_image_left", "行驶证照片正页正面"),
        ("plate_image_leftdown", "行驶证照片正页反面"),
        ("plate_image_right", "行驶证照片附页正面"),
        ("plate_image_rightdown", "行驶证照片附页反面"),
            )
#交强险
    LIABILITY_INSURANCE = (
        ("liability_number", "交强险保单号"),
        ("liability_tax", "交强险车船稅"),
        ("liability_price", "交强险保费"),
        ("liability_company", "交强险承保公司"),
        ("liability_phone_num", "交强险报案电话"),
        ("liability_date_start", "交强险保险期限起始日期"),
        ("liability_date_stop", "交强险保险期限终止日期"),
        ("liability_image", "交强险保单图片"),
            )
#商业保险
    COMMERCIAL_INSURANCE= (
        ("commercial_num", "商业险保单号"),
        ("commercial_tax", "商业险险种"),
        ("commercial_price", "商业险保费"),
        ("commercial_company", "商业险承保公司"),
        ("commercial_phone_num", "商业险报案电话"),
        ("commercial_image", "商业险保单图片"),
        ("commercial_date_start", "商业险保险期限起始日期"),
        ("commercial_date_stop", "商业险保险期限终止日期"),
            )
    #商业险种类
    COMMERCIAL_KIND= (
                      ('', '未选择'),
                      ("third_liability", "第三者责任险"),
                      ("vehicle_damage", "车辆损失险"),
                      ("glass_broken", "玻璃险"),
                      ("driver_insurance", "司机险"),
                      ("passenger_insurance", "乘客险"),
                      ("theft_insurance", "盗抢险"),
                      ("no_pay", "不计免赔险"),
                      ("spontaneous_combustion", "自燃险"),
                      ("scratch_risk", "划痕险"),
                      ("wade_insurance", "涉水险"),
                      ("no_third_liability", "无法找到第三者"),
                      )
#         ("vehicle_damage", "车辆损失险"),
#         ("third_liability", "第三者责任险"),
#         ("theft_insurance", "盗抢险"),
#         ("car_seat_liability", "车上座位责任险"),
#         ("glass_broken", "玻璃单独破碎险"),
#         ("spontaneous_combustion", "自燃险"),
#         ("scratch_risk", "划痕险"),
#         ("no_franchise", "不计免赔率"),
#         ("no_deductible", "不计免赔额"),
#             )

    FAIL_REASON = (
        ('absence', '缺少证件信息'),
        ('breezing', '证件信息不清晰'),
        ('truth', '证件真实性不足'),
        ('equal', '证件信息与提交的认证信息不符'),
        ('timeout', '证件过期'),
        ('false', '证件真实性不足'),
    )

    IDENTIFICATION_TYPE = (
        ('plate', '行驶证'),
        ('liability', '交强险'),
        ('commercial', '商业险'),
    )
    
    CAR_TYPE = (
        ('', '未选择'),
        ('jc', '轿车'),
        ('xxptkc', '小型普通客车'),
        ('zxptkc', '中型普通客车'),
        ('dxptkc', '大型普通客车'),
        ('zxpthc', '重型普通货车'),
        ('zxxshc', '重型箱式货车'),
        ('zxzxhc', '重型自卸货车'),
        ('zxfbhc', '中型封闭货车'),
         ('zxjzxc', '中型集装箱车'),
        ('zxzxhc', '中型自卸货车'),
        ('qxpthc', '轻型普通货车'),
        ('qxxshc', '轻型箱式货车'),
        ('qxzxhc', '轻型自卸货车'),
        ('wxpthc', '微型普通货车'),
        ('wxxshc', '微型箱式货车'),
        ('wxzxhc', '微型自卸货车'),
        ('zxptbgc', '重型普通半挂车'),
        ('zxptbgc', '中型普通半挂车'),
        ('wxptbgc', '微型普通半挂车'),
        ('zxptqgc', '重型普通全挂车'),
        ('zxptqgc', '中型普通全挂车'),
        ('dxzxzyc', '大型专项作业车'),
        ('zxzxzyc', '中型专项作业车'),
        ('xxzxzyc', '小型专项作业车'),
        ('zxbgqyc', '重型半挂牵引车'),
        ('qt', '其他'),
    
                    
    )
     
    USE_PROPERTY = (
        ('', '未选择'),
        ('jtzy', '家庭自用'),
        ('fyykc', '非营业客车'),
        ('yykc', '营业客车'),
        ('fyyhc', '非营业货车'),
        ('yyhc', '营业货车'),
        ('tzc', '特种车'),
        ('mtc', '摩托车'),
    )
    USER_CLASSIFY = (
        ('unit', '单位'),
        ('personal', '个人'),
    )
    
    
    state = StringField(max_length=20, choices=CERTIFICATE_STATE, default='init')          # 认证状态#2017弃用
    car_state = StringField(max_length=20, choices=CAR_STATE, default='0')          # 车辆保存来源
    plate_expiration_periods = DateTimeField()                     #行驶证校验有效期//车辆年检时间//验车时间/2017/12/17修改参数类型
    start_date = StringField(default='')                      #起保年份#2017弃用
 
    # 实名认证信息
    # 人
  #  user = ReferenceField(User, reverse_delete_rule=NULLIFY)     # # 用户，其中User已经具有的属性包括：password, email, first_name, last_name
  #  profile = EmbeddedDocumentField(UserProfile, default=UserProfile)
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 对应的用户
    # 车 行驶证
    plate_number = StringField(max_length=10, default='')            # 车牌号
    plate_image_left =  ListField(StringField(max_length=100, default=""), default=[])                        # 行驶证照片正页反面
#     plate_image_leftdown = StringField(default='')                           # 行驶证照片正页反面
 #   plate_image_right = StringField(default='')                           # 行驶证照片附页正面
#     plate_image_rightdown = StringField(default='')                           # 行驶证照片附页反面
    car_type = StringField(choices=CAR_TYPE)                # 车辆类型#2017与机动车辆保险统一
    holder = StringField()                      # 所有人
    use_property = StringField(choices=USE_PROPERTY)  #使用性质#2017与机动车辆保险统一
    car_number = StringField()             #车辆识别代码
    brand_digging = StringField()               # 品牌型号
    engine_number = StringField()               # 发动机号
    issue_date = DateTimeField()                # 注册日期
    people_number = StringField()                # 核载人数
    load_weight = StringField()                # 核载质量 
    
    #2017/12/14添加行驶证时间部分
    license_expiration_time = DateTimeField()                # 运营证到期时间
    grade_expiration_time = DateTimeField()                # 等级评定到期时间
    twolevel_expiration_time = DateTimeField()                # 二级维护到期时间
    trailer_expiration_time = DateTimeField()                # 挂车车船稅到期时间
    #2018/01/09添加发证日期
    award_date = DateTimeField()                # 发证日期
    
    # 交强险
    liability_number=StringField(default='')              #保单号
    liability_tax=IntField(default=0)              #车船税
    liability_price= IntField(default=0)               #保费
    liability_date_start=DateTimeField()                    #保险期限起始日期
    liability_date_stop=DateTimeField()                    #保险期限终止日期
    liability_company=StringField(default='')          #承保公司#2017弃用
    liability_phone_num=StringField(default='')          #报案电话#2017弃用
    liability_image = StringField(default='')              #交通事故责任险保单图片#2017弃用
    liability_company_new = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)               #承保公司#2017更新
    liability_up_state = StringField(max_length=20, choices=UP_STATE, default='picture')              # 保单类型
    liability_image_list = ListField(StringField(max_length=1000, default=""), default=[])                 # 保单地址

    #商业险
    commercial_num=StringField(default='')             #保单号
   # commercial_tax=StringField(choices=COMMERCIAL_KIND)                #险种
    commercial_tax=ListField(EmbeddedDocumentField(TaxList), default=[])              #险种清单
    commercial_price= IntField(default=0)             #保费
    commercial_date_start=DateTimeField()                    #保险期限
    commercial_date_stop=DateTimeField()                    #保险期限
    commercial_company=StringField(default='')          #承保公司#2017弃用
    commercial_phone_num=StringField(default='')          #报案电话#2017弃用
    commercial_image = StringField(default='')              #商业险保单图片#17/12/14弃用
    commercial_company_new = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)               #承保公司#2017更新
    commercial_up_state = StringField(max_length=20, choices=UP_STATE, default='picture')              # 保单类型
    commercial_image_list = ListField(StringField(max_length=1000, default=""), default=[])                 # 保单地址
    
    #总保费
    total_price =IntField(default=0)             #总保费

 
    #返回油卡金额
    oil_card_price=IntField(default=0)          #返回油卡金额

    create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序
    certificate_time = DateTimeField()  # 认证时间

    # 认证结果
    failed_reason = StringField(choices=FAIL_REASON)                # 认证失败的原因#2017弃用
    failed_fields = ListField(StringField(choices=IDENTIFICATION_TYPE), default=[])            # 认证失败的类型#2017弃用
    note = StringField(max_length=100, default='')                  # 认证结果的备注，将会提供给用户查看认证失败的具体原因#2017弃用
    #2017/12/07添加字段
    insured_classify = StringField(max_length=20, choices=USER_CLASSIFY, default='personal')#被保人身份（单位、个人）
    insured_name = StringField()               # 被保人姓名（单位名称）
    insured_number = StringField(default='')                            #被保人证件号（营业执照或身份证号）
    is_hidden = BooleanField(default=False)             # True表示已经隐藏，False表示没有隐藏可以查看


    meta = { 'ordering': ['-create_time']}

# 保险平台配置
class  ConfigureList(EmbeddedDocument):
    c_key = StringField(default='')       #配置项
    c_value = StringField(default=0)           # 配置项对应的值
    
# 保险平台配置 
class InsurancePlatform(Document, DataTools):
    #i_name = StringField(max_length=60, default='')      #保险公司名称
    company = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)        # 保险公司
    i_config=ListField(EmbeddedDocumentField(ConfigureList), default=[])              #配置项-配置项对应的值
    i_create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序
    
    meta = {
            'ordering': ['-create_time']
    }
    
class AccessTokenApi(Document, DataTools):
    """
    An AccessToken instance represents the actual access token to
    access user's resources, as in :rfc:`5`.

    Fields:

    * :attr:`logistics` 关联物流平台的appId及密钥
    * :attr:`token` Access token
    * :attr:`refresh_token` 用户刷新token
    * :attr:`expires_in` 过期时间
    * :attr:`scope` Allowed scopes
    """
    token = StringField(max_length=255)     
    expires_in =DateTimeField()

    refresh_token = StringField(max_length=255)   
    refresh_token_expires = DateTimeField()
    logistics = ReferenceField(Logistics, reverse_delete_rule=CASCADE)     #appId及密钥
    create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序
    
    meta = {
            'ordering': ['-create_time']
    }

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        if not self.expires_in:
            return True
        import datetime 
        return datetime.datetime.now() >= self.expires_in
    
    def is_resfresh_token_expired(self):
        """
        Check token expiration with timezone awareness
        """
        if not self.refresh_token_expires:
            return True
        import datetime 
        return datetime.datetime.now() >= self.refresh_token_expires

class CargoArea(Document, DataTools):
    name = StringField(max_length=50, default='')                   # 地区名称
    code = StringField(max_length=50, default='')                     # 地区编码
    level = StringField(max_length=50, default='')                       # 地区等级
    parentcode = StringField(max_length=50, default='')          # 上级编码
    create_time = DateTimeField(default=datetime.now)   
    meta = {
            'ordering': ['-create_time']
        }
    

#平台产品维护
class PlatformProducts(Document, DataTools):
    PRODUCT_TYPE = (
        ('car', '运单保险'),
        ('batch', '车次保险'),
        ('ticket', '单票保险'),
        ('wlgsqnwlzrx', '物流公司全年物流责任险'),
        ('dcqnwlzrx', '单车全年物流责任险'),
        ('gzzrx', '雇主责任险'),
        ('jdclbx', '机动车辆保险'),
        ('ywx', '人身险'),
    )
    IS_LINE = (
        ('0', '线下投保'),
        ('1', '在线投保'),
         ('2', '第三方投保')
    )
    name = StringField(max_length=16, default='')               # 产品名称
    product_type = StringField(choices=PRODUCT_TYPE)                # 产品类型
    product_introduce = StringField(default='')  #产品介绍
    product_characteristic = StringField(default='')#产品特点
    product_url = StringField(default='')#产品链接地址
    
    create_time = DateTimeField(default=datetime.now)           # 创建时间，主要用于排序
    priority = IntField(default='')    # 微信公众号中显示的优先级顺序
    isline = StringField(choices=IS_LINE,default='1')                 # 是否在线投保,1为是，0为线下投保
    wx_share_title = StringField(default='')        #微信分享标题
    wx_share_desc = StringField(default='')      #微信分享介绍
    wx_share_pic = StringField(max_length=100, default="")           #微信分享图片
    wx_product_pic = StringField(max_length=100, default="")          #产品介绍展示图片
    meta = {
        'ordering': ['-create_time']
    }



#中介人员
class IntermediaryPeople(Document, DataTools):
    # 基本信息
    user = ReferenceField(User, reverse_delete_rule=CASCADE)  # 用户，其中User已经具有的属性包括：password, email, first_name, last_name
    profile = EmbeddedDocumentField(UserProfile, default=UserProfile)  # 属性（内嵌文档）
    intermediary = ReferenceField(Intermediary, reverse_delete_rule=CASCADE)         # 保险中介
    name = StringField(max_length=16, default='')                   # 姓名
    create_time = DateTimeField(default=datetime.now)               # 创建时间，主要用于排序

    # 第三方登录
    has_password = BooleanField(default=False)          # 标记是否有密码，如果没有密码则不支持原始登录方式
    wx_id = StringField(max_length=50, default='')      # 微信id，若有则表示该用户已绑定微信帐号。

    meta = {
        'ordering': ['-create_time']
    }



#机动车保险订单
class InquiryInfo(Document, DataTools):
#验证车险订单是否审核通过    
    JDCBX_REQUIRED = (
        #订单信息
        ("paper_id", "订单号"),
        ("client", "使用的账户"),
        #车辆信息
        ("plate_number", "车牌号"),
        ("car_type", "产品类型"),
        ("holder", "所有人"),
        ("use_property", "使用性质"),
        ("brand_digging", "品牌型号"),
        ("car_number", "车辆识别代码"),
        ("engine_number", "发动机号"),
        ("issue_date", "注册日期"),
        #投保人、被保人信息
        ("applicant_phone", "投保人手机号"),
        ("insured_name", "被保人姓名"),
        ("insured_phone", "被保人手机号"),
        ("policy_address", "保单快递地址"),
        #险种
        ("liability_state", "交强险"),
        ("vehicle_vessel_tax_state", "车船使用税"),
        ("third_insurance", "三者险"),
        ("damage_insurance", "车损险"),
        ("glass_insurance", "玻璃险"),
        ("driver_insurance", "司机险"),
        ("passenger_insurance", "乘客险"),
        ("theft_insurance", "盗抢险"),
        ("iop_insurance", "不计免赔"),
        ("autoignition_insurance", "自燃损失险"),
        ("wading_insurance", "涉水险"),
        ("scratch_insurance", "划痕险"),
        ("user_classify", "投保人身份（单位或个人）"),
        
    )

    ORDER_TYPE = (
        ('verify', '审核中'),
        ('price', '询价中'),
        ('wait', '未确认'),
        ('init', '待支付'),
        ('paid', '已支付'),
        ('done', '已完成'),
        ('fail', '已驳回'),
    )
    CAR_TYPE = (
        ('', '未选择'),
        ('jc', '轿车'),
        ('xxptkc', '小型普通客车'),
        ('zxptkc', '中型普通客车'),
        ('dxptkc', '大型普通客车'),
        ('zxpthc', '重型普通货车'),
        ('zxxshc', '重型箱式货车'),
        ('zxzxhc', '重型自卸货车'),
        ('zxfbhc', '中型封闭货车'),
         ('zxjzxc', '中型集装箱车'),
        ('zxzxhc', '中型自卸货车'),
        ('qxpthc', '轻型普通货车'),
        ('qxxshc', '轻型箱式货车'),
        ('qxzxhc', '轻型自卸货车'),
        ('wxpthc', '微型普通货车'),
        ('wxxshc', '微型箱式货车'),
        ('wxzxhc', '微型自卸货车'),
        ('zxptbgc', '重型普通半挂车'),
        ('zxptbgc', '中型普通半挂车'),
        ('wxptbgc', '微型普通半挂车'),
        ('zxptqgc', '重型普通全挂车'),
        ('zxptqgc', '中型普通全挂车'),
        ('dxzxzyc', '大型专项作业车'),
        ('zxzxzyc', '中型专项作业车'),
        ('xxzxzyc', '小型专项作业车'),
        ('qt', '其他'),
    
                    
    )
     
    USE_PROPERTY = (
        ('', '未选择'),
        ('jtzy', '家庭自用'),
        ('fyykc', '非营业客车'),
        ('yykc', '营业客车'),
        ('fyyhc', '非营业货车'),
        ('yyhc', '营业货车'),
        ('tzc', '特种车'),
        ('mtc', '摩托车'),
    )
     
#     CHOICE_STATE = (
#         ('true', '已选'),
#         ('false', '不选'),
#     )
    ORDER_CAR_TYPE = (
        ('passenger_car', '九座以下客车'),
        ('truck', '货车'),
    )
    USER_CLASSIFY = (
        ('unit', '单位'),
        ('personal', '个人'),
    )
    
    UP_STATE = (
        ('picture', '图片'),
        ('pdf', 'pdf文件'),
        ('web_url', 'web网址'),
    )
    
    INSURANCE_FIELD_TUPLE = (
        ('paper_id', '订单号'),
        ('state', '订单状态'),
        ('plate_number', '车牌号'),
        ('record_clerk', '录单员信息'),
        ('car_type', '车辆类型'),
        ('issue_date', '注册日期'),
        ('load_weight', '核载质量'),
        ('liability_id', '交强险保单号'),
        ('liability_price', '交强险保费'),
        ('liability_expectStartTime', '交强险起期'),
        ('liability_expectEndTime', '交强险到期时间'),
#         ('liability_image_list', '交强险保单地址'),
        ('commercial_id', '商业险保单号'),
        ('commercial_price', '商业险保费'),
        ('commercial_expectStartTime', '商业险起期'),
        ('commercial_expectEndTime', '商业险到期时间'),
        ('vehicle_vessel_price', '车船稅保费'),
#         ('commercial_image_list', '商业险保单地址'),
        ('client', '使用的账户'),
#         ('applicant_name', '投保人人姓名'),
#         ('insured_name', '被保险人姓名'),
        ('company', '保险公司'),
        ('insurance_intermediary', '中介'),
        ('quoted_profit_point', '报价时利润点'),
#         ('plate_image_left', '行驶证照片正页'),
#         ('plate_image_right', '行驶证照片附页'),
#         ('business_license_image', '投保人营业执照照片'),
#         ('insured_license_image', '被保人营业执照照片'),
#         ('id_card_up', '投保人身份证照片正面'),
#         ('id_card_down', '投保人身份证照片背面'),
#         ('insured_card_up', '被保人身份证照片正面'),
#         ('insured_card_down', '保人身份证照片背面'),
        ('applicant_phone', '投保人手机号'),
        ('insured_phone', '被保人手机号'),
        ('policy_address', '保单快递地址'),
        ('referee_people', '推荐人信息'),
         ('price', '应缴纳保费'),
        ('intermediary_price', '付给保险中介金额'),
        ('pay_price', '实付保费'),
        ('profit', '利润'),
        ('create_time', '创建订单时间'),
        ('pay_time', '付款时间'),
        
    )
    
    #订单信息
    paper_id = StringField(max_length=50, default='')           # 订单号
    liability_id = StringField(default='')                # 交强险保单号
    liability_image_list = ListField(StringField(max_length=100, default=""), default=[])          # 交强险电子保单图片地址列表,
    commercial_id = StringField(default='')                # 商业险保单号
    commercial_image_list = ListField(StringField(max_length=100, default=""), default=[])          # 商业险电子保单图片地址列表,
    old_commercial_image_list = ListField(StringField(max_length=100, default=""), default=[])          # 上一年商业险电子保单图片地址列表,
     
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 使用的账户
    state = StringField(choices=ORDER_TYPE, default='verify')            # 订单状态
    company = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)         # 确认投保的保险公司
    insurance_intermediary = ReferenceField(Intermediary, reverse_delete_rule=CASCADE)     # 报价的中介
    price = IntField(default=0)                             # 应缴纳保费   保费金额，即需要用户缴纳的保险费用的金额，单位为分
    intermediary_price = IntField(default=0)           # 应付给保险中介金额
    pay_price = IntField(default=0)                         # 实付保费金额，即用户实际缴纳的保险费用，单位为分
     
    #车辆信息
    plate_image_left =  StringField(max_length=100, default="")                        # 行驶证照片正页
    plate_image_right =  StringField(max_length=100, default="")                     # 行驶证照片附页
    #11/29添加字段
    city=  ReferenceField(CargoArea, reverse_delete_rule=CASCADE)                      # 所属城市
    order_car_type = StringField(choices=ORDER_CAR_TYPE)                # 订单产品类型（分为货车和9人以下客车）
     
    plate_number = StringField(max_length=10, default='')            # 车牌号
    car_type = StringField(choices=CAR_TYPE)                # 产品类型
    holder = StringField()                      # 所有人
    use_property = StringField(choices=USE_PROPERTY)  #使用性质
    brand_digging = StringField()               # 品牌型号
    car_number = StringField()             #车辆识别代码
    engine_number = StringField()               # 发动机号
    issue_date = DateTimeField()                # 注册日期
    #approved_load = StringField()               # 核定载重
    people_number = StringField()                # 核载人数
    load_weight = StringField()                # 核载质量 
     
    #投保人、被保人信息
    user_classify = StringField(max_length=20, choices=USER_CLASSIFY, default='personal')#投保人身份（单位、个人）
    insured_classify = StringField(max_length=20, choices=USER_CLASSIFY, default='personal')#被保人身份（单位、个人）
    #单位
    business_license_image = StringField(default='')        # 投保人营业执照照片
    insured_license_image = StringField(default='')        # 被保人营业执照照片
    applicant_company_name = StringField(default='')                            #投保人单位名称
    organ = StringField(max_length=20, default='')                   # 组织机构代码或营业执照号码
    #个人
    id_card_up =  StringField(max_length=100, default="")                        # 投保人身份证照片正面
    id_card_down =  StringField(max_length=100, default="")                     # 投保人身份证照片背面
    insured_card_up =  StringField(max_length=100, default="")                        # 被保人身份证照片正面
    insured_card_down =  StringField(max_length=100, default="")                     # 被保人身份证照片背面
    applicant_name = StringField(default='')                            #投保人姓名
    certificate_number = StringField(default='')                            #投保人身份证号码
    #公共
    applicant_phone = StringField()               # 投保人手机号
    insured_name = StringField()               # 被保人姓名（单位名称）
    insured_number = StringField(default='')                            #被保人证件号（营业执照或身份证号）
    insured_phone = StringField()               # 被保人手机号
    policy_address = StringField(max_length=100,  default='')               # 保单快递地址
    #2017添加字段
    mail_address = StringField(max_length=20,  default='')               # 保单快递地址（省市区）
     
    #险种
    liability_state = BooleanField(default=True)    #交强险（False不投保，True 投保）
    vehicle_vessel_tax_state = BooleanField(default=True)    #车船使用税（False不投保，True 投保）
    #商业险内容（与车车保持一致）
    third_insurance = IntField(default=0)               # 三者险（价值,即保险中承诺的最大赔付金额，单位为分）
    damage_insurance = BooleanField(default=False) #车损险（False不投保）
    glass_insurance = StringField(max_length=20,  default='')  #玻璃险：no 不投保；china 国产；import 进口。
    driver_insurance = IntField(default=0)               # 司机险
    passenger_insurance = IntField(default=0)       # 乘客险
    theft_insurance = BooleanField(default=False)       # 盗抢险（False不投保）
    iop_insurance  = BooleanField(default=False) #不计免赔（False不投保）
    autoignition_insurance = BooleanField(default=False) #自燃损失险（False不投保）
    wading_insurance = BooleanField(default=False) #涉水险（False不投保）
    scratch_insurance = IntField(default=0)  #划痕险
 
#     number_people = StringField()       # 人数
    
    #保险起期
    liability_expectStartTime = DateTimeField() #交强险保险起期
    commercial_expectStartTime = DateTimeField() #商业保险保险起期
    # 平台控制项
    create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序
    pay_time = DateTimeField()  #付款时间
    hidden = BooleanField(default=True)             # 用于控制保单是否显示在用户界面  True显示，False 隐藏
    is_compensate = BooleanField(default=False)             # 已理赔，用于分类显示保单，冗余数据，在发起理赔时自动改写
    #2017/1/9添加可询价保险中介字段
    intermediary_list = ListField(ReferenceField(Intermediary,reverse_delete_rule=PULL), default=[])        # 包含创建订单时可报价的保险中介列表
    #2017添加驳回原因
    fail_reason = StringField(default='')                # 驳回原因
    #添加保单上传状态
    liability_up_state = StringField(max_length=20, choices=UP_STATE, default='picture')               # 交强险上传状态
    commercial_up_state = StringField(max_length=20, choices=UP_STATE, default='picture')              # 商业险上传状态
    #添加特别约定部分
    special_agreement = StringField(max_length=150,  default='')               # 特别约定
    meta = {
        'ordering': ['-create_time']
    }

    
        # 生成订单号
    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None,  cascade=None, cascade_kwargs=None,
             _refs=None, **kwargs):
        # 自动订单号编号
        if not self.paper_id:
            self.product_paper()
        return Document.save(self,  force_insert=force_insert, validate=validate, clean=clean,
                             write_concern=write_concern,  cascade=cascade, cascade_kwargs=cascade_kwargs,
                             _refs=_refs, **kwargs)
     
     
     
    def product_paper(self):
        date_time = datetime.now().strftime("%Y%m%d")[2:]
        need_paper_id = True
        paper_id = ""
        count = 0
        order_set = InquiryInfo.objects()
        while count < 100 and need_paper_id:
            random_number = FormatTools.get_random_product_paper_id().zfill(6)
            paper_id = date_time+random_number
            if order_set.filter(paper_id=paper_id).count() > 0:
                count += 1
            else:
                need_paper_id = False
        if need_paper_id:
            exception = DException(trackback="tools_document DocumentTools get_paper_id line 190 count > 50")
            exception.exception = 'too many paper id'
            exception.type = "生成订单号失败"
            exception.save()
        else:
            self.paper_id = paper_id
            
            
    def pay_money(self):
#         if self.client.balance >= self.price:
            self.state = 'paid'
            self.pay_price = self.price
            self.pay_time = datetime.now()
#             self.client.balance -= self.price
#             self.client.save()
            
 #验证是否通过审核     
    def verify(self):
        fields = InquiryInfo.JDCBX_REQUIRED
        a= 'success'
        for field, name in fields:
            b=field
            c=getattr(self, field)
            if not getattr(self, field) and getattr(self, field) != False:    #
                a="fail"
                raise ValidationError("{0}不能为空".format(name))
        return a
#         if a== 0:
#             self.state = "price"
#             self.save()


     
# #中介人员
# class IntermediaryPeople(Document, DataTools):
#     # 基本信息
#     user = ReferenceField(User, reverse_delete_rule=CASCADE)  # 用户，其中User已经具有的属性包括：password, email, first_name, last_name
#     profile = EmbeddedDocumentField(UserProfile, default=UserProfile)  # 属性（内嵌文档）
#     intermediary = ReferenceField(Intermediary, reverse_delete_rule=CASCADE)         # 保险中介
#     name = StringField(max_length=16, default='')                   # 姓名
#     create_time = DateTimeField(default=datetime.now)               # 创建时间，主要用于排序
# 
#     # 第三方登录
#     has_password = BooleanField(default=False)          # 标记是否有密码，如果没有密码则不支持原始登录方式
#     wx_id = StringField(max_length=50, default='')      # 微信id，若有则表示该用户已绑定微信帐号。
# 
#     meta = {
#         'ordering': ['-create_time']
#     }

    #中介公司和手续费比例关联表
class JdclbxHistory(Document, DataTools):
     #订单信息
    ORDER_DETAIL = (
        ('state', '订单状态'),
        #行驶证部分
        ('plate_image_left', '行驶证照片正页'),
        ('plate_image_right', '行驶证照片附页'),
        ('plate_number', '车牌号'),
        ('car_type', '产品类型'),
        ('holder', ' 所有人'),
        ('use_property', '使用性质'),
        ('brand_digging', '品牌型号'),
        ('car_number', '车辆识别代码'),
        ('engine_number', '发动机号'),
        ('issue_date', '注册日期'),
        ('people_number', '核载人数'),
        ('load_weight', '核载质量 '),
        #投保人部分
        ('user_classify', '投保人身份'),
        ('insured_classify', '被保人身份'),
        ('business_license_image', '投保人营业执照照片'),
        ('insured_license_image', '被保人营业执照照片'),
        ('applicant_company_name', '投保人单位名称'),
        ('organ', '组织机构代码或营业执照号码'),
        ('id_card_up', '投保人身份证照片正面'),
        ('id_card_down', '投保人身份证照片背面'),
        ('insured_card_up', '被保人身份证照片正面'),
        ('insured_card_down', '被保人身份证照片背面'),
         ('applicant_name', '投保人姓名'),
        ('certificate_number', '投保人身份证号码'),
        ('applicant_phone', '投保人手机号'),
        ('insured_name', '被保人姓名（单位名称）'),
        ('insured_number', '被保人证件号（营业执照或身份证号）'),
        ('insured_phone', '被保人手机号'),
        ('policy_address', '保单快递地址'),
        ('mail_address', '保单快递地址（省市区）'),
        
    )
    state = StringField(choices=InquiryInfo.ORDER_TYPE, default='verify')            # 订单状态  
    order = ReferenceField(InquiryInfo, reverse_delete_rule=CASCADE)    # 确认投保的订单
     
    #车辆信息
    plate_image_left =  StringField(max_length=100, default="")                        # 行驶证照片正页
    plate_image_right =  StringField(max_length=100, default="")                     # 行驶证照片附页
     
    plate_number = StringField(max_length=10, default='')            # 车牌号
    car_type = StringField(choices=InquiryInfo.CAR_TYPE)                # 车辆类型
    holder = StringField()                      # 所有人
    use_property = StringField(choices=InquiryInfo.USE_PROPERTY)  #使用性质
    brand_digging = StringField()               # 品牌型号
    car_number = StringField()             #车辆识别代码
    engine_number = StringField()               # 发动机号
    issue_date = DateTimeField()                # 注册日期
    people_number = StringField()                # 核载人数
    load_weight = StringField()                # 核载质量 
     
    #投保人、被保人信息
    user_classify = StringField(max_length=20, choices=InquiryInfo.USER_CLASSIFY, default='personal')#投保人身份（单位、个人）
    insured_classify = StringField(max_length=20, choices=InquiryInfo.USER_CLASSIFY, default='personal')#被保人身份（单位、个人）
    #单位
    business_license_image = StringField(default='')        # 投保人营业执照照片
    insured_license_image = StringField(default='')        # 被保人营业执照照片
    applicant_company_name = StringField(default='')                            #投保人单位名称
    organ = StringField(max_length=20, default='')                   # 组织机构代码或营业执照号码
    #个人
    id_card_up =  StringField(max_length=100, default="")                        # 投保人身份证照片正面
    id_card_down =  StringField(max_length=100, default="")                     # 投保人身份证照片背面
    insured_card_up =  StringField(max_length=100, default="")                        # 被保人身份证照片正面
    insured_card_down =  StringField(max_length=100, default="")                     # 被保人身份证照片背面
    applicant_name = StringField(default='')                            #投保人姓名
    certificate_number = StringField(default='')                            #投保人身份证号码
    #公共
    applicant_phone = StringField()               # 投保人手机号
    insured_name = StringField()               # 被保人姓名（单位名称）
    insured_number = StringField(default='')                            #被保人证件号（营业执照或身份证号）
    insured_phone = StringField()               # 被保人手机号
    policy_address = StringField(max_length=100,  default='')               # 保单快递地址
    #2017添加字段
    mail_address = StringField(max_length=20,  default='')               # 保单快递地址（省市区）

    # 平台控制项
    create_time = DateTimeField(default=datetime.now)  # 创建时间，主要用于排序
    #添加特别约定部分
    special_agreement = StringField(max_length=150,  default='')               # 特别约定
    meta = {
        'ordering': ['-create_time']
    }
    
#中介报价
class IntermediaryPrice(Document, DataTools):
    PRICE_TYPE = (
        ('verify', '未确认'),
        ('done', '已完成'),
    )
    # 基本信息
    state = StringField(choices=PRICE_TYPE, default='verify')            # 报价状态
   # intermediary_people = ReferenceField(IntermediaryPeople, reverse_delete_rule=CASCADE)         # 保险中介人员（弃用）
    insurance_intermediary = ReferenceField(Intermediary, reverse_delete_rule=CASCADE)     # 报价的中介
    company = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)         # 确认报价的保险公司
    order = ReferenceField(InquiryInfo, reverse_delete_rule=CASCADE)    # 确认投保的订单
    order_price_all = IntField(default=0)               # 订单总报价(报价即所得，包含手续费)
    order_price_no_process = IntField(default=0)               # 订单不含手续费报价
    order_price_add_profit = IntField(default=0)             
      # 订单给用户查看的数据 = 交强险报价*（1-交强险手续费比例）+ 交强险报价*利润点+车船稅+商业险报价*（1-商业险手续费比例）+ 商业险报价*利润点
    intermediary_profit_point = FloatField(default=0.0)                     # 中介渠道利润点（例如5个利润点，就是5%）2017修改为浮点型可保存8.88%类数据
    
    liability_price = IntField(default=0)               # 交强险报价
    liability_process_price = FloatField(default=0.0)          #交强险手续费,存的%前的数字，如用户输入30%，这里存30.0
    vehicle_vessel_price = IntField(default=0)               # 车船税报价
    vehicle_vessel_process_price = FloatField(default=0.0)          #车船税手续费
    commercial_price = IntField(default=0)               # 商业险报价
    commercial_process_price = FloatField(default=0.0)           #商业险手续费
    #商业险内容（与车车保持一致）
    third_insurance_price = IntField(default=0)               # 三者险（价值,即保险中承诺的最大赔付金额，单位为分）
    damage_insurance_price = IntField(default=0)             #车损险（False不投保）
    glass_insurance_price = IntField(default=0)             #玻璃险：no 不投保；china 国产；import 进口。
    driver_insurance_price = IntField(default=0)               # 司机险
    passenger_insurance_price = IntField(default=0)       # 乘客险
    theft_insurance_price = IntField(default=0)                 # 盗抢险
    iop_insurance_price  = IntField(default=0)          #不计免赔
    autoignition_insurance_price = IntField(default=0)          #自燃损失险
    wading_insurance_price = IntField(default=0)        #涉水险
    scratch_insurance_price = IntField(default=0)       #划痕险

    create_time = DateTimeField(default=datetime.now)               # 创建时间，主要用于排序

    meta = {
        'ordering': ['-create_time']
    }
    
    #中介公司和手续费比例关联表
class IntermediaryRate(Document, DataTools):
    # 基本信息
    intermediary = ReferenceField(Intermediary, reverse_delete_rule=CASCADE)         # 保险中介
    company = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)        # 保险公司
    liability_process_price = FloatField(default=0.0)          #交强险手续费,存的%前的数字，如用户输入30%，这里存30.0
    commercial_process_price = FloatField(default=0.0)           #商业险手续费
    create_time = DateTimeField(default=datetime.now)               # 创建时间，主要用于排序
    #2017添加字段
    jdclbx_order=ReferenceField(InquiryInfo, reverse_delete_rule=CASCADE)        # 保险订单
    company_state  = BooleanField(default=True)             # 用于控制本公司是否承保  True承保，False 不承保
    state  = BooleanField(default=True)             # 用于控制保单中介手续费比例是否可修改  True修改，False 不可修改
    
    #2017/2/15添加字段
    intermediary_state  = BooleanField(default=True)             # 用于控制本中介是否承保  True承保，False 不承保

    meta = {
        'ordering': ['-create_time']
    }

#2017支付统计
class PaymentStatistical(Document, DataTools):
    PRICE_TYPE = (
        ('', '无'),      
        ('wx_price', '微信支付'),
        ('ht_price', '后台支付'),
        ('xx_price', '线下支付'),
    )
    ORDER_TYPE = (
        ('', '无'),   
        ('car', '运单保险'),
        ('batch', '车次保险'),
        ('ticket', '单票保险'),
        ('wlgsqnwlzrx', '物流公司全年物流责任险'),
        ('dcqnwlzrx', '单车全年物流责任险'),
        ('gzzrx', '雇主责任险'),
        ('jdclbx', '机动车辆保险'),
        ('ywx', '人身险'),
    )
     
    INSURANCE_FIELD_TUPLE1 = (
        ('client', '用户手机号'),
        ('order_type', '订单类型'),
        ('order', '订单号'),
        ('jdclbx_order', '机动车保险订单号'),
        ('state', '支付方式'),
        ('create_time', '支付时间'),
    )
     
    price = IntField(default=0)                   # 支付金额
    order_type = StringField(choices=ORDER_TYPE, default='')            # 订单类型
    order = ReferenceField(Ordering, reverse_delete_rule=CASCADE)           # 关联订单
    order_no = StringField(max_length=32, default='')           # 订单号
    jdclbx_order = ReferenceField(InquiryInfo, reverse_delete_rule=CASCADE)           # 关联订单
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)    # 所属人
    create_time = DateTimeField(default=datetime.now)   
    state = StringField(choices=PRICE_TYPE, default='')            # 支付方式
    meta = {
            'ordering': ['-create_time']
        }

#2017/11/24保险管家添加数据库
# 其他清单
class OtherList(EmbeddedDocument):
    field_name = StringField(max_length=50, default='')           # 字段名称
    field_content = StringField(default='')           # 字段内容
    
# 员工名单（手工录入）
class RosterList(EmbeddedDocument):
    work_type = StringField(max_length=50, default='')           # 工种
    name = StringField(max_length=50, default='')           # 姓名
    id_number = StringField(default='')           # 身份证
#2017/11/24添加员工保险
class EmployeeInsurance(Document, DataTools):
    INSURANCE_TYPE = (
        ('', '无'),      
        ('gzzrx', '雇主责任险'),
        ('ywx', '意外险'),
    )
    UP_ROSTER= (
        ('picture', '图片'),
        ('pdf', 'pdf文件'),
        ('manual', '手工录入'),
    )
    UP_STATE = (
        ('picture', '图片'),
        ('pdf', 'pdf文件'),
        ('web_url', 'web网址'),
    )
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 保单用户 
    paper_id = StringField(max_length =100, default='')            # 保单号：录入
    company = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)        # 承保公司（保险分公司）
    insurance_type = StringField(choices=INSURANCE_TYPE, default='')                # 险种：（雇主责任险和意外险）
    death_disability_price = StringField(max_length =100, default='')                # 死亡伤残保险金额
    medical_price = StringField(max_length =100, default='')                # 医疗费保险金额
    loss_working_price = StringField(max_length =100, default='')                # 误工费保险金额
    hospitalization_price = StringField(max_length =100, default='')                # 住院津贴保险金额
    deductible = StringField(max_length =100, default='')                # 免赔
    up_state = StringField(max_length=20, choices=UP_STATE, default='picture')              # 保单类型
    insurance_image_list = ListField(StringField(max_length=1000, default=""), default=[])                 # 保单地址
    other_list = ListField(EmbeddedDocumentField(OtherList), default=[])           # 其他字段（内勤自由录入）
    date_start=DateTimeField()                    #保险起始日期
    date_stop=DateTimeField()                    #保险终止日期
    up_roster = StringField(max_length=20, choices=UP_ROSTER, default='manual')              # 员工保险中添加员工名单类型
    roster_list = ListField(StringField(max_length=1000, default=""), default=[])                 # 员工名单地址
    roster_list_manual = ListField(EmbeddedDocumentField(RosterList), default=[])           # 员工名单地址（内勤自由录入）
    is_hidden = BooleanField(default=False)             # True表示已经隐藏，False表示没有隐藏可以查看
    create_time = DateTimeField(default=datetime.now)   
    meta = {
            'ordering': ['-create_time']
        }
    
    #2017/12/2添加货运年险
class ＦreightInsurance(Document, DataTools):
    INSURANCE_TYPE = (
        ('', '无'),      
        ('wlzrx', '物流责任险'),
        ('hyx', '货运险预约协议'),
        ('cyr', '承运人责任险'),
    )
    UP_STATE = (
        ('picture', '图片'),
        ('pdf', 'pdf文件'),
        ('web_url', 'web网址'),
    )
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 保单用户 
    paper_id = StringField(max_length =100, default='')            # 保单号：录入
    company = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)        # 承保公司（保险分公司）
    insurance_type = StringField(choices=INSURANCE_TYPE, default='')                # 险种：（物流责任险和货运险预约协议和承运人责任险）
    single_vehicle_price = StringField(max_length =100, default='')                # 单车保险金额
    insurance_price = StringField(max_length =100, default='')                # 保费
    deductible = StringField(max_length =100, default='')                # 免赔
    up_state = StringField(max_length=20, choices=UP_STATE, default='picture')              # 保单类型
    insurance_image_list = ListField(StringField(max_length=1000, default=""), default=[])                 # 保单地址
    other_list = ListField(EmbeddedDocumentField(OtherList), default=[])           # 其他字段（内勤自由录入）
    date_start=DateTimeField()                    #保险起始日期
    date_stop=DateTimeField()                    #保险终止日期
    is_hidden = BooleanField(default=False)             # True表示已经隐藏，False表示没有隐藏可以查看
    create_time = DateTimeField(default=datetime.now)   
    meta = {
            'ordering': ['-create_time']
        }
    
    
    
    #2017/12/5个人保险
class PersonalInsurance(Document, DataTools):
    INSURANCE_TYPE = (
        ('', '无'),      
        ('ywx', '意外险'),
        ('zdjbbx', '重大疾病保险'),
        ('ylbx', '养老保险'),
        ('njbx', '年金保险'),
    )
    UP_STATE = (
        ('picture', '图片'),
        ('pdf', 'pdf文件'),
        ('web_url', 'web网址'),
    )
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 保单用户 
    paper_id = StringField(max_length =100, default='')            # 保单号：录入
    company = ReferenceField(InsuranceCompany, reverse_delete_rule=CASCADE)        # 承保公司（保险分公司）
    insurance_type = StringField(choices=INSURANCE_TYPE, default='')                # 险种：（物流责任险和货运险预约协议和承运人责任险）
    up_state = StringField(max_length=20, choices=UP_STATE, default='picture')              # 保单类型
    insurance_image_list = ListField(StringField(max_length=1000, default=""), default=[])                 # 保单地址
    other_list = ListField(EmbeddedDocumentField(OtherList), default=[])           # 其他字段（内勤自由录入）
    date_start=DateTimeField()                    #保险起始日期
    date_stop=DateTimeField()                    #保险终止日期
    is_hidden = BooleanField(default=False)             # True表示已经隐藏，False表示没有隐藏可以查看
    create_time = DateTimeField(default=datetime.now)   
    meta = {
            'ordering': ['-create_time']
        }
    
    #2017/12/13其他保险
class OtherInsurance(Document, DataTools):
    UP_STATE = (
        ('picture', '图片'),
        ('pdf', 'pdf文件'),
        ('web_url', 'web网址'),
    )
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 保单用户       
    up_state = StringField(max_length=20, choices=UP_STATE, default='picture')              # 保单类型
    insurance_image_list = ListField(StringField(max_length=1000, default=""), default=[])                 # 保单地址
    other_list = ListField(EmbeddedDocumentField(OtherList), default=[])           # 其他字段（内勤自由录入）
    date_start=DateTimeField()                    #保险起始日期
    date_stop=DateTimeField()                    #保险终止日期
    is_hidden = BooleanField(default=False)             # True表示已经隐藏，False表示没有隐藏可以查看
    create_time = DateTimeField(default=datetime.now)   
    meta = {
            'ordering': ['-create_time']
        }

#商品大类
class GoodsType(Document, DataTools):
    name = StringField(max_length=50, default='')                   # 分类名称
    picture = StringField(max_length=1000, default="")                     # 图片分类
    priority = IntField(default=50)    # 优先级，默认为50，建议值为1~100之间                 
    is_hidden = BooleanField(default=False)             # True表示已经隐藏，False表示没有隐藏可以查看
    create_time = DateTimeField(default=datetime.now)   
    meta = {
            'goodstype': ['-create_time']
        }
        
#2017/12/19商城
class MallGoods(Document, DataTools):
    TYPE = (
      #  ('', '无'),   
        ('wait', '待发布'),   
        ('publish', '发布'),
        ('offshelf', '下架'),
        ('done', '已完成'),
    )
    #商品状态
    PRESENT_SITUATION = (
        ('', '无'),   
        ('new', '全新，未拆封'),   
        ('intact', '包装破损，内部全新'),
        ('scratch', '外观轻微划痕/磕碰，功能正常'),
        #('repair', '维修后功能正常'),
        ('other', '其他'),
    )
    CERTIFICATE_TYPE = (
        ('picture', '图片'),
        ('web_url', 'web网址'),
    )
    client = ReferenceField(Client, reverse_delete_rule=CASCADE)         # 用户 
    state = StringField(choices=TYPE,max_length =100, default='wait')            # 本单状态
    
    #商品部分
    goods_name  = StringField(max_length =100, default='')  #商品名称
    goods_count  = StringField(max_length =100, default='')  #商品数量
    goods_brand_digging  = StringField(max_length =100, default='')  #品牌型号（选填）
    original_cost = IntField(default=0 ) #  商品原价
    unit_price    =   IntField(default=0 ) #  商品单价
    goods_present_situation = StringField(choices=PRESENT_SITUATION,max_length =100, default='')            # 商品状态
    other_notes  = StringField(max_length =100, default='') #备注
    goods_describe  = StringField(default='') #商品描述
    contact_people  = StringField(max_length =100, default='') #联系人
    contact_phone  = StringField(max_length =100, default='') #联系方式-手机
    contact_landline  = StringField(max_length =100, default='') #联系方式-座机
    contact_qq  = StringField(max_length =100, default='') #联系方式-QQ
    contact_wx  = StringField(max_length =100, default='') #联系方式-微信
    goods_image_list = ListField(StringField(max_length=1000, default=""), default=[])                 # 商品图片
    certificate_type = StringField(choices=CERTIFICATE_TYPE,max_length =100, default='')            # 证明商品价值地址方式
    certificate_image_list = ListField(StringField(max_length=1000, default=""), default=[])                 # 证明商品价值地址
    mail_address = StringField(max_length=20,  default='')               # 商品所在地址（省市区）
    policy_address = StringField(max_length=100,  default='')               # 商品所在地址
    video = StringField(max_length=1000, default="")                # 视频地址
    
    #商品类别
    goods_type = ReferenceField(GoodsType, reverse_delete_rule=CASCADE)   #商品类别
    
    
    
    is_hidden = BooleanField(default=False)             # True表示已经隐藏，False表示没有隐藏可以查看
    create_time = DateTimeField(default=datetime.now)   
    meta = {
            'mallgoods': ['-create_time']
        }
    
#特推产品
class RecommendProduct(Document, DataTools):
    PRODUCT_TYPE = (
        ('', '未选择'),    
        ('insurance', '保险类'),
        ('loan', '贷款类'),
    )
    name = StringField(default='')  # 名称
    product_type = StringField(choices=PRODUCT_TYPE,max_length =100, default='')            # 产品分类
    phone = StringField(default='')  # 联系电话
    product_image_list = ListField(StringField(max_length=1000, default=""), default=[])                 # 产品图片
    description = StringField(max_length=5000, default='')       # 产品介绍
    
    is_hidden = BooleanField(default=False)             # True表示已经隐藏，False表示没有隐藏可以查看
    create_time = DateTimeField(default=datetime.now)  # 创建时间

    meta = {
        'ordering': ['-create_time']
    } 
    
#广告位置
class AdvertisingPosition(Document, DataTools):
    name = StringField(max_length=50, default='')                   # 广告位名称
    paper_id = IntField(default=0 )                   # 编号
    picture = StringField(max_length=1000, default="")                     # 图片
    note = StringField(max_length=1000, default="")                     # 备注        
    is_hidden = BooleanField(default=False)             # True表示已经隐藏，False表示没有隐藏可以查看
    create_time = DateTimeField(default=datetime.now)   

    meta = {
        'ordering': ['-create_time']
    } 

#广告
class Advertising(Document, DataTools):
    position = ReferenceField(AdvertisingPosition, reverse_delete_rule=CASCADE)         # 广告位置
    name = StringField(max_length=50, default='')                   # 广告名称
    picture = StringField(max_length=1000, default="")                     # 图片
    advertising_url = StringField(max_length=1000, default="")                     # 地址           
    is_hidden = BooleanField(default=False)             # True表示已经隐藏，False表示没有隐藏可以查看
    create_time = DateTimeField(default=datetime.now)   

    meta = {
        'ordering': ['-create_time']
    }    
    
    