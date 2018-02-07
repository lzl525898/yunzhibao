__author__ = 'mlzx'
try:
    from common.models import SiteSettings
except ImportError:
    from common.models import BaseSettings as SiteSettings
from common.models import DException
import hashlib
from django.conf import settings
import traceback
from uuid import uuid1
import os
from datetime import datetime
from common.interface_helper import FileTypeError, FileSizeError, ImageSizeError, ImageTypeError
from enum import Enum


#获取分页信息，参数说明：page_count分页导航条中的最多可以显示页面数量, list_count列表中可显示的最多条数,
#  page_index当前页面编号, item_count总共元素数量
class BasePageTools():
    site_settings = SiteSettings.get_settings()

    def get_paging(self, page_count, page_index, item_count, list_count=-1):
        if isinstance(list_count, int):
            if list_count > self.site_settings.max_list_count:
                list_count = self.site_settings.max_list_count
        else:
            list_count = int(list_count)
        if list_count <= 0:
            list_count = self.site_settings.default_list_count
        total_pages_count = int(item_count/list_count)  # 可以产生的最多页面数量
        #判断是否有不满一页的内容，如果有，则增加一个页面
        if item_count % list_count != 0:
            total_pages_count += 1

        #修正page_index
        if page_index > total_pages_count:
            page_index = total_pages_count
        if page_index < 1:
            page_index = 1

        #产生分页数据
        if total_pages_count > page_count:
            #分页数多余可以显示的默认值
            page_start = page_index
            page_end = page_index + page_count
            if page_end > total_pages_count:
                page_start = total_pages_count - page_count + 1
                page_end = total_pages_count + 1
            pages = [x for x in range(page_start, page_end)]
        else:
            #分页数少余可以显示的默认值
            pages = [x+1 for x in range(total_pages_count)]

        #设置上一页
        if page_index > 1:
            prev_page = page_index - 1
        else:
            prev_page = 1

        #设置下一页
        if page_index < total_pages_count:
            next_page = page_index + 1
        else:
            next_page = total_pages_count

        start_item = (page_index-1)*list_count
        end_item = page_index*list_count

        return {'total_pages_count': total_pages_count,
                'pages': pages,
                'prev_page': prev_page,
                'next_page': next_page,
                'start_item': start_item,
                'end_item': end_item,
                'page_index': page_index,
                'item_count': item_count}


# 进行数据转换的工具类
class BaseConvertTools(object):

    @staticmethod
    def is_boolean(value):
        if isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return value == 1
        elif isinstance(value, str):
            return value in ['1', 'True', 'true', 'on', 'TRUE']
        else:
            value = str(value)
            return value in ['1', 'True', 'true', 'on', 'TRUE']

    @staticmethod
    def get_sha1_string(password):
        if not isinstance(password, str):
            raise Exception('unknown type of password:{0}'.format(type(password)))
        return hashlib.sha1(password.encode('utf-8')).hexdigest()

    @staticmethod
    def show_value(value):
        if isinstance(value, bool):
            if value:
                return '是'
            else:
                return '否'
        else:
            return value

    @staticmethod
    def validation_email(email):
        if email is not None:
            try:
                email_name, domain_part = email.strip().split('@', 1)
            except ValueError:
                pass
            else:
                email = '@'.join([email_name, domain_part.lower()])
        return email

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


class BaseRequestTools(object):
    request = None

    def __init__(self, request):
        self.request = request

    # 从request中获取参数
    def get_parameter(self, key, default_key=''):
        if self.request.method == "POST":
            return self.request.POST.get(key, default_key).strip()
        else:
            return self.request.GET.get(key, default_key).strip()

    # 从META中获取用户IP
    def get_ip(self):
        if "HTTP_X_FORWARDED_FOR" in self.request.META:
            ip = self.request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = self.request.META['REMOTE_ADDR']
        return ip

    # 检查session中的message信息
    def check_message(self, data):
        print("session里面的message"+self.request.session.get('message', ''))
        message = self.request.session.get('message', '')
        data['message'] = message
        print("data里面的message"+data['message'])
        self.request.session['message'] = ''

    # 检查session中的message信息
    def set_message(self, message):
        self.request.session['message'] = message


class EnumType(Enum):

    @classmethod
    def valid(cls, value):
        if value in cls._member_names_:
            return True
        elif value in cls._value2member_map_:
            return True
        else:
            return False


class ContentType(EnumType):
    gif = 'image/gif'
    png = 'image/png'
    jpeg = 'image/jpeg'
    jpg = 'image/jpg'


class FolderType(EnumType):
    user = 'pic/user'
    doc = 'file/document'


# 文件保存工具类
class FileTools(object):
    site_settings = SiteSettings.get_settings()
    content_type = ContentType
    folder_type = FolderType

    #判断图片是否符合要求
    def valid(self, request_file, size=-1):
        content = request_file.content_type
        if ".xlsx" == str(request_file.name)[-5:]:
            content='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif ".xls" == str(request_file.name)[-4:]:
            content= 'application/vnd.ms-excel'
        else:
            content = request_file.content_type
        self.valid_content(content=content)
        file_size = request_file.size
        self.valid_size(size=size, file_size=file_size)

    def valid_content(self, content):
        if self.content_type.valid(value=content):
            return self.content_type(content).name
        else:
            raise FileTypeError("暂不支持{0}格式文件，请上传如下格式文件：{1}".format(content, self.content_type._member_names_))

    def valid_size(self, size, file_size):
        if size <= 0:
            if hasattr(self.site_settings, 'file_max_size'):
                size = self.site_settings.file_max_size
            else:
                size = -1
        if size > 0:
            max_size = size*1024
            if file_size > max_size:
                raise FileSizeError("文件尺寸过大，请上传小于{0}K的文件".format(max_size/1024))

    def save(self, request_file, file_folder, old_file=''):
        self.valid(request_file=request_file, size=-1)
        if not self.folder_type.valid(file_folder) and not isinstance(file_folder, self.folder_type):
            raise FileTypeError('非法的文件类型')
        # 文件要保存到那个目录
        file_folder = self.folder_type(file_folder)
        # 文件的类型：标识着文件的扩展名
        #测试部分
        test11=request_file.content_type
        if ".xlsx" == str(request_file.name)[-5:]:
            file_type_content='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif ".xls" == str(request_file.name)[-4:]:
            file_type_content= 'application/vnd.ms-excel'
#         elif request_file.content_type == 'video/quicktime':
#             file_type_content= 'video/mp4'
        else:
            file_type_content= request_file.content_type
        file_type = self.content_type(file_type_content)
        #测试结束
        #file_type = self.content_type(request_file.content_type)
        # 当前日期的字符串，按日期保存文件
        date_str = datetime.now().strftime("%Y%m%d")
        # 随机生成文件名
        file_name = str(uuid1()) + '.' + str(file_type.name)
        # 基本目录,若基本目录不存在则需要创建基本目录
        base_dir = "{0}/static/{1}".format(settings.BASE_DIR, file_folder.value)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        # 存放文件的目录，若目录不存在则需要创建目录
        file_dir = "{0}/static/{1}/{2}".format(settings.BASE_DIR, file_folder.value, date_str)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        # 文件的相对路径，数据库中存放的路径
        file_res_path = "{0}/{1}/{2}".format(file_folder.value, date_str, file_name)
        # 文件的绝对路径，文件系统中文件的路径
        file_abs_path = "{0}/static/{1}".format(settings.BASE_DIR, file_res_path)
        # 开始保存文件
        image_file = open(file_abs_path, 'wb')
        for chunk in request_file.chunks():
            image_file.write(chunk)
        image_file.close()
        # 保存文件结束
        # 删除原文件
        if old_file != '':
            self.delete(old_file)
        return file_res_path

    @staticmethod
    def delete(file_res_path):
        file_abs_path = "{0}/static/{1}".format(settings.BASE_DIR, file_res_path)
        try:
            if os.path.exists(file_abs_path):
                os.remove(file_abs_path)
        except Exception as e:
            exception = DException(exception=str(e), traceback=traceback.format_exc()).save()


class ImageContentType(EnumType):
    gif = 'image/gif'
    png = 'image/png'
    jpeg = 'image/jpeg'
    jpg = 'image/jpg'
    ico = 'image/x-icon'


class ImageFolderType(EnumType):
    user = 'pic/user'
    batch = 'pic/batch'
    logistics = 'pic/logistics'
    lawyer = 'pic/lawyer'
    insurance = 'pic/insurance'
    driver = 'pic/driver'
    car = 'pic/car'
    proeditor = 'pic/proeditor'
    wx_share = 'pic/share'
    jdclbx = 'pic/jdclbx'
    mall = 'pic/mall'
    product = 'pic/product'


# 进行图片处理的工具类
class ImageTools(FileTools):
    content_type = ImageContentType
    folder_type = ImageFolderType


class DocumentContentType(EnumType):
    docx = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    doc = 'application/msword'
    xml = 'text/xml'
    xlsx = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    xls = 'application/vnd.ms-excel'
    pdf = 'application/pdf'


class DocumentFolderType(EnumType):
    document = 'document/insurance'
    batch = 'batch/list'
    jdclbx = 'jdclbx/document'
    order ='order/document'


# 进行图片处理的工具类
class DocumentTools(FileTools):
    content_type = DocumentContentType
    folder_type = DocumentFolderType
    
###############添加视频文件###################### 
class VideoContentType(EnumType):
    mp4='video/mp4'
    mpeg = 'video/mpeg'
    avi ='video/x-msvideo'
    mov= 'video/quicktime'
    movie='video/x-sgi-movie'


class VideoFolderType(EnumType):
    video = 'video/mall'


# 进行图片处理的工具类
class VideoTools(FileTools):
    content_type = VideoContentType
    folder_type = VideoFolderType  