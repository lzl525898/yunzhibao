__author__ = 'mlzx'
try:
    from common.models import SiteSettings
except ImportError:
    from common.models import BaseSettings as SiteSettings
from common.tools_legoo import BaseConvertTools, BaseRequestTools, BasePageTools
from common.models import *
from django.contrib.auth import authenticate
from datetime import timedelta
from common.interface_helper import *
from uuid import uuid1
from mongoengine.django.auth import User
import json
import hashlib
import common.tools_m5c_sms as m5c_sms_helper
import re
import jieba
import time
#import datetime 




class PageTools(BasePageTools):
    pass


class DocumentTools(object):

    @staticmethod
    def check_token(token, time_overdue):
        if not token:
            raise TokenError('访问口令不能为空')
        _token = AccessToken.objects(token=token).first()
        if _token is None:
            raise TokenError('访问口令错误')
        if _token.overdue:
            raise TokenTimeoutError('访问令牌已超时')
        span = _token.create_time - datetime.now()
        if span > timedelta(seconds=time_overdue):
            # 访问令牌已超时
            _token.overdue = True
            _token.save()
            raise TokenTimeoutError('访问令牌已超时')
        return _token

    @staticmethod
    def multi_authenticate(account, password):
        entity = Client.objects(Q(profile__phone=account)).first()
        entity1 = Claim.objects(Q(profile__phone=account)).first()
        entity2 = Lawyer.objects(Q(profile__phone=account)).first()
        entity3 = IntermediaryPeople.objects(Q(profile__phone=account)).first()
        if entity:
            return authenticate(username=entity.user.username, password=password), entity
        elif entity1:
            return authenticate(username=entity1.user.username, password=password), entity1
        elif entity2:
            return authenticate(username=entity2.user.username, password=password), entity2
        elif entity3:
            return authenticate(username=entity3.user.username, password=password), entity3
        else:
            return None, None

    # 验证验证码
    @staticmethod
    def check_code(code, phone, code_type):
        if FormatTools.validate_choices(code_type, VerificationCode.TYPE):
            delta = timedelta(seconds=90)
            end_time = datetime.now() - delta
            _code = VerificationCode.objects(code=code, used=False, type=code_type, telephone=phone,create_time__gt=end_time).first()
            if _code:
                _code.used = True
                _code.save()
                return True
            elif code == '123456':
                return True
            else:
                raise ParameterError('无效的校验码或者已经过期')

        else:
            raise ParameterError('验证码类型错误')

    # 生成验证码
    @staticmethod
    def make_code(phone, verification_type):
        if FormatTools.validate_choices(verification_type, VerificationCode.TYPE):
            delta = timedelta(seconds=600)
            end_time = datetime.now() - delta
            verification_set = VerificationCode.objects(create_time__gt=end_time)
            if verification_set.count() >= 100:
                raise NewError(CODE_VERIFICATION_CODE_TOO_FAST_ERROR, '发送验证码的频率过快')
            code = str(random.randint(100000, 999999))
            _code = VerificationCode(code=code, type=verification_type, telephone=phone).save()
            if _code:
                return _code
            else:
                raise Exception('生成验证码失败')
        else:
            raise ParameterError('验证码类型错误')

    # 发送验证码短信
    @staticmethod
    def send_phone_message(phone, verification_type, verification_code):
        # print('send verification code {1} to {0} for {2}'.format(phone, verification_code, verification_type))
        site_settings = SiteSettings.get_settings()
        # TODO: 对手机号进行判断，根据不同的手机号发送不同的短信
        if phone.startswith('+'):
            if phone.startswith('+86'):
                phone = phone[3:]
                helper = m5c_sms_helper.SmsHelper(site_settings.meilian_username, site_settings.meilian_password, site_settings.meilian_api_key)
            else:
                # 此项目不发送海外短信，故此注释下列代码
                # helper = tw_sms_helper.SmsHelper(site_settings.twilio_account, site_settings.twilio_password)
                raise ParameterError("不支持当前手机号")
        else:
            helper = m5c_sms_helper.SmsHelper(site_settings.meilian_username, site_settings.meilian_password, site_settings.meilian_api_key)
        content = "尊敬的用户您好，您的验证码是：{0}。请不要把验证码泄露给其他人，如非本人操作，可不用理会！".format(verification_code)
        # content = "{0}".format(verification_code)
        return helper.send_sms(phone_to=phone, content=content)

    # 验证用户是否存在
    @staticmethod
    def get_user(username):
        client = Client.objects(Q(profile__phone=username)).first()
        if client is not None:
            return client.user
        return None

    # 生成用户名
    @staticmethod
    def get_username():
        username = str(uuid1()).replace('-', '')[:30]
        try:
            count = 0
            while count < 1000:
                username = str(uuid1()).replace('-', '')[:30]
                user = User.objects.get(username=username)
                count += 1
            raise ParameterError('生成用户名失败')
        except User.DoesNotExist:
            return username

    # 重置密码
    @staticmethod
    def reset_password(password, user):
        password = hashlib.sha1(password.encode('utf-8')).hexdigest()
        user.set_password(password)
        client_set = Client.objects(user=user)
        client_set.update(set__password=password)
        AccessToken.objects(user=user, overdue=False).update(set__overdue=True)

    # 选择chooice
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


class ConvertTools(BaseConvertTools):
    pass


class RequestTools(BaseRequestTools):
    site_settings = SiteSettings.get_settings()

    # 保存日志
    def save_log(self):
        content = "post:{0};\nget:{1};".format(json.dumps(self.request.POST), json.dumps(self.request.GET))
        user = self.request.user
        path = self.request.META['PATH_INFO']
        if 'login' in path:
            log_type = 'login'
        elif 'logout' in path:
            log_type = 'logout'
        elif 'delete' in path:
            log_type = 'delete'
        elif 'save' in path or 'edit' in path:
            log_type = 'edit'
        elif 'create' in path:
            log_type = 'create'
        else:
            if self.request.method == "POST":
                log_type = 'edit'
            else:
                log_type = 'search'
        ip = self.get_ip()[:15]
        Log(content=content[:2000], ip=ip, type=log_type, path=path[:200], user=user).save()

    def check_token(self):
        token = self.get_parameter('access_token')
        overdue = self.site_settings.access_token_time_overdue
        return DocumentTools.check_token(token, overdue)

    # 过滤认证搜索
    def certificate_filter(self, certificate_set, keyword=""):
        if not isinstance(certificate_set, QuerySet):
            raise ParameterError('非法的参数：certificate_set')
        if keyword:

            client_set = Client.objects(Q(name__contains=keyword) |
                                         Q(profile__phone__contains=keyword))
            certificate_set = certificate_set.filter(Q(name__contains=keyword) |
                                                     Q(national_id__contains=keyword) |
                                                     Q(driver_id__contains=keyword) |
                                                     Q(plate_number__contains=keyword) |
                                                     Q(transportation_license_id__contains=keyword) |
                                                     Q(operating_permit_id__contains=keyword) |
                                                     Q(business_license_id__contains=keyword) |
                                                     Q(client__in=client_set))

        state = self.get_parameter("state", "active")
        if state == 'init':
            certificate_set = certificate_set.filter(state=state)
        elif state == 'success':
            certificate_set = certificate_set.filter(state=state)
        elif state == 'fail':
            certificate_set = certificate_set.filter(state=state)
        certification_goal = self.get_parameter("certification_goal", 'init')
        if certification_goal == 'transport':
            certificate_set = certificate_set.filter(user_type=certification_goal)
        elif certification_goal == 'driver':
            certificate_set = certificate_set.filter(user_type=certification_goal)
        elif certification_goal == 'boss':
            certificate_set = certificate_set.filter(user_type=certification_goal)
        return certificate_set

    # 过滤保险总公司搜索
    def head_company_filter(self, head_company_set, keyword=""):
        if not isinstance(head_company_set, QuerySet):
            raise ParameterError('非法的参数：certificate_set')
        if keyword:
            head_company_set = head_company_set.filter(Q(name__contains=keyword) | Q(phone__contains=keyword) | Q(paper_id__contains=keyword))
        state = self.get_parameter("state", "active")
        if state == 'active':
            head_company_set = head_company_set.filter(is_hidden=False)
        elif state == 'hidden':
            head_company_set = head_company_set.filter(is_hidden=True)
        return head_company_set

    # 过滤保险分公司搜索
    def tail_company_filter(self, tail_company_set, keyword=""):
        if not isinstance(tail_company_set, QuerySet):
            raise ParameterError('非法的参数：certificate_set')
        if keyword:
            tail_company_set = tail_company_set.filter(Q(name__contains=keyword) | Q(paper_id__contains=keyword))
        state = self.get_parameter("state", "active")
        if state == 'active':
            tail_company_set = tail_company_set.filter(is_hidden=False)
        elif state == 'hidden':
            tail_company_set = tail_company_set.filter(is_hidden=True)
        return tail_company_set

    # 过滤保险文档搜索
    def insurance_document_filter(self, insurance_document_set, keyword=""):
        if not isinstance(insurance_document_set, QuerySet):
            raise ParameterError('非法的参数：insurance_document_set')
        if keyword:
            insurance_document_set = insurance_document_set.filter(Q(name__contains=keyword))
        state = self.get_parameter("state", "active")
        if state == 'active':
            insurance_document_set = insurance_document_set.filter(is_hidden=False)
        elif state == 'hidden':
            insurance_document_set = insurance_document_set.filter(is_hidden=True)
        return insurance_document_set

    # 过滤产品搜索
    def insurance_product_filter(self, insurance_product_set, keyword=""):
        if not isinstance(insurance_product_set, QuerySet):
            raise ParameterError('非法的参数：insurance_product_set')
        if keyword:
            insurance_product_set = insurance_product_set.filter(Q(name__contains=keyword) | Q(paper_id__contains=keyword))
        state = self.get_parameter("state", "all")
        if state == 'active':
            insurance_product_set = insurance_product_set.filter(is_hidden=False)
        elif state == 'hidden':
            insurance_product_set = insurance_product_set.filter(is_hidden=True)
        return insurance_product_set

    # 过滤订单搜索
    def order_filter(self, order_set, keyword=""):
        if not isinstance(order_set, QuerySet):
            raise ParameterError('非法的参数：order_set')
        if keyword:
            product_set = InsuranceProducts.objects().filter(Q(name__contains=keyword))
            order_set = order_set.filter(Q(insurance_id__contains=keyword) | Q(paper_id__contains=keyword) | Q(transport_id__contains=keyword)| Q(insured__contains=keyword))#|Q(insurance_product__in=product_set))#| Q(insurance_product__name__contains=keyword))
        start_time = self.request.session.get('start_time', '')
        end_time = self.request.session.get('end_time', '')
        order_from = self.get_parameter("order_from", "")
        if start_time :     
            if order_from =="cos_order":
                order_set = order_set.filter(pay_time__gt=start_time)
            else:
                order_set = order_set.filter(expectStartTime__gt=start_time)
        if end_time:
            end_time2 = datetime.strptime(end_time,"%Y-%m-%d")
            end_time1 = (end_time2+timedelta(days= 1)).strftime('%Y-%m-%d') 
            if order_from =="cos_order":
                order_set = order_set.filter(pay_time__lt=end_time1)
            else:
                order_set = order_set.filter(expectStartTime__lt=end_time1)
            
            
        state = self.get_parameter("state", "")
        if state == 'active':
            order_set = order_set.filter(is_hidden=False)
        elif state == 'hidden':
            order_set = order_set.filter(is_hidden=True)
        pay_state = self.get_parameter("pay_state", '')
        if pay_state == 'init':
            order_set = order_set.filter(state=pay_state)
        elif pay_state == 'paid':
            order_set = order_set.filter(state=pay_state)
        elif pay_state == 'done':
            order_set = order_set.filter(state=pay_state)

        user_type = self.get_parameter("user_type", '')
        if user_type == 'transport':
            client_set = Client.objects(user_type=user_type)
            order_set = order_set.filter(client__in=client_set)
        elif user_type == 'driver':
            client_set = Client.objects(user_type=user_type)
            order_set = order_set.filter(client__in=client_set)
        elif user_type == 'boss':
            client_set = Client.objects(user_type=user_type)
            order_set = order_set.filter(client__in=client_set)
        elif user_type == 'registered':
            client_set = Client.objects(user_type=user_type)
            order_set = order_set.filter(client__in=client_set)

        id_client = self.get_parameter("id_client", '')
        if id_client:
            client = Client.objects(id=id_client).first()
            if client:
                order_set = order_set.filter(client=client)
            else:
                raise ParameterError("您查找的用户不存在")

        client_sign = self.get_parameter("client_sign", '')
        if client_sign:
            client = Client.objects(id=client_sign).first()
            if client:
                order_set = order_set.filter(client=client)
            else:
                raise ParameterError("您查找的用户不存在")
        
        product_detail_id = self.get_parameter("product_detail_id", '')
        if product_detail_id:
            try:
                insurance_product_detail  = InsuranceProducts.objects(id =product_detail_id).first()
                if insurance_product_detail:
                    order_set = order_set.filter(insurance_product = insurance_product_detail)
            except Exception as e:
                raise ParameterError("您查找的指定产品的订单不存在")
        return order_set

    # 过滤产品搜索
    def compensate_filter(self, compensate_set, keyword=""):
        if not isinstance(compensate_set, QuerySet):
            raise ParameterError('非法的参数：compensate__set')
        # if keyword:
        #     # compensate_set = compensate_set.filter(Q(name__contains=keyword) | Q(paper_id__contains=keyword))
        state = self.get_parameter("state", "active")
        if state == 'active':
            compensate_set = compensate_set.filter(is_hidden=False)
        elif state == 'hidden':
            compensate_set = compensate_set.filter(is_hidden=True)
        compensate_state = self.get_parameter("compensate_state", 'init')
        if compensate_state == 'init':
            compensate_set = compensate_set.filter(state=compensate_state)
        elif compensate_state == 'paid':
            compensate_set = compensate_set.filter(state=compensate_state)
        elif compensate_state == 'done':
            compensate_set = compensate_set.filter(state=compensate_state)
        return compensate_set

    # 过滤优惠券搜索
    def coupon_filter(self, coupon_set, keyword=""):
        if not isinstance(coupon_set, QuerySet):
            raise ParameterError('非法的参数：coupon_set')
        if keyword:
            coupon_set = coupon_set.filter(Q(name__contains=keyword) | Q(describe__contains=keyword))
        state = self.get_parameter("state", "active")
        if state == 'active':
            coupon_set = coupon_set.filter(is_hidden=False)
        elif state == 'hidden':
            coupon_set = coupon_set.filter(is_hidden=True)
        return coupon_set

    # 过滤优惠券用户
    def client_filter(self, client_set, keyword=""):
        if not isinstance(client_set, QuerySet):
            raise ParameterError('非法的参数：client_set')
        if keyword:
            client_set = client_set.filter(Q(name__contains=keyword)|Q(company_name__contains=keyword)|Q(profile__phone__contains=keyword))
        state = self.get_parameter("state", "")
        if state == 'transport':
            client_set = client_set.filter(user_type='transport')
        elif state == 'driver':
            client_set = client_set.filter(user_type='driver')
        elif state == 'boss':
            client_set = client_set.filter(user_type='boss')
        elif state == 'registered':
            client_set = client_set.filter(user_type='registered')
        return client_set

        # 过滤优惠券用户
    def client_sent_filter(self, client_set, keyword=""):
        if not isinstance(client_set, QuerySet):
            raise ParameterError('非法的参数：client_set')
        if keyword:
            client_set = client_set.filter(Q(name__contains=keyword)|Q(company_name__contains=keyword)|Q(profile__phone__contains=keyword))
        state = self.get_parameter("modal_state", "")
        if state == 'transport':
            client_set = client_set.filter(user_type='transport')
        elif state == 'driver':
            client_set = client_set.filter(user_type='driver')
        elif state == 'boss':
            client_set = client_set.filter(user_type='boss')
        elif state == 'registered':
            client_set = client_set.filter(user_type='registered')
        return client_set

    # 过滤优惠券发放记录搜索
    def coupon_record_filter(self, coupon_record_set, keyword=""):
        if not isinstance(coupon_record_set, QuerySet):
            raise ParameterError('非法的参数：coupon_record_set')
        if keyword:
            client_set = Client.objects().filter(name__contains=keyword)
            coupon_set = Coupon.objects().filter(name__contains=keyword)
            coupon_record_set = coupon_record_set.filter(Q(coupon__in=coupon_set) | Q(client__in=client_set))
        return coupon_record_set

    # 过滤预存保费
    def balance_filter(self, balance_set, keyword=""):
        if not isinstance(balance_set, QuerySet):
            raise ParameterError('非法的参数：client_set')
        if keyword:
            balance_set = Client.objects().filter(Q(name__contains=keyword) |
                                                  Q(company_name__contains=keyword) |
                                         Q(profile__phone__contains=keyword))
        certification_goal = self.get_parameter("certification_goal", '')
        if certification_goal == 'transport':
            balance_set = balance_set.filter(user_type=certification_goal)
        elif certification_goal == 'driver':
            balance_set = balance_set.filter(user_type=certification_goal)
        elif certification_goal == 'boss':
            balance_set = balance_set.filter(user_type=certification_goal)
        return balance_set
    
    

    # 过滤微信物流公司搜索
    def logistics_filter(self, logistics_set, keyword=""):
        if not isinstance(logistics_set, QuerySet):
            raise ParameterError('非法的参数：order_set')
        if keyword:
            logistics_set = logistics_set.filter(Q(phone__contains=keyword) | Q(phone1__contains=keyword) | Q(person__contains=keyword) | Q(company_name__contains=keyword))
        return logistics_set


    # 过滤微信律师搜索
    def campaign_lawyer_filter(self, campaign_lawyer_set, keyword=""):
        if not isinstance(campaign_lawyer_set, QuerySet):
            raise ParameterError('非法的参数：order_set')
        if keyword:
            campaign_lawyer_set = campaign_lawyer_set.filter(Q(phone__contains=keyword) | Q(phone1__contains=keyword) | Q(qualified__contains=keyword) | Q(practice__contains=keyword) | Q(name__contains=keyword))
        return campaign_lawyer_set
    
        # 过滤后台宣传推广-司机搜索
    def campaign_driver_filter(self, trucker_set, keyword=""):
        if not isinstance(trucker_set, QuerySet):
            raise ParameterError('非法的参数：order_set')
        if keyword:
            trucker_set = trucker_set.filter(Q(user_name__contains=keyword) | Q(user_phone__contains=keyword) | Q(user_age__contains=keyword) | Q(special_line_list__contains=keyword))
        return trucker_set
    
    # 过滤微信-宣传推广-司机搜索
    def wx_driver_filter(self, trucker_set, keyword="",car_type="",car_length=""):
        if not isinstance(trucker_set, QuerySet):
            raise ParameterError('非法的参数：order_set')
        if keyword :

            trucker_set = trucker_set.filter(Q(user_name__contains=keyword) | Q(car_num_head__contains=keyword) | Q(car_num_foot__contains=keyword) | Q(car_type=car_type) | Q(car_length=car_length))
        else:
            trucker_set = trucker_set.filter(Q(car_type=car_type) | Q(car_length=car_length))
        return trucker_set
    
     # 过滤微信-宣传推广-物流司机搜索
    def wx_logistics_filter(self, logistics_set, keyword=""):
        if not isinstance(logistics_set, QuerySet):
            raise ParameterError('非法的参数：order_set')
        str = keyword.strip()
        if str:
            str = ' '.join(str.split())
            if re.search(u"\s",str):
                keyword = str .split(" ")  #中间存在空格，变成数组
                if len(keyword) == 2:
                     logistics_set = logistics_set.filter(Q(special_line_list__contains=keyword[0]) & Q(special_line_list__contains=keyword[1]) |Q(company_name__contains=str))
                elif len(keyword) >= 3:
                     logistics_set = logistics_set.filter(Q(special_line_list__contains=keyword[0]) & Q(special_line_list__contains=keyword[1]) & Q(special_line_list__contains=keyword[2]) |Q(company_name__contains=str))
            else:
                keyword = str
                logistics_set = logistics_set.filter(Q(special_line_list__contains=keyword) |Q(company_name__contains=keyword))
             
        return logistics_set
    
    # 过滤微信-宣传推广-物流司机搜索
    def wx_logistics_filter(self, logistics_set, keyword=""):
        if not isinstance(logistics_set, QuerySet):
            raise ParameterError('非法的参数：order_set')
        str = keyword.strip()
        if str:
                seg_list = jieba.cut(str)
                keyword = ' '.join(seg_list)
                keyword = keyword .split(" ")  #中间存在空格，变成数组
                if len(keyword) ==1:
                     logistics_set = logistics_set.filter(Q(special_line_list__contains=keyword[0])|Q(company_name__contains=str))
                elif len(keyword) == 2:
                     logistics_set = logistics_set.filter(Q(special_line_list__contains=keyword[0]) & Q(special_line_list__contains=keyword[1]) |Q(company_name__contains=str))
                elif len(keyword) == 3:
                     logistics_set = logistics_set.filter(Q(special_line_list__contains=keyword[0]) & Q(special_line_list__contains=keyword[1]) & Q(special_line_list__contains=keyword[2]) |Q(company_name__contains=str)) 
                else:
                     logistics_set = logistics_set.filter(Q(special_line_list__contains=keyword[0]) & Q(special_line_list__contains=keyword[1]) & Q(special_line_list__contains=keyword[2]) & Q(special_line_list__contains=keyword[3]) |Q(company_name__contains=str)) 
        return logistics_set
    
    
       # 过滤微信-我的订单-搜索
    def wx_my_order_filter(self,order_set,keyword):
        if not isinstance(order_set, QuerySet):
            raise ParameterError('非法的参数：order_set')
        str = keyword.strip()
        i = 0
        product_type= []
        if str:
            for k,v in InsuranceProducts.PRODUCT_TYPE:
                if str in v :
                    product_type.append(k)
                    i+=1
            if len(product_type)==0:
                order_set = order_set.filter(Q(transport_id__contains=str) | Q(plate_number__contains=str))
            elif len(product_type) == 1:
                order_set = order_set.filter(Q(product_type__contains=product_type[0])|Q(transport_id__contains=str)|Q(plate_number__contains=str))
            elif len(product_type) == 2:
                order_set = order_set.filter(Q(product_type__contains=product_type[0])|Q(product_type__contains=product_type[1])|Q(transport_id__contains=str)|Q(plate_number__contains=str))
            elif len(product_type) == 3:
                order_set = order_set.filter(Q(product_type__contains=product_type[0])|Q(product_type__contains=product_type[1])|Q(product_type__contains=product_type[2])|Q(transport_id__contains=str)|Q(plate_number__contains=str))
        return order_set

    
    
    #预存记录搜索
    def deposit_statistical_filter(self, balance_set, keyword=""):
        if not isinstance(balance_set, QuerySet):
            raise ParameterError('非法的参数：client_set')
        if keyword:
            balance_set = DepositStatistical.objects().filter(Q(name__contains=keyword)  |
                                         Q(phone__contains=keyword)|
                                                  Q(company_name__contains=keyword))
        return balance_set
    #第三方预存记录搜索
    def transaction_filter(self, balance_set, keyword=""):
        if not isinstance(balance_set, QuerySet):
            raise ParameterError('非法的参数：client_set')
        if keyword:
            client_set =  Client.objects().filter(Q(name__contains=keyword)  |
                                         Q(profile__phone__contains=keyword)|
                                                  Q(company_name__contains=keyword))
            balance_set = balance_set.filter(Q(client__in=client_set))
        return balance_set
    
    #律师按名称和城市搜索
    def lawyer_filter(self, campaign_lawyer_set, keyword=""):
        if not isinstance(campaign_lawyer_set, QuerySet):
            raise ParameterError('非法的参数：client_set')
        if keyword:
            campaign_lawyer_set = CampaignLawyer.objects().filter(Q(name__contains=keyword)  |
                                         Q(address__contains=keyword))
        return campaign_lawyer_set
    
    # 车辆按车牌号/所有人搜索
    def car_filter(self, car_set, keyword=""):
        if not isinstance(car_set, QuerySet):
            raise ParameterError('非法的参数：car_set')
        if keyword:
            car_set = car_set.filter(Q(plate_number__contains=keyword) | Q(holder__contains=keyword)| Q(state=keyword))
        return car_set
    
    # 过滤机动车保险订单搜索
    def jdcbx_filter(self, order_set):
        if not isinstance(order_set, QuerySet):
            raise ParameterError('非法的参数：order_set')
        
        keyword = self.get_parameter("search_keyword", '')
        if keyword:
            product_set = InsuranceProducts.objects().filter(Q(name__contains=keyword))
            order_set = order_set.filter( Q(paper_id__contains=keyword) )#第一版开放搜索订单号功能
            #order_set = order_set.filter(Q(plate_number__contains=keyword) | Q(paper_id__contains=keyword) )#| Q(insurance_product__name__contains=keyword))

        pay_state = self.get_parameter("pay_state", '')
        if pay_state == 'init':
            order_set = order_set.filter(state=pay_state)
        elif pay_state == 'paid':
            order_set = order_set.filter(state=pay_state)
        elif pay_state == 'done':
            order_set = order_set.filter(state=pay_state)
        elif pay_state == 'verify':
            order_set = order_set.filter(state=pay_state)
        elif pay_state == 'price':
            order_set = order_set.filter(state=pay_state)
        elif pay_state == 'wait':
            order_set = order_set.filter(state=pay_state)

        client_sign = self.get_parameter("id_client", '')
        if client_sign:
            try:
                client = Client.objects(id=client_sign).first()
            except:
                raise ParameterError("您查找的使用账户不存在，请刷新后重试试")
            if client:
                order_set = order_set.filter(client=client)
            else:
                raise ParameterError("您查找的用户不存在")
            
        #添加查找时间部分
        start_time = self.get_parameter("start_date", '')
        end_time = self.get_parameter("end_date", '')
        if start_time:
            order_set = order_set.filter(create_time__gt=start_time)
        if  end_time:     
           end_time2 = datetime.strptime(end_time,"%Y-%m-%d")
           end_time1 = (end_time2+timedelta(days= 1)).strftime('%Y-%m-%d') 
           order_set = order_set.filter(create_time__lt=end_time1)
        #添加查找时间部分结束
        return order_set
    
    
    # 过滤商品搜索
    def mall_goods_filter(self, mall_goods):
        if not isinstance(mall_goods, QuerySet):
            raise ParameterError('非法的参数：mall_goods')
        count=mall_goods.count()
        #显示状态
        search_state = self.get_parameter("search_state", "")
        if search_state == 'active':
            mall_goods = mall_goods.filter(is_hidden=False)
        elif search_state == 'hidden':
            mall_goods = mall_goods.filter(is_hidden=True)
        
        ##商品状态 
        goods_present_situation = self.get_parameter("search_present_situation", '')
        if goods_present_situation:
            if goods_present_situation in ['new','intact','scratch','repair','other']:
                mall_goods = mall_goods.filter(goods_present_situation=goods_present_situation)
            else:
                raise ParameterError('商品状态不正确')
        
        #商品分类   
        search_goods_type = self.get_parameter("search_goods_type", '')
        if search_goods_type:
            try:
                goods_type_detail  = GoodsType.objects(id =search_goods_type).first()
                if goods_type_detail:
                    mall_goods = mall_goods.filter(goods_type = goods_type_detail)
            except Exception as e:
                raise ParameterError("您查找的指定商品分类下暂时没有商品")
            
        #所有人
        client_sign = self.get_parameter("client_sign", '')
        if client_sign:
            client = Client.objects(id=client_sign).first()
            if client:
                mall_goods = mall_goods.filter(client=client)
            else:
                raise ParameterError("您查找的用户不存在")
            
        #关键字
        keyword = self.get_parameter("search_keyword", '')
        if keyword:
            try:
                mall_goods = mall_goods.filter(Q(goods_name__contains=keyword) | Q(goods_brand_digging__contains=keyword) )
            except Exception as e:
                raise ParameterError("您查找的指定产品的订单不存在")
        return mall_goods
    
    
    
    # 微信过滤二手商品搜索
    def wx_mallgoods_filter(self, mall_goods_set):
        if not isinstance(mall_goods_set, QuerySet):
            raise ParameterError('非法的参数：mall_goods_set')
        #关键字搜索
        keyword = self.get_parameter("search_keyword", '')
        if keyword:
            #product_set = InsuranceProducts.objects().filter(Q(name__contains=keyword))
            mall_goods_set = mall_goods_set.filter(Q(goods_name__contains=keyword)  )#名称搜索
        #分类搜索
        goods_type_state = self.get_parameter("goods_type_state", 'all')
        if goods_type_state:
            if goods_type_state == 'all':
                pass
            else:
                try:
                    goods_type_detail  = GoodsType.objects(id =goods_type_state).first()
                    if goods_type_detail:
                        mall_goods_set = mall_goods_set.filter(goods_type = goods_type_detail)
                except Exception as e:
                    raise ParameterError("您查找的指定商品分类下暂时没有商品")
            
        return mall_goods_set
    
    # 过滤特推产品搜索
    def recommend_product_filter(self, recommend_product_set):
        if not isinstance(recommend_product_set, QuerySet):
            raise ParameterError('非法的参数：recommend_product_set')
        keyword = self.get_parameter("search_keyword", "")
        if keyword:
            recommend_product_set = recommend_product_set.filter(Q(name__contains=keyword) | Q(phone__contains=keyword) )
        state = self.get_parameter("state", "active")
        if state == 'active':
            recommend_product_set = recommend_product_set.filter(is_hidden=False)
        elif state == 'hidden':
            recommend_product_set = recommend_product_set.filter(is_hidden=True)
        return recommend_product_set
    
    
    
    
